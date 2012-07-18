typedef struct {
   int* array;
   int size;
   int __return;
} Data2coreA_HW;

typedef struct {
   int a;
   int b;
   int __return;
} Data2coreC_HW;

typedef struct {
   int a;
   int b;
   int* c;
} Data2coreD_HW;

typedef struct {
   int* a;
   int __return;
} Data2coreE_HW;

#define ACTIVE_HW_COREA 0x1
extern Data2coreA_HW Send_coreA_HW;

#define ACTIVE_HW_COREC 0x2
extern Data2coreC_HW Send_coreC_HW;

#define ACTIVE_HW_CORED 0x4
extern Data2coreD_HW Send_coreD_HW;

#define ACTIVE_HW_COREE 0x8
extern Data2coreE_HW Send_coreE_HW;


