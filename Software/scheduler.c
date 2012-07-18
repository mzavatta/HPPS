#include "xparameters.h"
#include "xil_io.h"
#include "xstatus.h"
#include "stdlib.h"
#include "xintc.h"
#include "xil_exception.h"
#include "xmbox.h"
#include "Software_Cores.h"
#include "Hardware_Cores.h"

//START VARIABLE DEFINITION
XMbox Mbox;
XMbox_Config *ConfigPtr;
Data2coreA_HW Send_coreA_HW;
Data2coreB_SW Send_coreB_SW;
Data2coreC_HW Send_coreC_HW;
Data2coreD_HW Send_coreD_HW;
Data2coreE_HW Send_coreE_HW;
u32 ActiveTask_HW = 0;
u32 ActiveTask_SW = 0;
//Input and Output Buffers
u32 *ProducerHello;
u32 *RecvMsg;
/* Instance of the Interrupt Controller */
XIntc InterruptController;
//START VARIABLE DEFINITION

//START SHARED VARIABLES
int *array = 0x9a000000;
//END SHARED VARIABLES
int c_3_4;
int c;
int b_1_5;
int a_2_6;
int c_4_7;
int internal_374_8;
int a_0_1;
int b_1_2;
int b;
int a_2_3;
int a_17;
//END VARIABLE DEFINITION
#define TASKNUM 11
#define PROCELEM 3
unsigned int taskGraph[TASKNUM][TASKNUM];
unsigned int taskState[TASKNUM],tempTaskState;
unsigned int waitFor[TASKNUM];
unsigned int runnable[TASKNUM];
void (*runFunction[TASKNUM])(void);
unsigned int processingElement[PROCELEM];
unsigned int mapping[TASKNUM];
unsigned int __END__=0;
//START TASKS PROTOTYPE
void Start0_0_1_20();
void Start0_0_1_21();
void Start0_0_1_22();
void Start0_0_1_23();
void Start0_0_1_24();
void Start0_0_1_25();
void Start0_0_1_26();
void Start0_0_1_27();
void Start0_0_1_28();
void Start0_0_1_29();
void Start0_0_1_210();
//END TASK PROTOTYPES
//START SCHEDULER INITIALIZATION FUNCTION
void initSchedule()
{
   unsigned int i=0;
   unsigned int l=0;
   tempTaskState=0;
   for(i=0;i<TASKNUM;i++)
   {
      for(l=0;l<TASKNUM;l++)
      taskGraph[i][l]=0;
   }
   taskGraph[1][0]=1;
   taskGraph[2][1]=1;
   taskGraph[3][2]=1;
   taskGraph[4][3]=1;
   taskGraph[5][4]=1;
   taskGraph[6][5]=1;
   taskGraph[7][6]=1;
   taskGraph[8][7]=1;
   taskGraph[9][8]=1;
   taskGraph[10][9]=1;
   waitFor[0]= 0;
   waitFor[1]= 1;
   waitFor[2]= 1;
   waitFor[3]= 1;
   waitFor[4]= 1;
   waitFor[5]= 1;
   waitFor[6]= 1;
   waitFor[7]= 1;
   waitFor[8]= 1;
   waitFor[9]= 1;
   waitFor[10]= 1;
   runnable[0]= 1;
   runnable[1]= 0;
   runnable[2]= 0;
   runnable[3]= 0;
   runnable[4]= 0;
   runnable[5]= 0;
   runnable[6]= 0;
   runnable[7]= 0;
   runnable[8]= 0;
   runnable[9]= 0;
   runnable[10]= 0;
   runFunction[0]= Start0_0_1_20;
   runFunction[1]= Start0_0_1_21;
   runFunction[2]= Start0_0_1_22;
   runFunction[3]= Start0_0_1_23;
   runFunction[4]= Start0_0_1_24;
   runFunction[5]= Start0_0_1_25;
   runFunction[6]= Start0_0_1_26;
   runFunction[7]= Start0_0_1_27;
   runFunction[8]= Start0_0_1_28;
   runFunction[9]= Start0_0_1_29;
   runFunction[10]= Start0_0_1_210;
   processingElement[0]=1; //microblaze_1
   processingElement[1]=1; //microblaze_0
   processingElement[2]=1; //fpga_area
   processingElement[3]=1; //r0
   mapping[0]=0;//microblaze_1
   mapping[1]=3;//r0
   mapping[2]=0;//microblaze_1
   mapping[3]=0;//microblaze_1
   mapping[4]=1;//microblaze_0
   mapping[5]=0;//microblaze_1
   mapping[6]=3;//r0
   mapping[7]=0;//microblaze_1
   mapping[8]=0;//microblaze_1
   mapping[9]=3;//r0
   mapping[10]=0;//microblaze_1
}
//END SCHEDULER INITIALIZATION FUNCTION
//START TASKS DECLARATION
void Start0_0_1_20()
{
   (array)[0u] = 4;
   (array)[1u] = 3;
   (array)[2u] = 6;
   (array)[3u] = 5;
   (array)[4u] = 4;
   #pragma omp parallel sections num_threads(2) 
   {
      #pragma omp section
      {
         ActiveTask_SW |= 1 <<0;
      }
      void Start0_0_1_21()
      {
         Send_coreA_HW.array = &(array[0]) - 0x90000000;
         Send_coreA_HW.size = 5;
         HW_coreA();
      }
      void Start0_0_1_22()
      {
         a_0_1 = Send_coreA.__result;
         ActiveTask_SW |= 1 <<2;
      }
      void Start0_0_1_23()
      {
         a_17 = a_0_1;
         
      }
      #pragma omp section
      {
         ActiveTask_SW |= 1 <<3;
      }
      void Start0_0_1_24()
      {
         Send_coreB_SW.array = &(array[0]) - 0x90000000;
         Send_coreB_SW.size = 5;
         Send_coreB_SW.max = &(b) - 0x90000000;
         SW_coreB();
      }
      void Start0_0_1_25()
      {
         
      }
      
   }
   b_1_2 = b;
   a_2_3 = a_17;
   ActiveTask_SW |= 1 <<5;
}
void Start0_0_1_26()
{
   Send_coreC_HW.a = a_2_3;
   Send_coreC_HW.b = b_1_2;
   HW_coreC();
}
void Start0_0_1_27()
{
   c_3_4 = Send_coreC.__result;
   ActiveTask_SW |= 1 <<7;
}
void Start0_0_1_28()
{
   c = c_3_4;
   b_1_5 = b;
   a_2_6 = a_17;
   ActiveTask_SW |= 1 <<8;
}
void Start0_0_1_29()
{
   Send_coreD_HW.a = a_2_6;
   Send_coreD_HW.b = b_1_5;
   Send_coreD_HW.c = &(c) - 0x90000000;
   HW_coreD();
}
void Start0_0_1_210()
{
   c_4_7 = c;
   printf("test = %d\n", c_4_7);
   internal_374_8 = c;
   __END__=1;
   ActiveTask_SW |= 1 <<10;
}
//END TASK DECLARATIONS
void schedule()
{
   unsigned int i;
   for(i=0;i<TASKNUM;i++){
      if(runnable[i]==1 && processingElement[mapping[i]]==1)
      {
         (*runFunction[i])();
         runnable[i]=0;
         processingElement[mapping[i]]=0;
      }
   }
}
void updateSchedule()
{
   unsigned int i,l,t;
   for(t=0;t<TASKNUM;t++)
   {
      if(tempTaskState & (1<<t))
      {
         ActiveTask_SW &= ~(1<<t);
         ActiveTask_HW &= ~(1<<t);
         processingElement[mapping[t]]=1;
         for(i=0;i<TASKNUM;i++)
         {
            if(taskGraph[i][t]==1)
            {
               taskGraph[i][t]=0;
               waitFor[i]-=1;
               if(!waitFor[i])
               {
                  runnable[i]=1;
               }
            }
         }
      }
   }
   schedule();
}
int main()
{
   int Status;
   u32 index;
   ///////////// Initialize the System //////////////////
   ConfigPtr = XMbox_LookupConfig(XPAR_MBOX_0_DEVICE_ID);
   if (ConfigPtr == (XMbox_Config *)XNULL)
   {
      return XST_FAILURE;
   }
   Status = XMbox_CfgInitialize(&Mbox, ConfigPtr, ConfigPtr->BaseAddress);
   if (Status != XST_SUCCESS)
   {
      return Status;
   }
   Interrupt_Config(&InterruptController, 0);
   Mailbox_Int(&InterruptController, &Mbox);
   ////////////////////////////////////////////////////////////////
   initSchedule();
   schedule();
   while(!__END__)
   {
      unsigned int i;
      tempTaskState=ActiveTask_HW | ActiveTask_SW;
      for(i=0;i<TASKNUM;i++)
      if(tempTaskState & (1<<i))
      {
         updateSchedule();
         break;
      }
   }
   return internal_374_8;
}

