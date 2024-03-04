/*
 * SPDX-FileCopyrightText: 2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Unlicense OR CC0-1.0
 */

    .section    .data1,"aw"
    .global     __rv_core_test_stack_frame
    .type       __rv_core_test_stack_frame,@object
    .align      4
__rv_core_test_stack_frame:
    .space      1024, 0
__rv_core_test_stack_frame_end:


    .extern     _rv_core_critical_regs_restore
    .extern     rv_core_test_c_handler

    .section    .iram1,"ax"
    .global     __rv_core_critical_regs_restore
    .type       __rv_core_critical_regs_restore,@function
    .align      4

__rv_core_critical_regs_restore:

    la      sp, __rv_core_test_stack_frame_end
    call    rv_core_test_c_handler

    tail    _rv_core_critical_regs_restore

    .size   __rv_core_critical_regs_restore, . - __rv_core_critical_regs_restore
