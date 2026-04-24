/*
 * SPDX-FileCopyrightText: 2025 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */

#include <string.h>
#include <stdbool.h>
#include "py/obj.h"
#include "py/objstr.h"
#include "py/objtype.h"
#include "py/runtime.h"
#include "py/mphal.h"

#include "driver/rmt_rx.h"
#include "driver/rmt_tx.h"
#include "driver/rmt_encoder.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

typedef rmt_symbol_word_t rmt_item32_t;

// 自定义协议参数
#define SYNC_HIGH_US 9000
#define SYNC_LOW_US  4500

#define BIT_HIGH_US 500
#define BIT0_LOW_US 500
#define BIT1_LOW_US 1500

#define FRAME_HEADER 0xAA
#define FRAME_TAIL   0xA0

#define RX_MAX_LEN 64
#define RX_SYMBOL_BUF_NUM 640

static rmt_channel_handle_t tx_channel = NULL;
static rmt_encoder_handle_t tx_encoder = NULL;
static bool tx_is_initialized = false;
static int tx_init_pin = -1;

static rmt_channel_handle_t rx_channel = NULL;
static bool rx_is_initialized = false;
static bool rx_receiving = false;
static int rx_init_pin = -1;
static TaskHandle_t rx_task_handle = NULL;
static QueueHandle_t rx_done_queue = NULL;
static rmt_symbol_word_t *rx_symbols = NULL;

static mp_obj_t rx_callback = mp_const_none;
static uint8_t rx_buffer[256];
static size_t rx_len = 0;

static const rmt_receive_config_t rx_config = {
    .signal_range_min_ns = 100 * 1000,
    .signal_range_max_ns = 3 * 1000 * 1000,
};

// =================================================================================================
// class: rf433.Tx
typedef struct _tx_obj_t {
    mp_obj_base_t base;
    int out;
} tx_obj_t;

extern const mp_obj_type_t mp_tx_type;

static rmt_item32_t encode_bit(bool bit) {
    rmt_item32_t item;
    item.level0 = 1;
    item.duration0 = BIT_HIGH_US;
    item.level1 = 0;
    item.duration1 = bit ? BIT1_LOW_US : BIT0_LOW_US;
    return item;
}

static void encode_byte(rmt_item32_t *items, int *index, uint8_t byte) {
    for (int bit_idx = 7; bit_idx >= 0; bit_idx--) {
        items[(*index)++] = encode_bit((byte >> bit_idx) & 1);
    }
}

static esp_err_t tx_init_if_needed(int pin) {
    if (tx_is_initialized) {
        if (pin == tx_init_pin) {
            return ESP_OK;
        }
        if (tx_channel) {
            rmt_disable(tx_channel);
            rmt_del_channel(tx_channel);
            tx_channel = NULL;
        }
        if (tx_encoder) {
            rmt_del_encoder(tx_encoder);
            tx_encoder = NULL;
        }
        tx_is_initialized = false;
    }

    rmt_tx_channel_config_t tx_chan_cfg = {
        .gpio_num = pin,
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 1000000,
        .mem_block_symbols = 64,
        .trans_queue_depth = 4,
    };

    esp_err_t err = rmt_new_tx_channel(&tx_chan_cfg, &tx_channel);
    if (err != ESP_OK) {
        return err;
    }

    rmt_copy_encoder_config_t copy_cfg = {};
    err = rmt_new_copy_encoder(&copy_cfg, &tx_encoder);
    if (err != ESP_OK) {
        rmt_del_channel(tx_channel);
        tx_channel = NULL;
        return err;
    }

    err = rmt_enable(tx_channel);
    if (err != ESP_OK) {
        rmt_del_encoder(tx_encoder);
        rmt_del_channel(tx_channel);
        tx_encoder = NULL;
        tx_channel = NULL;
        return err;
    }

    tx_is_initialized = true;
    tx_init_pin = pin;
    return ESP_OK;
}

static void send_data(const uint8_t *payload, size_t len) {
    size_t item_max_count = 1 + (2 + len + 1) * 8;
    rmt_item32_t items[item_max_count];
    int item_idx = 0;

    items[item_idx++] = (rmt_item32_t) {.duration0 = SYNC_HIGH_US, .level0 = 1, .duration1 = SYNC_LOW_US, .level1 = 0};
    encode_byte(items, &item_idx, FRAME_HEADER);
    encode_byte(items, &item_idx, (uint8_t)len);
    for (size_t i = 0; i < len; i++) {
        encode_byte(items, &item_idx, payload[i]);
    }
    encode_byte(items, &item_idx, FRAME_TAIL);

    rmt_transmit_config_t tx_cfg = {
        .loop_count = 0,
    };
    rmt_transmit(tx_channel, tx_encoder, items, item_idx * sizeof(rmt_item32_t), &tx_cfg);
    rmt_tx_wait_all_done(tx_channel, -1);
}

static mp_obj_t tx_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    tx_obj_t *self = mp_obj_malloc_with_finaliser(tx_obj_t, &mp_tx_type);

    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_out_pin, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
    };
    mp_arg_val_t args_vals[MP_ARRAY_SIZE(allowed_args)];
    mp_map_t kw_args;
    mp_map_init_fixed_table(&kw_args, n_kw, args + n_args);
    mp_arg_parse_all(n_args, args + 1, &kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args_vals);

    self->out = mp_obj_get_int(args_vals[0].u_obj);
    esp_err_t err = tx_init_if_needed(self->out);
    if (err != ESP_OK) {
        mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("TX init failed: %d"), err);
    }

    return MP_OBJ_FROM_PTR(self);
}

static mp_obj_t tx_send(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    const mp_arg_t allowed_args[] = {
        { MP_QSTR_data, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = mp_const_none} },
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args - 1, pos_args + 1, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    mp_buffer_info_t data_buff;
    mp_get_buffer_raise(args[0].u_obj, &data_buff, MP_BUFFER_READ);
    send_data((const uint8_t *)data_buff.buf, data_buff.len);

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_KW(tx_send_obj, 1, tx_send);

static const mp_rom_map_elem_t tx_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_send), MP_ROM_PTR(&tx_send_obj) },
};
MP_DEFINE_CONST_DICT(tx_locals_dict, tx_locals_dict_table);

MP_DEFINE_CONST_OBJ_TYPE(
    mp_tx_type,
    MP_QSTR_Tx,
    MP_TYPE_FLAG_NONE,
    make_new, tx_make_new,
    locals_dict, &tx_locals_dict
    );

// =================================================================================================
// class: rf433.Rx
typedef struct _rx_obj_t {
    mp_obj_base_t base;
    int in;
} rx_obj_t;

extern const mp_obj_type_t mp_rx_type;

static bool decode_bit(rmt_item32_t item) {
    int high_us = item.duration0;
    int low_us = item.duration1;
    return high_us > 350 && high_us < 650 && low_us > 1350 && low_us < 1650;
}

static void decode_data(rmt_item32_t *items, size_t num_items) {
    uint8_t byte = 0;
    int bit_count = 0;
    int rx_state = 0;
    size_t data_len = 0;
    size_t buf_index = 0;

    for (size_t i = 0; i < num_items; i++) {
        bool bit = decode_bit(items[i]);
        byte = (byte << 1) | bit;
        bit_count++;

        if (bit_count == 8) {
            if (rx_state == 0) {
                if (byte == FRAME_HEADER) {
                    rx_state = 1;
                }
            } else if (rx_state == 1) {
                data_len = byte;
                if (data_len == 0 || data_len > RX_MAX_LEN) {
                    rx_state = 0;
                } else {
                    rx_state = 2;
                }
            } else if (rx_state == 2) {
                if (buf_index < RX_MAX_LEN + 1) {
                    rx_buffer[buf_index++] = byte;
                }
                if (buf_index >= data_len + 1) {
                    break;
                }
            }
            bit_count = 0;
            byte = 0;
        }
    }

    if (buf_index == data_len + 1 && rx_buffer[data_len] == FRAME_TAIL) {
        rx_len = data_len;
        if (rx_callback != mp_const_none && rx_len > 0) {
            (void)mp_sched_schedule(rx_callback, mp_const_none);
        }
    }
}

static bool rx_done_cb(rmt_channel_handle_t channel, const rmt_rx_done_event_data_t *edata, void *user_data) {
    BaseType_t high_task_wakeup = pdFALSE;
    (void)channel;
    (void)user_data;
    if (rx_done_queue != NULL) {
        size_t symbol_num = edata->num_symbols;
        xQueueOverwriteFromISR(rx_done_queue, &symbol_num, &high_task_wakeup);
    }
    return high_task_wakeup == pdTRUE;
}

static void app_rf433r_rx_decode(void *param) {
    (void)param;
    while (rx_is_initialized && rx_done_queue != NULL) {
        size_t symbol_num = 0;
        if (xQueueReceive(rx_done_queue, &symbol_num, portMAX_DELAY) == pdTRUE) {
            if (rx_symbols == NULL) {
                continue;
            }
            if (symbol_num > RX_SYMBOL_BUF_NUM) {
                symbol_num = RX_SYMBOL_BUF_NUM;
            }
            decode_data((rmt_item32_t *)rx_symbols, symbol_num);

            if (rx_receiving) {
                (void)rmt_receive(rx_channel, rx_symbols,
                    RX_SYMBOL_BUF_NUM * sizeof(rmt_symbol_word_t), &rx_config);
            }
        }
    }
    rx_task_handle = NULL;
    vTaskDelete(NULL);
}

static esp_err_t rx_init_if_needed(int pin) {
    if (rx_is_initialized) {
        if (pin == rx_init_pin) {
            return ESP_OK;
        }
        rx_is_initialized = false;
        rx_receiving = false;
        if (rx_task_handle) {
            vTaskDelete(rx_task_handle);
            rx_task_handle = NULL;
        }
        if (rx_done_queue) {
            vQueueDelete(rx_done_queue);
            rx_done_queue = NULL;
        }
        if (rx_channel) {
            rmt_disable(rx_channel);
            rmt_del_channel(rx_channel);
            rx_channel = NULL;
        }
        if (rx_symbols) {
            m_free(rx_symbols);
            rx_symbols = NULL;
        }
    }

    rmt_rx_channel_config_t rx_chan_cfg = {
        .gpio_num = pin,
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 1000000,
        .mem_block_symbols = 64,
    };

    esp_err_t err = rmt_new_rx_channel(&rx_chan_cfg, &rx_channel);
    if (err != ESP_OK) {
        return err;
    }

    rmt_rx_event_callbacks_t cbs = {
        .on_recv_done = rx_done_cb,
    };
    err = rmt_rx_register_event_callbacks(rx_channel, &cbs, NULL);
    if (err != ESP_OK) {
        rmt_del_channel(rx_channel);
        rx_channel = NULL;
        return err;
    }

    err = rmt_enable(rx_channel);
    if (err != ESP_OK) {
        rmt_del_channel(rx_channel);
        rx_channel = NULL;
        return err;
    }

    rx_symbols = m_malloc(RX_SYMBOL_BUF_NUM * sizeof(rmt_symbol_word_t));
    if (rx_symbols == NULL) {
        rmt_disable(rx_channel);
        rmt_del_channel(rx_channel);
        rx_channel = NULL;
        return ESP_ERR_NO_MEM;
    }

    rx_done_queue = xQueueCreate(1, sizeof(size_t));
    if (rx_done_queue == NULL) {
        m_free(rx_symbols);
        rx_symbols = NULL;
        rmt_disable(rx_channel);
        rmt_del_channel(rx_channel);
        rx_channel = NULL;
        return ESP_ERR_NO_MEM;
    }

    BaseType_t task_created = xTaskCreate(app_rf433r_rx_decode, "app_rf433r_rx_decode", 4096, NULL, 3, &rx_task_handle);
    if (task_created != pdPASS) {
        vQueueDelete(rx_done_queue);
        rx_done_queue = NULL;
        m_free(rx_symbols);
        rx_symbols = NULL;
        rmt_disable(rx_channel);
        rmt_del_channel(rx_channel);
        rx_channel = NULL;
        return ESP_ERR_NO_MEM;
    }

    rx_is_initialized = true;
    rx_init_pin = pin;
    rx_receiving = true;
    return rmt_receive(rx_channel, rx_symbols,
        RX_SYMBOL_BUF_NUM * sizeof(rmt_symbol_word_t), &rx_config);
}

static mp_obj_t rx_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    rx_obj_t *self = mp_obj_malloc_with_finaliser(rx_obj_t, &mp_rx_type);

    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_in_pin, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
    };
    mp_arg_val_t args_vals[MP_ARRAY_SIZE(allowed_args)];
    mp_map_t kw_args;
    mp_map_init_fixed_table(&kw_args, n_kw, args + n_args);
    mp_arg_parse_all(n_args, args + 1, &kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args_vals);

    self->in = mp_obj_get_int(args_vals[0].u_obj);
    esp_err_t err = rx_init_if_needed(self->in);
    if (err != ESP_OK) {
        mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("RX init failed: %d"), err);
    }

    return MP_OBJ_FROM_PTR(self);
}

static mp_obj_t rx_start_recv(mp_obj_t self_in) {
    (void)self_in;
    if (rx_is_initialized && !rx_receiving) {
        rx_receiving = true;
        (void)rmt_receive(rx_channel, rx_symbols,
            RX_SYMBOL_BUF_NUM * sizeof(rmt_symbol_word_t), &rx_config);
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(rx_start_recv_obj, rx_start_recv);

static mp_obj_t rx_stop_recv(mp_obj_t self_in) {
    (void)self_in;
    rx_receiving = false;
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(rx_stop_recv_obj, rx_stop_recv);

static mp_obj_t rx_set_recv_callback(mp_obj_t self_in, mp_obj_t callback) {
    (void)self_in;
    if (callback == mp_const_none || mp_obj_is_callable(callback)) {
        rx_callback = callback;
    } else {
        mp_raise_ValueError(MP_ERROR_TEXT("callback must be callable or None"));
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_2(rx_set_recv_callback_obj, rx_set_recv_callback);

static mp_obj_t rx_read(mp_obj_t self_in) {
    (void)self_in;
    if (rx_len == 0) {
        return mp_const_none;
    }
    mp_obj_t data = mp_obj_new_bytes(rx_buffer, rx_len);
    rx_len = 0;
    return data;
}
static MP_DEFINE_CONST_FUN_OBJ_1(rx_read_obj, rx_read);

static const mp_rom_map_elem_t rx_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_start_recv), MP_ROM_PTR(&rx_start_recv_obj) },
    { MP_ROM_QSTR(MP_QSTR_stop_recv), MP_ROM_PTR(&rx_stop_recv_obj) },
    { MP_ROM_QSTR(MP_QSTR_read), MP_ROM_PTR(&rx_read_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_recv_callback), MP_ROM_PTR(&rx_set_recv_callback_obj) },
};
MP_DEFINE_CONST_DICT(rx_locals_dict, rx_locals_dict_table);

MP_DEFINE_CONST_OBJ_TYPE(
    mp_rx_type,
    MP_QSTR_Rx,
    MP_TYPE_FLAG_NONE,
    make_new, rx_make_new,
    locals_dict, &rx_locals_dict
    );

static const mp_rom_map_elem_t rf433_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_rf433) },
    { MP_ROM_QSTR(MP_QSTR_Tx), MP_ROM_PTR(&mp_tx_type) },
    { MP_ROM_QSTR(MP_QSTR_Rx), MP_ROM_PTR(&mp_rx_type) },
};
static MP_DEFINE_CONST_DICT(rf433_globals, rf433_globals_table);

const mp_obj_module_t module_rf433 = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&rf433_globals,
};

MP_REGISTER_MODULE(MP_QSTR_rf433, module_rf433);
