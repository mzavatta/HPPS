#include <xparameters.h>
#include <xil_io.h>
#include <xstatus.h>
#include <stdlib.h>
#include "xintc.h"
#include "xil_exception.h"
#include "Software_Cores.h"
#include "Hardware_Cores.h"

extern u32 ActiveTask_HW;

void Interrupt_coreA_HW(void *CallbackRef);
void Interrupt_coreC_HW(void *CallbackRef);
void Interrupt_coreD_HW(void *CallbackRef);
void Interrupt_coreE_HW(void *CallbackRef);

//Add a new IP to the Interrupt controller
void Interrupt_Config(XIntc *InstancePtr, u16 DeviceId)
{
   Xuint32 IntMasc;
   int Status;
   if (InstancePtr->IsReady == 0)
   {
      Status = XIntc_Initialize(InstancePtr, DeviceId);
      if (Status != XST_SUCCESS)
      {
         xil_printf("Interruptions Initialization Fail \n\r");
      }
   }
   u32 dir;
   //Interrupts Connected
   Status = XIntc_Connect(InstancePtr, 1,(XInterruptHandler) Interrupt_coreA_HW, (void *)dir);
   Status = XIntc_Connect(InstancePtr, 2,(XInterruptHandler) Interrupt_coreC_HW, (void *)dir);
   Status = XIntc_Connect(InstancePtr, 3,(XInterruptHandler) Interrupt_coreD_HW, (void *)dir);
   Status = XIntc_Connect(InstancePtr, 4,(XInterruptHandler) Interrupt_coreE_HW, (void *)dir);
   //Initialize interruptions
   Status = XIntc_Start(InstancePtr, XIN_REAL_MODE);
   IntMasc = 0xFF;
   XIntc_EnableIntr(InstancePtr->BaseAddress, IntMasc);
   microblaze_enable_interrupts();
}

