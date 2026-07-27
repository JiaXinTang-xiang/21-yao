#ifndef __SERIAL_H
#define __SERIAL_H

#include <stdio.h>
#include "stm32f10x.h" // Device header

#define VISION_FRAME_HEAD      0xA5
#define VISION_FRAME_LENGTH    0x34
#define VISION_CMD_OUTER       0x0102
#define VISION_CMD_INNER       0x0103
#define VISION_CMD_RED         0x0104

/* 视觉串口解析后的数据，坐标单位为像素 */
typedef struct
{
	float outer[4][2];
	float inner[4][2];
	float red_x;
	float red_y;
	uint16_t last_cmd;
	uint16_t last_flags;
	uint8_t outer_valid;
	uint8_t inner_valid;
	uint8_t red_valid;
	uint32_t byte_count;
	uint32_t frame_count;
	uint32_t error_count;
} VisionSerialData;

extern uint8_t Serial_RxPacket[];
extern uint8_t Serial_RxFlag;
extern VisionSerialData vision_data;


void Serial_Init(void);
uint8_t Serial_GetRxFlag(void);

#endif
