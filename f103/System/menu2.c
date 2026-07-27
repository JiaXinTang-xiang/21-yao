#include "stm32f10x.h"       
#include "menu2.h"
#include "OLED.h"
#include "Key.h"
#include "Delay.h"



u8 keynum2;
u8 out;
extern int taskchoise;
// 显示主菜单
void OLED_ShowMainMenu2(void)
{
    OLED_Clear();
	
	OLED_ShowString(1, 3, "Basics_One");
	OLED_ShowString(2, 3, "Basics_Two");
    OLED_ShowString(3, 3, "FAHUI_One");
    OLED_ShowString(4, 3, "FAHUI_Two");  	
}

int menu2_main(void)//主菜单设置
{    int cflag=1;
	 if(out==0)
     {
	 OLED_ShowMainMenu2();
	 }
     while(out==0)
     {  keynum2=Key_GetNum();
        OLED_ShowString(cflag,1,"->");
	  	if(keynum2==1)
		{
			cflag++;
			for(int i=1;i<=4;i++)
			{
				 OLED_ShowString(i,1,"  ") ;
			}
			if(cflag>=5)cflag=1;		
		}
        if(keynum2==2)
	   {
            switch(cflag)
            {  
	             case 1:taskchoise=1;out=1;OLED_Clear();break;
	             case 2:taskchoise=2;out=1;OLED_Clear();break;
                 case 3:taskchoise=3;out=1;OLED_Clear();break;
                 case 4:taskchoise=4;out=1;OLED_Clear();break;
            }
      }
  }
}


