/*
 * SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */

#include <string.h>
#include <stdbool.h>
#include "py/nlr.h"
#include "py/obj.h"
#include "py/objtuple.h"
#include "py/runtime.h"
#include "py/mphal.h"
#include "py/stream.h"
#include "extmod/vfs_fat.h"
#include "_vfs_stream.h"

#include "esp_log.h"
#include "esp_hosted.h"
#include "esp_hosted_ota.h"
#include "esp_hosted_api_types.h"
#include "esp_app_format.h"
#include "esp_app_desc.h"
#include <string.h>

static const char *TAG = "esp_hosted_utils";

#define DEBUG 0
#if DEBUG
#define DEBUG_printf(...) ESP_LOGI(TAG, __VA_ARGS__)
#else
#define DEBUG_printf(...) (void)0
#endif

static mp_obj_t connect(void) {
    esp_err_t ret = esp_hosted_connect_to_slave();
    if (ret != ESP_OK) {
        mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("Failed to connect to slave: %s"), esp_err_to_name(ret));
    }

    return mp_obj_new_bool(ret == ESP_OK);
}
static MP_DEFINE_CONST_FUN_OBJ_0(connect_obj, connect);

static mp_obj_t get_host_firmware_version(void) {
    char version_str[32] = { 0 };
    snprintf(version_str, sizeof(version_str), "%d.%d.%d",
        ESP_HOSTED_VERSION_MAJOR_1, ESP_HOSTED_VERSION_MINOR_1, ESP_HOSTED_VERSION_PATCH_1);

    return mp_obj_new_str(version_str, strlen(version_str));
}
static MP_DEFINE_CONST_FUN_OBJ_0(get_host_firmware_version_obj, get_host_firmware_version);

static mp_obj_t get_slave_firmware_version(void) {
    esp_hosted_coprocessor_fwver_t slave_version = {0};
    esp_err_t ret = esp_hosted_get_coprocessor_fwversion(&slave_version);
    if (ret != ESP_OK) {
        DEBUG_printf("Could not get slave firmware version (error: %s)", esp_err_to_name(ret));
        return mp_obj_new_str("", 0);
    }
    char version_str[32] = { 0 };
    snprintf(version_str, sizeof(version_str), "%ld.%ld.%ld",
        slave_version.major1, slave_version.minor1, slave_version.patch1);

    return mp_obj_new_str(version_str, strlen(version_str));
}
static MP_DEFINE_CONST_FUN_OBJ_0(get_slave_firmware_version_obj, get_slave_firmware_version);

/**
 * @brief Compare host and slave firmware versions
 *
 * Compares major.minor versions only (ignoring patch level)
 *
 * @return 0 if versions match
 *           -1 if host version > slave version (slave needs upgrade)
 *            1 if host version < slave version (host needs upgrade)
 */
static int compare_versions(uint32_t slave_version) {
    uint32_t host_version = ESP_HOSTED_VERSION_VAL(ESP_HOSTED_VERSION_MAJOR_1,
        ESP_HOSTED_VERSION_MINOR_1,
        ESP_HOSTED_VERSION_PATCH_1);

    // Compare major.minor only (ignore patch level)
    slave_version &= 0xFFFFFF00;
    host_version &= 0xFFFFFF00;

    if (host_version == slave_version) {
        return 0;    // Versions match
    } else if (host_version > slave_version) {
        #ifndef CONFIG_ESP_HOSTED_FW_VERSION_MISMATCH_WARNING_SUPPRESS
        ESP_LOGW(TAG, "Version mismatch: Host [%u.%u.%u] > Co-proc [%u.%u.%u] ==> Upgrade co-proc to avoid RPC timeouts",
            ESP_HOSTED_VERSION_PRINTF_ARGS(host_version), ESP_HOSTED_VERSION_PRINTF_ARGS(slave_version));
        #endif
        return -1;    // Host newer, slave needs upgrade
    } else {
        #ifndef CONFIG_ESP_HOSTED_FW_VERSION_MISMATCH_WARNING_SUPPRESS
        ESP_LOGW(TAG, "Version mismatch: Host [%u.%u.%u] < Co-proc [%u.%u.%u] ==> Upgrade host to avoid compatibility issues",
            ESP_HOSTED_VERSION_PRINTF_ARGS(host_version), ESP_HOSTED_VERSION_PRINTF_ARGS(slave_version));
        #endif
        return 1;    // Slave newer, host needs upgrade
    }
}

// 0 if versions are compatible (OTA not needed)
// -1 if slave needs upgrade
// 1 if host needs upgrade
static mp_obj_t check_version_compatibility(void) {
    esp_hosted_coprocessor_fwver_t slave_version = {0};
    esp_err_t ret = esp_hosted_get_coprocessor_fwversion(&slave_version);

    if (ret != ESP_OK) {
        DEBUG_printf("Could not get slave firmware version (error: %s)", esp_err_to_name(ret));
        DEBUG_printf("Proceeding without version compatibility check");
        return MP_OBJ_NEW_SMALL_INT(-1);      // Assume upgrade needed
    }

    DEBUG_printf("Host firmware version: %" PRIu32 ".%" PRIu32 ".%" PRIu32,
        ESP_HOSTED_VERSION_MAJOR_1, ESP_HOSTED_VERSION_MINOR_1, ESP_HOSTED_VERSION_PATCH_1);
    DEBUG_printf("Slave firmware version: %" PRIu32 ".%" PRIu32 ".%" PRIu32,
        slave_version.major1, slave_version.minor1, slave_version.patch1);

    uint32_t slave_ver = ESP_HOSTED_VERSION_VAL(slave_version.major1,
        slave_version.minor1,
        slave_version.patch1);
    return MP_OBJ_NEW_SMALL_INT(compare_versions(slave_ver));
}
static MP_DEFINE_CONST_FUN_OBJ_0(check_version_compatibility_obj, check_version_compatibility);

/* Function to parse ESP32 image header and get firmware info from file */
static esp_err_t parse_image_header_from_file(const char *file_path, size_t *firmware_size, char *app_version_str, size_t version_str_len) {
    esp_image_header_t image_header;
    esp_image_segment_header_t segment_header;
    esp_app_desc_t app_desc;
    size_t offset = 0;
    size_t total_size = 0;

    void *file = vfs_stream_open(file_path, VFS_READ);
    if (file == NULL) {
        ESP_LOGE(TAG, "Failed to open firmware file for header verification: %s", file_path);
        return ESP_FAIL;
    }

    /* Read image header */
    if (vfs_stream_read(file, &image_header, sizeof(image_header)) != sizeof(image_header)) {
        ESP_LOGE(TAG, "Failed to read image header from file");
        vfs_stream_close(file);
        return ESP_FAIL;
    }

    /* Validate magic number */
    if (image_header.magic != ESP_IMAGE_HEADER_MAGIC) {
        ESP_LOGE(TAG, "Invalid image magic: 0x%" PRIx8 " (expected: 0x%" PRIx8 ")", image_header.magic, ESP_IMAGE_HEADER_MAGIC);
        ESP_LOGE(TAG, "This indicates the file is not a valid ESP32 firmware image!");
        ESP_LOGE(TAG, "Please ensure you have flashed the correct firmware binary to the LittleFS partition.");
        vfs_stream_close(file);
        return ESP_ERR_INVALID_ARG;
    }

    ESP_LOGI(TAG, "Image header: magic=0x%" PRIx8 ", segment_count=%" PRIu8 ", hash_appended=%" PRIu8,
        image_header.magic, image_header.segment_count, image_header.hash_appended);

    /* Calculate total size by reading all segments */
    offset = sizeof(image_header);
    total_size = sizeof(image_header);

    for (int i = 0; i < image_header.segment_count; i++) {
        /* Read segment header */
        if (vfs_stream_seek(file, offset, SEEK_SET) != offset ||
            vfs_stream_read(file, &segment_header, sizeof(segment_header)) != sizeof(segment_header)) {
            ESP_LOGE(TAG, "Failed to read segment %d header", i);
            vfs_stream_close(file);
            return ESP_FAIL;
        }

        ESP_LOGI(TAG, "Segment %d: data_len=%" PRIu32 ", load_addr=0x%" PRIx32, i, segment_header.data_len, segment_header.load_addr);

        /* Add segment header size + data size */
        total_size += sizeof(segment_header) + segment_header.data_len;
        offset += sizeof(segment_header) + segment_header.data_len;

        /* Read app description from the first segment */
        if (i == 0) {
            size_t app_desc_offset = sizeof(image_header) + sizeof(segment_header);
            if (vfs_stream_seek(file, app_desc_offset, SEEK_SET) == app_desc_offset &&
                vfs_stream_read(file, &app_desc, sizeof(app_desc)) == sizeof(app_desc)) {
                memcpy(app_version_str, app_desc.version, version_str_len - 1);
                // strncpy(app_version_str, app_desc.version, version_str_len - 1);
                app_version_str[version_str_len - 1] = '\0';
                ESP_LOGI(TAG, "Found app description: version='%s', project_name='%s'",
                    app_desc.version, app_desc.project_name);
            } else {
                ESP_LOGW(TAG, "Failed to read app description");
                strncpy(app_version_str, "unknown", version_str_len - 1);
                app_version_str[version_str_len - 1] = '\0';
            }
        }
    }

    /* Add padding to align to 16 bytes */
    size_t padding = (16 - (total_size % 16)) % 16;
    if (padding > 0) {
        ESP_LOGD(TAG, "Adding %u bytes of padding for alignment", (unsigned int)padding);
        total_size += padding;
    }

    /* Add the checksum byte (always present) */
    total_size += 1;
    ESP_LOGD(TAG, "Added 1 byte for checksum");

    /* Add SHA256 hash if appended */
    bool has_hash = (image_header.hash_appended == 1);
    if (has_hash) {
        total_size += 32;  // SHA256 hash is 32 bytes
        ESP_LOGD(TAG, "Added 32 bytes for SHA256 hash (hash_appended=1)");
    } else {
        ESP_LOGD(TAG, "No SHA256 hash appended (hash_appended=0)");
    }

    *firmware_size = total_size;
    ESP_LOGI(TAG, "Total image size: %u bytes", (unsigned int)*firmware_size);

    vfs_stream_close(file);
    return ESP_OK;
}

static mp_obj_t ota_perform(mp_obj_t firmware_path_obj) {
    if (!mp_obj_is_str(firmware_path_obj)) {
        mp_raise_TypeError(MP_ERROR_TEXT("Firmware path must be a string"));
    }
    const char *firmware_path = mp_obj_str_get_str(firmware_path_obj);
    #ifndef CHUNK_SIZE
    #define CHUNK_SIZE 1500
    #endif
    uint8_t chunk[CHUNK_SIZE] = {0};

    /* Verify image header and get firmware info */
    size_t firmware_size;
    char new_app_version[32];
    esp_err_t ret = parse_image_header_from_file(firmware_path, &firmware_size, new_app_version, sizeof(new_app_version));
    if (ret != ESP_OK) {
        mp_raise_ValueError(MP_ERROR_TEXT("Invalid firmware image"));
    }

    #ifdef CONFIG_OTA_VERSION_CHECK_SLAVEFW_SLAVE
    /* Get current running slave firmware version */
    esp_hosted_coprocessor_fwver_t current_slave_version = {0};
    esp_err_t version_ret = esp_hosted_get_coprocessor_fwversion(&current_slave_version);

    if (version_ret == ESP_OK) {
        char current_version_str[32];
        snprintf(current_version_str, sizeof(current_version_str), "%" PRIu32 ".%" PRIu32 ".%" PRIu32,
            current_slave_version.major1, current_slave_version.minor1, current_slave_version.patch1);

        ESP_LOGI(TAG, "Current slave firmware version: %s", current_version_str);
        ESP_LOGI(TAG, "New slave firmware version: %s", new_app_version);

        if (strcmp(new_app_version, current_version_str) == 0) {
            ESP_LOGW(TAG, "Current slave firmware version (%s) is the same as new version (%s). Skipping OTA.",
                current_version_str, new_app_version);
            mp_raise_ValueError(MP_ERROR_TEXT("Firmware version is the same as current version, OTA not required"));
        }

        ESP_LOGI(TAG, "Version differs - proceeding with OTA from %s to %s", current_version_str, new_app_version);
    } else {
        ESP_LOGW(TAG, "Could not get current slave firmware version (error: %s), proceeding with OTA",
            esp_err_to_name(version_ret));
    }
    #else
    ESP_LOGI(TAG, "Version check disabled - proceeding with OTA (new firmware version: %s)", new_app_version);
    #endif

    /* Open firmware file */
    void *firmware_file = vfs_stream_open(firmware_path, VFS_READ);
    if (firmware_file == NULL) {
        ESP_LOGE(TAG, "Failed to open firmware file: %s", firmware_path);
        mp_raise_ValueError(MP_ERROR_TEXT("Invalid firmware image"));
    }

    ESP_LOGI(TAG, "Starting OTA from LittleFS: %s", firmware_path);

    /* Begin OTA */
    ret = esp_hosted_slave_ota_begin();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to begin OTA: %s", esp_err_to_name(ret));
        vfs_stream_close(firmware_file);
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to begin OTA"));
    }

    /* Write firmware in chunks */
    size_t bytes_read;
    while ((bytes_read = vfs_stream_read(firmware_file, chunk, CHUNK_SIZE)) > 0) {
        ret = esp_hosted_slave_ota_write(chunk, bytes_read);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to write OTA chunk: %s", esp_err_to_name(ret));
            vfs_stream_close(firmware_file);
            mp_raise_ValueError(MP_ERROR_TEXT("Failed to write OTA chunk"));
        }
    }
    vfs_stream_close(firmware_file);

    /* End OTA */
    ret = esp_hosted_slave_ota_end();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to end OTA: %s", esp_err_to_name(ret));
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to complete OTA"));
    }

    ESP_LOGI(TAG, "LittleFS OTA completed successfully");

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(ota_perform_obj, ota_perform);

static const mp_rom_map_elem_t esp_hosted_utils_globals_table[] = {
    /* *FORMAT-OFF* */
    { MP_ROM_QSTR(MP_QSTR___name__),                    MP_ROM_QSTR(MP_QSTR_esp_hosted_utils)        },
    { MP_ROM_QSTR(MP_QSTR_connect),                     MP_ROM_PTR(&connect_obj)                     },
    { MP_ROM_QSTR(MP_QSTR_get_host_firmware_version),   MP_ROM_PTR(&get_host_firmware_version_obj)   },
    { MP_ROM_QSTR(MP_QSTR_get_slave_firmware_version),  MP_ROM_PTR(&get_slave_firmware_version_obj)  },
    { MP_ROM_QSTR(MP_QSTR_check_version_compatibility), MP_ROM_PTR(&check_version_compatibility_obj) },
    { MP_ROM_QSTR(MP_QSTR_ota_perform),                 MP_ROM_PTR(&ota_perform_obj)                 },
    /* *FORMAT-ON* */
};
static MP_DEFINE_CONST_DICT(esp_hosted_utils_globals, esp_hosted_utils_globals_table);

const mp_obj_module_t module_esp_hosted_utils = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *)&esp_hosted_utils_globals,
};

MP_REGISTER_MODULE(MP_QSTR_esp_hosted_utils, module_esp_hosted_utils);
