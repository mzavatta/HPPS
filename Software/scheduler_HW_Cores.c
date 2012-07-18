#include <xparameters.h>
#include <xil_io.h>
#include <xstatus.h>
#include <stdlib.h>

#include "Hardware_Cores.h"
#include "Software_Cores.h"
#include "em_bridge_npi.h"

extern u32 ActiveTask_HW;


void HW_coreA(void)
{
   EM_BRIDGE_NPI_mWriteSlaveReg2(XPAR_NPI_COREA_0_BASEADDR, 0, Send_coreA_HW.array);
   EM_BRIDGE_NPI_mWriteSlaveReg3(XPAR_NPI_COREA_0_BASEADDR, 0, Send_coreA_HW.size);
   ActiveTask_HW = ActiveTask_HW | ACTIVE_HW_COREA;
   EM_BRIDGE_NPI_mWriteSlaveReg0(XPAR_NPI_COREA_0_BASEADDR, 0, START);
}

void Interrupt_coreA_HW(void *CallbackRef)
{
   Send_coreA_HW.__return = EM_BRIDGE_NPI_mReadSlaveReg1(XPAR_NPI_COREA_0_BASEADDR, 0);
   EM_BRIDGE_NPI_mWriteSlaveReg0(XPAR_NPI_COREA_0_BASEADDR, 0, 0);
   ActiveTask_HW = ActiveTask_HW & (~ACTIVE_HW_COREA);
}

void HW_coreC(void)
{
   EM_BRIDGE_NPI_mWriteSlaveReg2(XPAR_NPI_COREC_0_BASEADDR, 0, Send_coreC_HW.a);
   EM_BRIDGE_NPI_mWriteSlaveReg3(XPAR_NPI_COREC_0_BASEADDR, 0, Send_coreC_HW.b);
   ActiveTask_HW = ActiveTask_HW | ACTIVE_HW_COREC;
   EM_BRIDGE_NPI_mWriteSlaveReg0(XPAR_NPI_COREC_0_BASEADDR, 0, START);
}

void Interrupt_coreC_HW(void *CallbackRef)
{
   Send_coreC_HW.__return = EM_BRIDGE_NPI_mReadSlaveReg1(XPAR_NPI_COREC_0_BASEADDR, 0);
   EM_BRIDGE_NPI_mWriteSlaveReg0(XPAR_NPI_COREC_0_BASEADDR, 0, 0);
   ActiveTask_HW = ActiveTask_HW & (~ACTIVE_HW_COREC);
}

void HW_coreD(void)
{
   EM_BRIDGE_NPI_mWriteSlaveReg2(XPAR_NPI_CORED_0_BASEADDR, 0, Send_coreD_HW.a);
   EM_BRIDGE_NPI_mWriteSlaveReg3(XPAR_NPI_CORED_0_BASEADDR, 0, Send_coreD_HW.b);
   EM_BRIDGE_NPI_mWriteSlaveReg4(XPAR_NPI_CORED_0_BASEADDR, 0, Send_coreD_HW.c);
   ActiveTask_HW = ActiveTask_HW | ACTIVE_HW_CORED;
   EM_BRIDGE_NPI_mWriteSlaveReg0(XPAR_NPI_CORED_0_BASEADDR, 0, START);
}

void Interrupt_coreD_HW(void *CallbackRef)
{
   EM_BRIDGE_NPI_mWriteSlaveReg0(XPAR_NPI_CORED_0_BASEADDR, 0, 0);
   ActiveTask_HW = ActiveTask_HW & (~ACTIVE_HW_CORED);
}

void HW_coreE(void)
{
   EM_BRIDGE_NPI_mWriteSlaveReg2(XPAR_NPI_COREE_0_BASEADDR, 0, Send_coreE_HW.a);
   ActiveTask_HW = ActiveTask_HW | ACTIVE_HW_COREE;
   EM_BRIDGE_NPI_mWriteSlaveReg0(XPAR_NPI_COREE_0_BASEADDR, 0, START);
}

void Interrupt_coreE_HW(void *CallbackRef)
{
   Send_coreE_HW.__return = EM_BRIDGE_NPI_mReadSlaveReg1(XPAR_NPI_COREE_0_BASEADDR, 0);
   EM_BRIDGE_NPI_mWriteSlaveReg0(XPAR_NPI_COREE_0_BASEADDR, 0, 0);
   ActiveTask_HW = ActiveTask_HW & (~ACTIVE_HW_COREE);
}

