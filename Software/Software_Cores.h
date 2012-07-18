#define START 0x08000000
#define DONE 0x04000000
typedef struct {
   int* array;
   int size;
   int* max;
} Data2coreB_SW;

#define ACTIVE_SW_COREB 0x1
extern Data2coreB_SW Send_coreB_SW;


