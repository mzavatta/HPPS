#include <xparameters.h>
#include <xil_io.h>
#include <xstatus.h>
#include <stdlib.h>

#include "xmbox.h"
#include "xintc.h"
#include "Software_Cores.h"
#include "Hardware_Cores.h"

/*-----------------------------------------------------*/
extern u32 *ProducerHello;
extern u32 *RecvMsg;
extern u32 ActiveTask_SW;
extern XMbox Mbox;
extern XMbox_Config *ConfigPtr;
/*-----------------------------------------------------*/

void Interrupt_SW(void *CallbackRef);


/*****************************************************************************
*
* This function sends the a message to the other processor.
*
******************************************************************************/
int Mailbox_Send(XMbox *MboxInstancePtr, int size_bytes)
{
	XStatus Status;
	u32 Nbytes;
	u32 BytesSent;

	Nbytes = 0;
	
	while (Nbytes < size_bytes) {
		Status = XMbox_Write(MboxInstancePtr,(u32*)((u8*)ProducerHello + Nbytes),
				     (size_bytes - Nbytes),&BytesSent);

		if (Status == XST_SUCCESS) Nbytes += BytesSent;
		
	}

	return XST_SUCCESS;
}

/*****************************************************************************
*
* This function receives a message from the other processor. It waits until a 
* message arrives to the MailBox.
*
******************************************************************************/
int Mailbox_Receive(XMbox *MboxInstancePtr, int size_bytes)
{
	XStatus Status;
	u32 Nbytes;
	u32 BytesRcvd;

	Nbytes = 0;

	RecvMsg = (u32*)malloc(size_bytes);

	while (Nbytes < size_bytes) {

		Status = XMbox_Read(MboxInstancePtr,(u32*)(RecvMsg + Nbytes), size_bytes, &BytesRcvd);		 
		if (Status == XST_SUCCESS){Nbytes += BytesRcvd;}

	}
}


/*****************************************************************************
*
* MailBox Interruption Configuration
*
******************************************************************************/
void Mailbox_Int(XIntc *InstancePtr, XMbox *MboxInstPtr) {

	XMbox_SetReceiveThreshold(MboxInstPtr, XPAR_INTR_MAIN_XPS_MAILBOX_0_INTERRUPT_1_INTR);
	
	XIntc_Connect(InstancePtr,0,(XInterruptHandler)Interrupt_SW,(void *)MboxInstPtr);
					 
	XMbox_SetInterruptEnable(MboxInstPtr,XMB_IX_RTA); 

}

