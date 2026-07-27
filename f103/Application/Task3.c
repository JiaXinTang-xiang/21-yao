#include "Task3.h"

extern uint64_t area;
extern int Run;
uint16_t Threeflag=0;

void Basics_Three()
{
    static uint16_t Threeflag=0;
	
    /* 
     * 主要任务：循线 路牌 红绿灯 障碍物
     *
     * 循线和路牌在下面switch case任务中判断
     * 障碍物通过定时器读取，如果开始小于某个值了，就把循线换成case2
     * 红绿灯通过
    */
    switch (Threeflag)
    {
        /* 先走循线,并在这个过程中不断判断路牌 */
        case 0:		  // id号左转是0，右转是1
			Run = 0;
            if(area>=50000 ){    // 如果路牌面积大于一个值(50000) 并且 id!=255则停止 进入下一步
                CanMotor_CanSpeedMode_Run2(0, 0, 5);
                Threeflag = 1;
            }
            else{     // 如果识别不到路牌 或者 路牌面积小于一个值
                Vision_task();
            }
            break;
        /* 第一个右转 */
        case 1:
			if( Motor_Turn(90) == 0){}
			else Threeflag=2;				
            break;
		case 2:
			Run = 0;
            if(area>=50000 ){    // 如果路牌面积大于一个值(50000) 并且 id!=255则停止 进入下一步
                CanMotor_CanSpeedMode_Run2(0, 0, 5);
                Threeflag = 3;
            }
            else{     // 如果识别不到路牌 或者 路牌面积小于一个值
                Vision_task();
            }
            break;		
        /* 第一个左转 */			
        case 3:
			if( Motor_Turn(-90) == 0){}
			else Threeflag=4;				
            break;			
		case 4:
			Run = 0;
            if(area>=50000 ){    // 如果路牌面积大于一个值(50000) 并且 id!=255则停止 进入下一步
                CanMotor_CanSpeedMode_Run2(0, 0, 5);
                Threeflag = 5;
            }
            else{     // 如果识别不到路牌 或者 路牌面积小于一个值
                Vision_task();
            }
            break;
        /* 第二个右转 */			
        case 5:
			if( Motor_Turn(90) == 0){}
			else Threeflag=6;				
            break;			
		case 6:
			Run = 0;
            if(area>=50000 ){    // 如果路牌面积大于一个值(50000) 并且 id!=255则停止 进入下一步
                CanMotor_CanSpeedMode_Run2(0, 0, 5);
                Threeflag = 7;
            }
            else{     // 如果识别不到路牌 或者 路牌面积小于一个值
                Vision_task();
            }
            break;		
        /* 第三个右转 */			
        case 7:
			if( Motor_Turn(90) == 0){}
			else Threeflag=8;				
            break;			
		case 8:
			Run = 0;
            if(area>=50000 ){    // 如果路牌面积大于一个值(50000) 并且 id!=255则停止 进入下一步
                CanMotor_CanSpeedMode_Run2(0, 0, 5);
                Threeflag = 9;
            }
            else{     // 如果识别不到路牌 或者 路牌面积小于一个值
                Vision_task();
            }
            break;
        /* 第四个右转 回到十字路口 */			
        case 9:
			if( Motor_Turn(90) == 0){}
			else Threeflag=10;				
            break;			
		case 10:
			Run = 0;
            if(area>=50000 ){    // 如果路牌面积大于一个值(50000) 并且 id!=255则停止 进入下一步
                CanMotor_CanSpeedMode_Run2(0, 0, 5);
                Threeflag = 11;
            }
            else{     // 如果识别不到路牌 或者 路牌面积小于一个值
                Vision_task();
            }
            break;		
        /* 第二个左转 */			
        case 11:
			if( Motor_Turn(-90) == 0){}
			else Threeflag=12;				
            break;			
		case 12:
			Run = 0;
            if(area>=50000 ){    // 如果路牌面积大于一个值(50000) 并且 id!=255则停止 进入下一步
                CanMotor_CanSpeedMode_Run2(0, 0, 5);
                Threeflag = 13;
            }
            else{     // 如果识别不到路牌 或者 路牌面积小于一个值
                Vision_task();
            }
            break;
        /* 第三个左转 */			
        case 13:
			if( Motor_Turn(-90) == 0){}
			else Threeflag=14;				
            break;			
		case 14:
			Run = 0;
            if(area>=50000 ){    // 如果路牌面积大于一个值(50000) 并且 id!=255则停止 进入下一步
                CanMotor_CanSpeedMode_Run2(0, 0, 5);
                Threeflag = 15;
            }
            else{     // 如果识别不到路牌 或者 路牌面积小于一个值
                Vision_task();
            }
            break;				
    }

}






