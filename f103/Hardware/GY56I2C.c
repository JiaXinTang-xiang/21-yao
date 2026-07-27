#include "IIC.h"
#include "delay.h"
#include  "GY56I2C.h"

/*
Keil: MDK5.10.0.2
MCU:stm32f103c8
GY-56---STM32
SCL---PB6
SDA---PB7
中断函数位于stm32f10x_it.c
*/
uint16_t diatance=0;
u8 j=0;
u8 ADDR=0Xe0;

void GY56_Init(void)
{
	I2C_GPIO_Config();
	Delay_ms(100);//等待模块初始化完成
}
uint16_t  GY56_Read(void)
{	  
	    // changeAddress(ADDR,0x40);//更改IIC地址
		requestRange((ADDR+1),&diatance);
		takeRangeReading(ADDR);
	    return diatance;
}
