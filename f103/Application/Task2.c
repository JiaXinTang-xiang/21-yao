#include "Task2.h"


extern int Run;
extern int k230_flag;
int aa=0;

void get_ser(void)
{

		if (Serial_GetRxFlag() == 1)
		{
//			Serial_GetData(); // 获取数据
		}

		if (Serial_GetRxFlag_K() == 1)
		{
			Serial_GetData_K(); // 获取K230数据
		}

}

void Basics_Two()
{
	static uint16_t Oneflag=0;
	switch (Oneflag)
	{
		case 0:
			CanMotor_CanPositionMode_Run(0x01,5,100,190000,0,0x02,5,100,190000,0);
			Delay_ms(2600);
			Oneflag=1;
			break;//1
		case 1:
			if( Motor_Turn(89) == 0){}
			else Oneflag=2;			
			break;
		case 2:
			CanMotor_CanPositionMode_Run(0x01,5,100,82000,0,0x02,5,100,82000,0);
			Delay_ms(2000);Run=0;
		    get_ser();
		    OLED_ShowSignedNum(4, 1, k230_flag, 2);
		    while(1)
		    {  if(k230_flag==0)
				aa++;
			   Delay_ms(20);
			   if(aa>=10)
			   break;
			   get_ser();
			   OLED_ShowSignedNum(4, 1, k230_flag, 2);
			  } aa=0;
		        CanMotor_CanPositionMode_Run(0x01,5,100,83000,0,0x02,5,100,83000,0);
			    Delay_ms(1800);
			    Oneflag=3;
			    break;//2
		
		
		
		
		
		case 3:
			if( Motor_Turn(-93) == 0){}
			else Oneflag=4;			
			break;
		case 4:
			CanMotor_CanPositionMode_Run(0x01,5,100,169000,0,0x02,5,100,169000,0);
			Delay_ms(2600);
			Oneflag=5;Run=0;
			break;//3
		case 5:
			if( Motor_Turn(85) == 0){}
			else Oneflag=6;			
			break;
		case 6:
			CanMotor_CanPositionMode_Run(0x01,5,100,164000,0,0x02,5,100,164000,0);
			Delay_ms(2600);
			Oneflag=7;Run=0;
			break;//4
		case 7:
			if( Motor_Turn(89) == 0){}
			else Oneflag=8;			
			break;
		case 8:
			CanMotor_CanPositionMode_Run(0x01,5,100,169000,0,0x02,5,100,169000,0);
			Delay_ms(2600);
			Oneflag=9;Run=0;
			break;//5
		case 9:
			if( Motor_Turn(89) == 0){}///////////
			else Oneflag=10;			
			break;
		case 10:
			CanMotor_CanPositionMode_Run(0x01,5,100,82000,0,0x02,5,100,82000,0);
			Delay_ms(2000);//6
		
		    get_ser();
		    OLED_ShowSignedNum(4, 1, k230_flag, 2);
		    
		    while(1)
		    {  if(k230_flag==0)
				aa++;
			   Delay_ms(20);
			   if(aa>=10)
			   break;
			   get_ser();
			   OLED_ShowSignedNum(4, 1, k230_flag, 2);
			   }aa=0;
		    CanMotor_CanPositionMode_Run(0x01,5,100,80000,0,0x02,5,100,80000,0);
		    Delay_ms(1800);
			Oneflag=11;Run=0;
			break;//6
		
		
		
		
		
		
		case 11:
			if( Motor_Turn(-88) == 0){}
			else Oneflag=12;			
			break;
		case 12:
			CanMotor_CanPositionMode_Run(0x01,5,100,158000,0,0x02,5,100,158000,0);
			Delay_ms(2400);
			Oneflag=13;Run=0;
			break;//7
		case 13:
			if( Motor_Turn(-90) == 0){}
			else Oneflag=14;			
			break;
		case 14:
			CanMotor_CanPositionMode_Run(0x01,5,100,145000,0,0x02,5,100,145000,0);
			Delay_ms(2500);
			Oneflag=15;Run=0;
			break;//8
		
	}
	
}

