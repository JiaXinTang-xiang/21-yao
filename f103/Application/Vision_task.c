#include "Vision_task.h"
#include "Serial.h"

pid_type_def imu_pid;                     // PID结构体
pid_type_def Jetson_pid;                  // PID结构体
pid_type_def Jetson_pid_two;              // PID结构体
pid_type_def dis_pid;                     // PID结构体
float imu_params[3] = {1.0f, 0.0f, 0.0f};    // PID参数
float Jetson_params[3] = {1.5f, 0.0f, 0.0f}; // PID参数
float Jetson_Twoparams[3] = {1.5f, 0.0f, 0.0f}; // PID参数
float dis_params[3] = {-5.0f, 0.0f, 0.0f};    // PID参数

float Yaw_now = 0;                        // 当前角度
extern uint16_t diatance;                 // 当前距离

float Target_x = 0;                          // 目标标
//float Target_dis1 = 3.0;                     // 目标距离（速度慢的）
float Target_dis = 4;                      // 目标距离（速度快的）
float target_Motor = 40.0f;                  // 电机输出


static uint8_t pid_init_done = 0; // 标记PID是否已初始化


void Vision_task()
{  
	static float Vision_out;                             // 电机输出
	Vision_out = PID_calc(&Jetson_pid, center_x, Target_x);                             // 参数：1.PID结构体 2.视觉中心线的当前值 3.视觉目标值
	CanMotor_CanSpeedMode_Run2(target_Motor+Vision_out,  target_Motor-Vision_out, 5); // 参数：1.左轮速度  2.右轮速度（0-2000） 3.加速度（0-400）
}

void Vision_taskTwo()
{  
	static float Vision_out;                             // 电机输出
	Vision_out = PID_calc(&Jetson_pid_two, center_x, Target_x);                             // 参数：1.PID结构体 2.视觉中心线的当前值 3.视觉目标值
	CanMotor_CanSpeedMode_Run2(100+Vision_out,  100-Vision_out, 8); // 参数：1.左轮速度  2.右轮速度（0-2000） 3.加速度（0-400）
}

void Distance_Ctrl()
{
    static float Dis_out;                                      
    Dis_out = PID_calc(&dis_pid, diatance, Target_dis); 
    CanMotor_CanSpeedMode_Run2(Dis_out, Dis_out, 5); 
}


/**
 * @brief  步进电机转弯函数
 * @param  旋转度数( 范围: -180°~ 180° )
 * @retval 无
 */
extern int Run;
int Motor_Turn(float Turn_angle)
{
	static float error;
	static float target;
	static float finish;
	
    Yaw_now = Xreadangle.Yaw;
	
	if(!Run){
		target = Yaw_now - Turn_angle;	
		Run=1;
		finish=0;
	}
	
    // 计算目标角度与当前角度的最短路径
    error = target - Yaw_now;

    if (error > 180.0f)   error -= 360.0f;
    else if (error < -180.0f)  error += 360.0f;

    target = Yaw_now + error;

    PID_calc(&imu_pid, Yaw_now, target);

    // 误差小于1°停止
    if(abs((int)error) <= 0.5 ){
        imu_pid.out = 0;
		finish=1;
    }

    CanMotor_CanSpeedMode_Run2(-imu_pid.out, +imu_pid.out, 4);
	return finish;
}

/**
 * @brief  PID初始化函数
 * @param  无
 * @retval 无
 */
void PID_Ctrl_Init()
{
    // 仅初始化一次PID (避免每次循环重置积分项)
    if (!pid_init_done)
    {
        // 视觉环参数：1.PID结构体 2.位置式 3.PID参数数组 4.输出限幅 5.积分限幅
        PID_init(&Jetson_pid, PID_POSITION, Jetson_params, 30, 0);
		
		// 视觉环（速度快）参数：1.PID结构体 2.位置式 3.PID参数数组 4.输出限幅 5.积分限幅
        PID_init(&Jetson_pid_two, PID_POSITION, Jetson_Twoparams, 50, 0);

        // 角度参数：1.PID结构体 2.位置式 3.PID参数数组 4.输出限幅 5.积分限幅
        PID_init(&imu_pid, PID_POSITION, imu_params, 50, 0);

        // 距离参数：1.PID结构体 2.位置式 3.PID参数数组 4.输出限幅 5.积分限幅
        PID_init(&dis_pid, PID_POSITION, dis_params, 30, 30);
		
        pid_init_done = 1;
    }
}

