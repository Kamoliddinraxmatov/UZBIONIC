cmake_minimum_required(VERSION 3.16)
project(uzbionic_firmware C)

set(CMAKE_C_STANDARD 11)
add_compile_options(-Wall -Wextra -Werror)

add_library(uzb_core src/uzb_dsp.c src/uzb_control.c src/uzb_modes.c)
target_include_directories(uzb_core PUBLIC include)
target_link_libraries(uzb_core PUBLIC m)

add_executable(host_run tests/host_run.c)
target_link_libraries(host_run uzb_core)

add_executable(test_control tests/test_control.c)
target_link_libraries(test_control uzb_core)

add_executable(test_modes tests/test_modes.c)
target_link_libraries(test_modes uzb_core)

enable_testing()
add_test(NAME test_control COMMAND test_control)
add_test(NAME test_modes COMMAND test_modes)
