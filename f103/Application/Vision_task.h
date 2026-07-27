#ifndef __VISION_TASK_H
#define __VISION_TASK_H

#include "bsp.h"

extern float Motor_out;	// 电机输出
extern float Target_dis;   // 目标距离

void PID_Ctrl_Init(void);
void Vision_task(void);
void Vision_taskTwo(void);
int Motor_Turn(float Turn_angle);
void Distance_Ctrl(void);

#endif

