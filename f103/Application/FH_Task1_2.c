#include "FH_Task1_2.h"

extern uint16_t diatance; // 当前距离
extern uint64_t area;
uint16_t FH2_flag = 0;
extern uint8_t sign_id;
extern int Run;
extern int k230_flag;
// 地图
//    7               8                9
//      -----------      -----------
//      |         |      |         |
//      |         |      |         |
//      |         |      |         |
//      -----------  —  -----------
//    4           |   5  |              6
//      -----------  —  -----------
//      |         |      |         |
//      |         |      |         |
//      |         |      |         |
//      -----------      -----------
//    1               2                3
// 起点                               终点
static uint8_t cnt = 0;
void FAHUI_Two()
{
	if (k230_flag != 0 && diatance <= 50 && diatance >= 20) // 红灯→停车
	{
		if (++cnt > 3)
		{
			Target_dis = 40;
			Distance_Ctrl();
		}
	}
	else // 循迹+避障
	{
		cnt = 0;

		if (FH2_flag != 1 && FH2_flag != 2 && diatance <= 5 && sign_id == 255) // 避障检测
		{
			fmq_ON();
			FH2_flag = 999;
		}
		else
		{
			fmq_OFF();
			if (FH2_flag == 999)
				FH2_flag = 0; // 只有从避障退出时才清零，继续执行寻找路牌转向
		}

		switch (FH2_flag)
		{
		case 0: // id号左转是0，右转是1
			Run = 0;
			if (area >= 28000 && sign_id == 0)
			{
				CanMotor_CanSpeedMode_Run2(0, 0, 5);
				FH2_flag = 1;
			}
			else if (area >= 28000 && sign_id == 1)
			{
				CanMotor_CanSpeedMode_Run2(0, 0, 5);
				FH2_flag = 2;
			}
			else if (area >= 5000 && sign_id == 2)
			{
				CanMotor_CanSpeedMode_Run2(0, 0, 5);
				FH2_flag = 3;
			}
			else
			{ // 如果识别不到路牌 或者 路牌面积小于一个值
				Vision_taskTwo();
				// fmq_OFF(); // 感觉重复了，先注释看看
			}
			break;
		/* 左转 */
		case 1:
			if (Motor_Turn(-90) == 0)
			{
			}
			else
			{
				GY56_Read();
				FH2_flag = 0;
			}
			break;
		/* 右转 */
		case 2:
			if (Motor_Turn(90) == 0)
			{
			}
			else
			{
				GY56_Read();
				FH2_flag = 0;
			}
			break;
		/* 停车前走一段 */
		case 3:
			CanMotor_CanSpeedMode_Run2(100, 100, 5); // 两轮同速前进（速度40）
			Delay_ms(600);							 // 走2秒
			FH2_flag = 4;							 // 跳到停车
			break;
		case 4:

			CanMotor_CanSpeedMode_Run2(0, 0, 5); // 彻底停下
			break;

		/* 遇到障碍物 */
		case 999:
			if (area >= 28000 && sign_id == 0)
			{
				FH2_flag = 1;
			}
			else if (area >= 28000 && sign_id == 1)
			{
				FH2_flag = 2;
			}
			else if (area >= 5000 && sign_id == 2)
			{
				FH2_flag = 3;
			}
			else
			{
				Target_dis = 8; // 距离障碍物的目标距离
				Distance_Ctrl();
			}
			break;
		}
	}
}
