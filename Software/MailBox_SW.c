#include <xparameters.h>
#include <xil_io.h>
#include <xstatus.h>
#include <stdlib.h>

#include "xmbox.h"

extern u32 *ProducerHello;
extern int RecvMsg;


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

