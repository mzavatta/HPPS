void coreB(int* array, int size, int* max)
{
   int internal_161_11;
   int i_12;
   int i_1;
   int i_4;
   unsigned int i_5_6;
   unsigned int internal_157_7;
   int* internal_158_9;
   int value_10;
   *(max) = 0;
   i_4 = 0;
   i_1 = i_4;
   //start of a loop
   GOTOLABEL1:
   if (i_1 < size)
   {
      i_5_6 = (unsigned int) (i_1);
      internal_157_7 = i_5_6 * (4u);
      internal_158_9 = array + i_5_6;
      value_10 = *(internal_158_9);
      if (i_1 == (0))
      {
         *(max) = value_10;
      }
      else
      {
         internal_161_11 = *(max);
         if (internal_161_11 < value_10)
         {
            *(max) = value_10;
         }
      }
      i_12 = (int)(i_1 + (1));
      i_1 = i_12;
      goto GOTOLABEL1;
   }
   return ;
}


