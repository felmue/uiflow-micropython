# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

# Create an INTERFACE library for our C module.
add_library(module_esp_hosted_utils INTERFACE)

# Add our source files to the lib
target_sources(module_esp_hosted_utils INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/mod_esp_hosted_utils.c
)

# Add the current directory as an include directory.
target_include_directories(module_esp_hosted_utils INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/../../managed_components/espressif__esp_hosted/host
    ${CMAKE_CURRENT_LIST_DIR}/../../managed_components/espressif__esp_hosted/host/api/include
)

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE module_esp_hosted_utils)

