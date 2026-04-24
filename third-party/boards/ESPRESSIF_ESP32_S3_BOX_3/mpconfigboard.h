#define MICROPY_HW_BOARD_NAME               "Espressif ESP32-S3-BOX-3"
#define MICROPY_HW_MCU_NAME                 "ESP32S3"

#define MICROPY_PY_MACHINE_DAC              (0)
#define MICROPY_PY_MACHINE_I2S              (1)

// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (0)

// #define MICROPY_HW_I2C0_SCL                 (9)
// #define MICROPY_HW_I2C0_SDA                 (8)

#define MICROPY_HW_USB_VID 0x303A
#define MICROPY_HW_USB_PID 0x7005
#define MICROPY_HW_USB_MANUFACTURER_STRING "Espressif"
#define MICROPY_HW_USB_PRODUCT_FS_STRING "ESP32-S3 Box(UiFlow2)"

#define AUDIO_RECORDER_DOWN_CH (1)

#define NO_HAVE_RTC_SYNC (1)
