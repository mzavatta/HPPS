#include <xparameters.h>
#include <xil_io.h>
#include <xstatus.h>
#include <stdlib.h>

#include "Software_Cores.h"
#include "xmbox.h"

u32 id_function;

extern u32 *ProducerHello;
extern u32 RecvMsg;

extern XMbox Mbox;
extern XMbox_Config *ConfigPtr;

extern u32 ActiveTask_SW;


void SW_coreB(void)
{
   id_function = ACTIVE_SW_COREB;
   ProducerHello = &id_function;
   Mailbox_Send(&Mbox,sizeof(id_function));
   
   ProducerHello = &Send_coreB_SW;
   Mailbox_Send(&Mbox,sizeof(Send_coreB_SW));
   
   ActiveTask_SW = ActiveTask_SW | ACTIVE_SW_COREB;
}

void Interrupt_SW(void *CallbackRef)
{
   XMbox *MboxInstPtr = (XMbox *)CallbackRef;
   //Clear Interrupt
   XMbox_ClearInterrupt  (MboxInstPtr, XMB_IX_RTA);
   Mailbox_Receive(&Mbox,sizeof(id_function));
   id_function = *(u32*) RecvMsg;
   switch (id_function)
   {
      case ACTIVE_SW_COREB: //coreB
         Mailbox_Receive(&Mbox,sizeof(Data2coreB_SW));
         Send_coreB_SW = *(Data2coreB_SW*) RecvMsg;
         ActiveTask_SW = ActiveTask_SW & ~(ACTIVE_SW_COREB);
         break;
      default:
         break;
   }
   if (!XMbox_IsEmptyHw(XPAR_XPS_MAILBOX_0_IF_1_BASEADDR)) Interrupt_SW(CallbackRef);
}

