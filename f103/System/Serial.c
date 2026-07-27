#include "stm32f10x.h" // Device header
#include <string.h>
#include "Serial.h"

uint8_t Serial_RxPacket[VISION_FRAME_LENGTH]; // 接收数据包数组，不包含帧头和长度字节
uint8_t Serial_RxFlag;                        // 接收数据包标志位
VisionSerialData vision_data;


static uint16_t Vision_ReadU16(uint8_t *Data)
{
	return (uint16_t)Data[0] | ((uint16_t)Data[1] << 8);
}

static float Vision_ReadFloat(uint8_t *Data)
{
	uint32_t Value;
	float Result;

	Value = (uint32_t)Data[0]
	      | ((uint32_t)Data[1] << 8)
	      | ((uint32_t)Data[2] << 16)
	      | ((uint32_t)Data[3] << 24);
	memcpy(&Result, &Value, sizeof(Result));
	return Result;
}

/**
 * 函    数：串口初始化
 * 参    数：无
 * 返 回 值：无
 */
void Serial_Init(void)
{
	/*开启时钟*/
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

	/*GPIO初始化*/
	GPIO_InitTypeDef GPIO_InitStructure;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	/*USART初始化*/
	USART_InitTypeDef USART_InitStructure;
	USART_InitStructure.USART_BaudRate = 115200;
	USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
	USART_InitStructure.USART_Mode = USART_Mode_Tx | USART_Mode_Rx;
	USART_InitStructure.USART_Parity = USART_Parity_No;
	USART_InitStructure.USART_StopBits = USART_StopBits_1;
	USART_InitStructure.USART_WordLength = USART_WordLength_8b;
	USART_Init(USART1, &USART_InitStructure);

	/*中断输出配置*/
	USART_ITConfig(USART1, USART_IT_RXNE, ENABLE);

	/*NVIC中断分组*/
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);

	/*NVIC配置*/
	NVIC_InitTypeDef NVIC_InitStructure;
	NVIC_InitStructure.NVIC_IRQChannel = USART1_IRQn;
	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 1;
	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 1;
	NVIC_Init(&NVIC_InitStructure);

	Serial_RxFlag = 0;
	memset((void *)&vision_data, 0, sizeof(vision_data));

	/*USART使能*/
	USART_Cmd(USART1, ENABLE);
}

static void Serial_ParsePacket(void)
{
	uint16_t Cmd;
	uint8_t i;

	Cmd = Vision_ReadU16(&Serial_RxPacket[0]);
	vision_data.last_cmd = Cmd;
	vision_data.last_flags = Vision_ReadU16(&Serial_RxPacket[2]);

	if (Cmd == VISION_CMD_OUTER)
	{
		for (i = 0; i < 4; i++)
		{
			vision_data.outer[i][0] = Vision_ReadFloat(&Serial_RxPacket[4 + i * 8]);
			vision_data.outer[i][1] = Vision_ReadFloat(&Serial_RxPacket[8 + i * 8]);
		}
		vision_data.outer_valid = 1;
	}
	else if (Cmd == VISION_CMD_INNER)
	{
		for (i = 0; i < 4; i++)
		{
			vision_data.inner[i][0] = Vision_ReadFloat(&Serial_RxPacket[4 + i * 8]);
			vision_data.inner[i][1] = Vision_ReadFloat(&Serial_RxPacket[8 + i * 8]);
		}
		vision_data.inner_valid = 1;
	}
	else if (Cmd == VISION_CMD_RED)
	{
		vision_data.red_x = Vision_ReadFloat(&Serial_RxPacket[4]);
		vision_data.red_y = Vision_ReadFloat(&Serial_RxPacket[8]);
		vision_data.red_valid = (vision_data.red_x != 0.0f || vision_data.red_y != 0.0f);
	}
	else
	{
		vision_data.error_count++;
		return;
	}

	vision_data.frame_count++;
	Serial_RxFlag = 1;
}

/**
 * 函    数：获取串口接收标志位
 * 参    数：无
 * 返 回 值：接收标志位，读取后自动清零
 */
uint8_t Serial_GetRxFlag(void)
{
 	if (Serial_RxFlag == 1)
	{
		Serial_RxFlag = 0;
		return 1;
	}
	return 0;
}


/**
 * 函    数：USART1中断函数
 * 参    数：无
 * 返 回 值：无
 * 注意事项：此函数为中断函数，无需调用，中断触发后自动执行
 */
void USART1_IRQHandler(void)
{
	static uint8_t RxState = 0;
	static uint8_t pRxPacket = 0;

	if (USART_GetITStatus(USART1, USART_IT_RXNE) == SET)
	{
		uint8_t RxData = (uint8_t)USART_ReceiveData(USART1);
		vision_data.byte_count++;

		if (RxState == 0)
		{
			if (RxData == VISION_FRAME_HEAD)
			{
				RxState = 1;
			}
		}
		else if (RxState == 1)
		{
			if (RxData == VISION_FRAME_LENGTH)
			{
				pRxPacket = 0;
				RxState = 2;
			}
			else if (RxData != VISION_FRAME_HEAD)
			{
				RxState = 0;
			}
		}
		else if (RxState == 2)
		{
			Serial_RxPacket[pRxPacket] = RxData;
			pRxPacket++;

			if (pRxPacket >= VISION_FRAME_LENGTH)
			{
				RxState = 0;
				pRxPacket = 0;
				Serial_ParsePacket();
			}
		}

		USART_ClearITPendingBit(USART1, USART_IT_RXNE);
	}
}
