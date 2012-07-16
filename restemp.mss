################
# Automatically generated by psgen, Polimi HPPS project 2012
# Author: Marco Zavatta (marco.zavatta@mail.polimi.it)
# Generated on 2012-07-16
# Generated from architecture_custom.xml
# Platform Specification Format version 2.1.0
# EDK version 12.1 Build EDK_MS1.53d
################

BEGIN DRIVER
 PARAMETER HW_INSTANCE = xps_mailbox_0
 PARAMETER DRIVER_NAME = mbox
 PARAMETER DRIVER_VER = 3.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = proc_sys_reset_0
 PARAMETER DRIVER_NAME = generic
 PARAMETER DRIVER_VER = 1.00.a
END

BEGIN PROCESSOR
 PARAMETER HW_INSTANCE = microblaze_1
 PARAMETER DRIVER_NAME = cpu
 PARAMETER DRIVER_VER = 1.12.b
 PARAMETER COMPILER = mb-gcc
 PARAMETER ARCHIVER = mb-ar
END

BEGIN OS
 PARAMETER PROC_INSTANCE = microblaze_1
 PARAMETER OS_NAME = standalone
 PARAMETER OS_VER = 3.00.a
 PARAMETER STDIN = mdm_0
 PARAMETER STDOUT = mdm_0
END

BEGIN PROCESSOR
 PARAMETER HW_INSTANCE = microblaze_0
 PARAMETER DRIVER_NAME = cpu
 PARAMETER DRIVER_VER = 1.12.b
 PARAMETER COMPILER = mb-gcc
 PARAMETER ARCHIVER = mb-ar
END

BEGIN OS
 PARAMETER PROC_INSTANCE = microblaze_0
 PARAMETER OS_NAME = standalone
 PARAMETER OS_VER = 3.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = mdm_0
 PARAMETER DRIVER_NAME = uartlite
 PARAMETER DRIVER_VER = 2.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = lmb_bram_1
 PARAMETER DRIVER_NAME = generic
 PARAMETER DRIVER_VER = 1.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = lmb_bram
 PARAMETER DRIVER_NAME = generic
 PARAMETER DRIVER_VER = 1.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = ilmb_cntlr_1
 PARAMETER DRIVER_NAME = bram
 PARAMETER DRIVER_VER = 2.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = ilmb_cntlr
 PARAMETER DRIVER_NAME = bram
 PARAMETER DRIVER_VER = 2.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = dlmb_cntlr_1
 PARAMETER DRIVER_NAME = bram
 PARAMETER DRIVER_VER = 2.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = dlmb_cntlr
 PARAMETER DRIVER_NAME = bram
 PARAMETER DRIVER_VER = 2.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = clock_generator_0
 PARAMETER DRIVER_NAME = generic
 PARAMETER DRIVER_VER = 1.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = ddr2_sdram
 PARAMETER DRIVER_NAME = mpmc
 PARAMETER DRIVER_VER = 4.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = Intr_Main
 PARAMETER DRIVER_NAME = intc
 PARAMETER DRIVER_VER = 2.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = Intr_Access
 PARAMETER DRIVER_NAME = intc
 PARAMETER DRIVER_VER = 2.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = npi_coreA_0
 PARAMETER DRIVER_NAME = generic
 PARAMETER DRIVER_VER = 1.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = npi_coreC_0
 PARAMETER DRIVER_NAME = generic
 PARAMETER DRIVER_VER = 1.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = npi_coreD_0
 PARAMETER DRIVER_NAME = generic
 PARAMETER DRIVER_VER = 1.00.a
END

BEGIN DRIVER
 PARAMETER HW_INSTANCE = npi_coreE_0
 PARAMETER DRIVER_NAME = generic
 PARAMETER DRIVER_VER = 1.00.a
END

