#include "stm32f10x.h"
#include "SerialK230.h"

volatile uint8_t vision_count;
volatile uint8_t vision_digits[VISION_MAX_DIGITS];
volatile uint8_t vision_rx_flag;
volatile uint32_t vision_frame_count;
volatile uint32_t vision_error_count;
uint8_t Serial_RxPacket_K[VISION_MAX_DIGITS + 1];
uint8_t Serial_RxFlag_K;

/* Compatibility values for the older K230 task files already in this project. */
int k230_w;
int k230_h;
int k230_flag;

static uint8_t Vision_IsValidCount(uint8_t count)
{
	return (count <= 4U);
}

void Serial_Init_K(void)
{
	GPIO_InitTypeDef GPIO_InitStructure;
	USART_InitTypeDef USART_InitStructure;
	NVIC_InitTypeDef NVIC_InitStructure;

	/* Keep the existing F103 vision port: USART2, PA2=TX and PA3=RX, 115200. */
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	USART_InitStructure.USART_BaudRate = 115200;
	USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
	USART_InitStructure.USART_Mode = USART_Mode_Tx | USART_Mode_Rx;
	USART_InitStructure.USART_Parity = USART_Parity_No;
	USART_InitStructure.USART_StopBits = USART_StopBits_1;
	USART_InitStructure.USART_WordLength = USART_WordLength_8b;
	USART_Init(USART2, &USART_InitStructure);

	USART_ITConfig(USART2, USART_IT_RXNE, ENABLE);
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);
	NVIC_InitStructure.NVIC_IRQChannel = USART2_IRQn;
	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 1;
	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 1;
	NVIC_Init(&NVIC_InitStructure);

	vision_count = 0;
	vision_rx_flag = 0;
	Serial_RxFlag_K = 0;
	vision_frame_count = 0;
	vision_error_count = 0;
	k230_w = 0;
	k230_h = 0;
	k230_flag = 1;
	USART_Cmd(USART2, ENABLE);
}

uint8_t Vision_GetRxFlag(void)
{
	if (Serial_RxFlag_K == 0U)
	{
		return 0;
	}

	Serial_RxFlag_K = 0;
	vision_rx_flag = 0;
	return 1;
}

uint8_t Serial_GetRxFlag_K(void)
{
	return Vision_GetRxFlag();
}

void Serial_GetData_K(void)
{
	/* Serial_RxPacket_K[0] is count; following bytes are left-to-right digits. */
	k230_w = Serial_RxPacket_K[0];
	k230_h = (k230_w > 0) ? Serial_RxPacket_K[1] : 0;
	k230_flag = (k230_w == 0) ? 1 : 0;
}

/* Maix frame: 12 | count | digit_1 ... digit_N | xor | 5B. */
void USART2_IRQHandler(void)
{
	static uint32_t RxState = 0;
	static uint32_t pRxPacket = 0;
	static uint8_t RxChecksum = 0;
	uint8_t RxData;
	uint8_t i;

	/* If a USART2 receive interrupt occurred, read exactly one byte. */
	if (USART_GetITStatus(USART2, USART_IT_RXNE) == SET)
	{
		RxData = (uint8_t)USART_ReceiveData(USART2);

		/* State 0: receive frame head 0x12. */
		if (RxState == 0)
		{
			if (RxData == VISION_FRAME_HEAD && Serial_RxFlag_K == 0U)
			{
				RxState = 1;
			}
		}
		/* State 1: receive count. Values 0 through 4 are valid. */
		else if (RxState == 1)
		{
			if (Vision_IsValidCount(RxData))
			{
				/* Packet data begins with count, followed by four digit positions. */
				Serial_RxPacket_K[0] = RxData;
				RxChecksum = RxData;
				pRxPacket = 0;
				RxState = 2;
			}
			else
			{
				vision_error_count++;
				RxState = (RxData == VISION_FRAME_HEAD) ? 1 : 0;
			}
		}
		/* State 2: always receive four digit bytes into Serial_RxPacket_K[1...4]. */
		else if (RxState == 2)
		{
			/* Only the first count positions may be 1..8; remaining positions must be 0. */
			if (((pRxPacket < Serial_RxPacket_K[0]) && (RxData >= 1U && RxData <= 8U)) ||
				((pRxPacket >= Serial_RxPacket_K[0]) && (RxData == 0U)))
			{
				Serial_RxPacket_K[pRxPacket + 1U] = RxData;
				pRxPacket++;
				RxChecksum ^= RxData;
				if (pRxPacket >= VISION_MAX_DIGITS)
				{
					RxState = 3;
				}
			}
			else
			{
				vision_error_count++;
				RxState = (RxData == VISION_FRAME_HEAD) ? 1 : 0;
			}
		}
		/* State 3: receive and verify XOR checksum. */
		else if (RxState == 3)
		{
			if (RxData == RxChecksum)
			{
				RxState = 4;
			}
			else
			{
				vision_error_count++;
				RxState = (RxData == VISION_FRAME_HEAD) ? 1 : 0;
			}
		}
		/* State 4: receive frame tail 0x5B, then publish this complete result. */
		else if (RxState == 4)
		{
			if (RxData == VISION_FRAME_TAIL)
			{
				vision_count = Serial_RxPacket_K[0];
				for (i = 0; i < vision_count; i++)
				{
					vision_digits[i] = Serial_RxPacket_K[i + 1U];
				}
				vision_frame_count++;
				vision_rx_flag = 1;
				Serial_RxFlag_K = 1;
				RxState = 0;
			}
			else
			{
				vision_error_count++;
				RxState = (RxData == VISION_FRAME_HEAD) ? 1 : 0;
			}
		}

		USART_ClearITPendingBit(USART2, USART_IT_RXNE);
	}
}
