#ifndef __SERIALK230_H
#define __SERIALK230_H

#include "stm32f10x.h"

#define VISION_FRAME_HEAD  0x12
#define VISION_FRAME_TAIL  0x5B
#define VISION_MAX_DIGITS  4

/* STM32 USART2 receives MaixCam2 UART4 output at 115200 baud. */
void Serial_Init_K(void);
uint8_t Vision_GetRxFlag(void);

/* Compatibility API retained for existing task files; new code uses Vision_GetRxFlag(). */
uint8_t Serial_GetRxFlag_K(void);
void Serial_GetData_K(void);
extern int k230_w;
extern int k230_h;
extern int k230_flag;

/* Read these after Vision_GetRxFlag() returns 1. Digits are left to right. */
extern volatile uint8_t vision_count;
extern volatile uint8_t vision_digits[VISION_MAX_DIGITS];
extern volatile uint32_t vision_frame_count;
extern volatile uint32_t vision_error_count;
extern uint8_t Serial_RxPacket_K[VISION_MAX_DIGITS + 1];
extern uint8_t Serial_RxFlag_K;

#endif
