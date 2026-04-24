set(IDF_TARGET esp32s3)

set(BOARD_ID 2)

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    boards/sdkconfig.ble
    boards/sdkconfig.240mhz
    boards/sdkconfig.flash_16mb
    boards/sdkconfig.flash_qio
    boards/sdkconfig.freertos
    boards/sdkconfig.spiram
    boards/sdkconfig.spiram_oct
    boards/ESPRESSIF_ESP32_S3_BOX_3/sdkconfig.s3box3
)

# Enable unified module
set(M5_UNIFIED_MODULE_ENABLE TRUE)
set(ADF_MODULE_ENABLE TRUE CACHE INTERNAL "ADF Enable")

set(ADF_COMPS     "$ENV{ADF_PATH}/components")

set(ADF_BOARD_INIT_SRC
    $ENV{ADF_PATH}/components
    ESPRESSIF_ESP32_S3_BOX_3/board_init.c
)

list(APPEND EXTRA_COMPONENT_DIRS
    $ENV{ADF_PATH}/components/audio_pipeline
    $ENV{ADF_PATH}/components/audio_sal
    $ENV{ADF_PATH}/components/esp-adf-libs
    $ENV{ADF_PATH}/components/esp-sr
    ${CMAKE_SOURCE_DIR}/boards
    # esp_codec_dev
)

message(STATUS "ADF_MODULE_ENABLE=${ADF_MODULE_ENABLE}")
message(STATUS "ESPRESSIF_ESP32_S3_BOX_3/CMakeLists.txt: EXTRA_COMPONENT_DIRS=${EXTRA_COMPONENT_DIRS}")
