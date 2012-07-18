#include <xparameters.h>
#include <xil_io.h>
#include <xstatus.h>
#include <stdlib.h>

#include "xmbox.h"
#include "Software_Cores.h"

static XMbox Mbox;

//Input and Output Buffers
u32 *ProducerHello;
int RecvMsg;

void main (void)
{
   
   int Status;
   XMbox_Config *ConfigPtr;
   XStatus Stat;
   u32 id_function;
   
   Data2coreB_SW Send_coreB_SW;
   
   ///////////// Initialize MailBox ///////////////////////////////
   ConfigPtr = XMbox_LookupConfig(XPAR_MBOX_0_DEVICE_ID);
   if (ConfigPtr == (XMbox_Config *)XNULL)
   {
      return XST_FAILURE;
   }
   
   Stat = XMbox_CfgInitialize(&Mbox, ConfigPtr, ConfigPtr->BaseAddress);
   if (Stat != XST_SUCCESS)
   {
      return Stat;
   }
   /////////////////////////////////////////////////////////////////
   
   while(1)
   {
      
      //Receive the id of the function to execute
      Mailbox_Receive(&Mbox,sizeof(id_function));
      id_function = *(u32*) RecvMsg;
      
      switch (id_function)
      {
         case ACTIVE_SW_COREB: // coreB
         {
            Mailbox_Receive(&Mbox,sizeof(Send_coreB_SW));
            Send_coreB_SW = *(Data2coreB_SW*) RecvMsg;
            
            coreB(Send_coreB_SW.array, Send_coreB_SW.size, Send_coreB_SW.max);
            
            ProducerHello = &id_function;
            Mailbox_Send(&Mbox,sizeof(id_function));
            
            ProducerHello = &Send_coreB_SW;
            Mailbox_Send(&Mbox,sizeof(Send_coreB_SW));
            
            break;
         }
         default:
            break;
      }
   }
}

