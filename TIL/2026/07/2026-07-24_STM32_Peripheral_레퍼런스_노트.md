# STM32 Peripheral 레퍼런스 노트

> 날짜: 2026-07-24
> 원본 노션: [링크](https://app.notion.com/p/STM32-Peripheral-3a71d46c18fc807ab94bfa5c3d16fab0)

---

# [LED]

```c
#include "device_driver.h"

// LED GPIO (PA5) 초기화
void LED_Init(void)
{
    // 1. GPIOA 클럭 활성화
    Macro_Set_Bit(RCC->AHB1ENR, 0U);

    // 2. PA5 Output Mode 설정 (MODER[11:10] = 01)
    Macro_Write_Block(GPIOA->MODER, 0x3U, 0x1U, 10U);

    // 3. Output Type -> Push-Pull 설정 (0: push-pull, 1: open-drain)
    Macro_Clear_Bit(GPIOA->OTYPER, 5U);

    // 6. 초기 상태: LED OFF
    LED_Off();
}

// LED 켜기 (Active High 기준: High 출력)
void LED_On(void)
{
    Macro_Set_Bit(GPIOA->ODR, 5U);
}

// LED 끄기 (Low 출력)
void LED_Off(void)
{
    Macro_Clear_Bit(GPIOA->ODR, 5U);
}

// LED 상태 반전 (토글)
void LED_Toggle(void)
{
    Macro_Invert_Bit(GPIOA->ODR, 7U);
}
```

# [Type Qualifier]

[volatile]

1. [ISR 공유 변수] 메인 루프와 인터럽트 서비스 루틴(ISR)이 함께 쓰는 전역 변수
1. [하드웨어 레지스터] Memory-Mapped I/O (MMIO) 레지스터 주소 포인터
1. [멀티태스킹 / DMA] RTOS 태스크 간 공유 변수 및 DMA가 직접 변경하는 메모리
[const]

1. [Flash 저장 (메모리 절약)] 배열, 룩업 테이블(LUT) 등을 RAM 대신 Flash(ROM)에 배치할 때
1. [포인터 매개변수 보호] 함수 내부에서 읽기만 하고 입력 데이터를 수정하지 않음을 보장할 때
1. [상수 정의 및 하드웨어 읽기] 값이 절대 변경되면 안 되는 하드웨어 스펙/설정값을 정의할 때
- const int *ptr: 포인터가 가리키는 '값(내용물)'을 변경할 수 없음 (ptr = 10; ❌)
- int * const ptr: 포인터 '주소 자체'를 변경할 수 없음 (ptr = &other; ❌)
- const int * const ptr: 주소와 값 둘 다 변경할 수 없음 ❌
# [Key]

```c
int is_pressed;
int is_locked = 0;

// PC13 스위치 (Active Low) 초기화
void Key_Init(void)
{
    // 1. GPIOC 클럭 활성화
    Macro_Set_Bit(RCC->AHB1ENR, 2U);

    // 2. PC13 핀을 Input Mode로 설정
    Macro_Write_Block(GPIOC->MODER, 0x3U, 0x0U, 26U);
    
    // 3. [선택] 내부 풀업 저항 설정
    Macro_Write_Block(GPIOA->PUPDR, 0x3U, 0x1U, 26U);
}

for (;;)
{
		is_pressed = Macro_Check_Bit_Clear(GPIOC->IDR, USER_KEY_PIN);

		if (!is_locked && is_pressed)
		{
			Macro_Invert_Bit(GPIOA->ODR, LED_PIN);
			is_locked = 1;
		}
		else if (is_locked && !is_pressed)
		{
			is_locked = 0;
		}
}
```

# [USART1]

PA9 = TX, PA10 = RX

- SR Bit 7 (TXE, Transmit Data Register Empty)
- SR Bit 5 (RXNE, Read Data Register Not Empty)
```c
void Uart2_Send_Byte(char data)
{
    // 개행 문자가 들어오면 '\r' (CR)을 먼저 전송해 주는 센스
    if (data == '\n')
    {
        while (!Macro_Check_Bit_Set(USART2->SR, 7U)) ; // TXE 비트(7) 기다림
        USART2->DR = 0x0D;
    }

    while (!Macro_Check_Bit_Set(USART2->SR, 7U)) ;     // TXE 비트(7) 기다림
    USART2->DR = data;
}

void Uart2_Send_String(const char *str)
{
    while (*str != '\0')
    {
        Uart2_Send_Byte(*str++);
    }
}

char Uart2_Receive_Byte(void)
{
    while (!Macro_Check_Bit_Set(USART2->SR, 5U)) ;     // RXNE 비트(5) 기다림
    return (char)USART2->DR;
}
```

# [SysTick]

```c
void SysTick_Run(unsigned int msec)
{
	// Timer 설정 : 인터럽트 발생 안함, clock source는 HCLK/8, Timer 정지
	// Enable: [0번 비트] 1: ON, 2: Off
	// CLKSOURCE: [2번 비트] 0: AHB clock/8, 1: AHB clock
	// COUNTFLAG: [16번 비트] 1: Timeout, 0: X
	Macro_Write_Block(SysTick->CTRL, 0x7, 0x0, 0U);

	// 주어진 msec 값 만큼의 msec를 count하는 초기값 설정 (LOAD)
	SysTick->LOAD = (int)((HCLK / 8. / 1000.) + 0.5) * msec;

	// VAL 레지스터 값 초기화(0) 및 COUNTFLAG Clear
	SysTick->VAL = 0;

	// Timer Start (시작이 되면 자동으로 LOAD의 값을 VAL로 가져간다)
	Macro_Set_Bit(SysTick->CTRL, 0U);
}

int SysTick_Check_Timeout(void)
{
	// Timer의 Timeout이 발생하면 참(1)리턴, 아니면 거짓(0) 리턴
	return Macro_Check_Bit_Set(SysTick->CTRL, 16U);
}

unsigned int SysTick_Get_Time(void)
{
	// Timer의 현재 count 값 리턴
	return SysTick->VAL;
}

unsigned int SysTick_Get_Load_Time(void)
{
	// Timer에 설정된 초기값을 리턴
	return SysTick->LOAD;
}

void SysTick_Stop(void)
{
	// Timer Stop
	Macro_Clear_Bit(SysTick->CTRL, 0U);
}
```

# [Timer]

CR1 0번 레지스터(CEN): 1: On, 2: Off

Timeout 발생 시 SR의 0번 레지스터(UIF)가 1로 Set (수동으로 clear 해야 함)

[TIM2]

```c
#define TIM2_TICK (20U)					 // usec
#define TIM2_FREQ (1000000. / TIM2_TICK) // Hz
#define TIM2_1ms_Pls (TIM2_FREQ / 1000.) // 1ms
#define TIM2_MAX (0xFFFFU)

void TIM2_Stopwatch_Start(void)
{
	Macro_Set_Bit(RCC->APB1ENR, 0U);

	// TIM2 CR1 설정: down count, one pulse
	TIM2->CR1 = (0x1U << 3U) | (0x1U << 4U);
	// PSC 초기값 설정 => 20usec tick이 되도록 설계 (50KHz)
	// 분주는 N + 1이 설정되므로 -1 해줘야함.
	TIM2->PSC = (unsigned int)(TIMXCLK / TIM2_FREQ + 0.5) - 1U;
	// ARR 초기값 설정 => 최대값 0xFFFF 설정
	TIM2->ARR = TIM2_MAX;
	// UG 이벤트 발생
	Macro_Set_Bit(TIM2->EGR, 0U);
	// TIM2 start
	Macro_Set_Bit(TIM2->CR1, 0U);
}

unsigned int TIM2_Stopwatch_Stop(void)
{
	unsigned int time;

	// TIM2 stop
	Macro_Clear_Bit(TIM2->CR1, 0U);
	// CNT 초기 설정값 (0xffff)와 현재 CNT의 펄스수 차이를 구하고
	// 그 펄스수 하나가 20usec이므로 20을 곱한값을 time에 저장
	time = (TIM2_MAX - TIM2->CNT) * TIM2_TICK;
	// 계산된 time 값을 리턴(단위는 usec)
	return time;
}

void TIM2_Delay(int time)
{
	Macro_Set_Bit(RCC->APB1ENR, 0U);

	TIM2->CR1 = (0x1U << 4U) | (0x1U << 3U);
	TIM2->PSC = (unsigned int)(TIMXCLK / TIM2_FREQ + 0.5) - 1;

	unsigned int pls = TIM2_1ms_Pls * time;
	unsigned int q = pls / TIM2_MAX;
	unsigned int r = pls % TIM2_MAX;
	unsigned int i;

	for (i = 0U; i < q; i++)
	{
		TIM2->ARR = TIM2_MAX - 1U;

		Macro_Set_Bit(TIM2->EGR, 0U);
		Macro_Clear_Bit(TIM2->SR, 0U);
		Macro_Set_Bit(TIM2->CR1, 0U);

		while (!Macro_Check_Bit_Set(TIM2->SR, 0U))
			;
	}

	if (r > 0U)
	{

		TIM2->ARR = r - 1U;

		Macro_Set_Bit(TIM2->EGR, 0U);
		Macro_Clear_Bit(TIM2->SR, 0U);
		Macro_Set_Bit(TIM2->CR1, 0U);

		while (!Macro_Check_Bit_Set(TIM2->SR, 0U))
			;
	}

	// TIM2 Stop
	Macro_Clear_Bit(TIM2->CR1, 0U);
}
```

[TIM4]

```c
void TIM4_Repeat(int time)
{
	Macro_Set_Bit(RCC->APB1ENR, 2U);

	// TIM4 CR1: ARPE=0, down counter, repeat mode
	TIM4->CR1 = (0x1U << 4U) | (0x0U << 3U);
	// PSC(50KHz), ARR(reload 시 값) 설정
	TIM4->PSC = (unsigned int)(TIMXCLK / TIM2_FREQ + 0.5) - 1;
	TIM4->ARR = (unsigned int)(TIM2_1ms_Pls * time);
	// UG 이벤트 발생
	Macro_Set_Bit(TIM4->EGR, 0U);
	// Update Interrupt Pending Clear
	Macro_Clear_Bit(TIM4->SR, 0U);
	// TIM4 start
	Macro_Set_Bit(TIM4->CR1, 0U);
}

int TIM4_Check_Timeout(void)
{
	// 타이머가 timeout 이면 1 리턴, 아니면 0 리턴
	int is_timeout = Macro_Check_Bit_Set(TIM4->SR, 0U);
	if (is_timeout)
	{
		Macro_Clear_Bit(TIM4->SR, 0U);
	}
	return is_timeout;
}

void TIM4_Stop(void)
{
	Macro_Clear_Bit(TIM4->CR1, 0U);
}

void TIM4_Change_Value(int time)
{
	TIM4->ARR = 50 * time;
}
```

# [PWM]

```c
#define TIM3_FREQ (8000000)				// Hz
#define TIM3_TICK (1000000 / TIM3_FREQ) // usec
#define TIME3_PLS_OF_1ms (1000 / TIM3_TICK)

void TIM3_Out_Init(void)
{
	Macro_Set_Bit(RCC->AHB1ENR, 1);
	Macro_Set_Bit(RCC->APB1ENR, 1);

	Macro_Write_Block(GPIOB->MODER, 0x3, 0x2, 0);  // PB0 => ALT
	Macro_Write_Block(GPIOB->AFR[0], 0xf, 0x2, 0); // PB0 => AF02

	Macro_Write_Block(TIM3->CCMR2, 0xff, 0x60, 0);
	TIM3->CCER = (0 << 9) | (1 << 8);
}

void TIM3_Out_PWM_Generation(unsigned short freq, int duty)
{
	unsigned int arr_val;

	// Timer 주파수가 TIM3_FREQ가 되도록 PSC 설정
	TIM3->PSC = (unsigned int)(((double)TIMXCLK / TIM3_FREQ) + 0.5) - 1U;
	// 요청한 주파수가 되도록 ARR 설정
	arr_val = (unsigned int)(((double)TIM3_FREQ / freq) + 0.5) - 1U;
	TIM3->ARR = arr_val;
	// duty %가 되도록 설정
	TIM3->CCR3 = (unsigned int)(arr_val * (duty / 100U) + 0.5);
	// Manual Update(UG 발생)
	Macro_Clear_Bit(TIM3->EGR, 0U);
	// Down Counter, Repeat Mode, Timer Start
	TIM3->CR1 = (0x1U << 4U) | (0x0U << 3U) | (0x1U << 0U);
}

void TIM3_Out_Stop(void)
{
	Macro_Clear_Bit(TIM3->CR1, 0);
}
```

```c
// TIM5 초기화 (모터 PWM 제어용)
void TIM5_Init(void)
{
    Macro_Set_Bit(RCC->AHB1ENR, 0U); // GPIOA 클럭 활성화
    Macro_Set_Bit(RCC->APB1ENR, 3U); // TIM5 클럭 활성화

    // PA0, PA1 핀 설정 (AF 모드 / AF02: TIM5)
    Macro_Write_Block(GPIOA->MODER, 0xFU, 0xAU, 0U);
    Macro_Write_Block(GPIOA->AFR[0], 0xFFU, 0x22U, 0U);

    TIM5->CR1 = (1U << 4U) | (0U << 3U); // Down-counter, Repeat Mode

    // PWM 주파수 설정
    TIM5->PSC = (unsigned int)(TIMXCLK / TIM5_CNT_FREQ) - 1U;
    TIM5->ARR = (unsigned int)(TIM5_CNT_FREQ / TIM5_PWM_FREQ) - 1U;

    // CH1, CH2 PWM Mode 1 및 Preload 활성화
    Macro_Write_Block(TIM5->CCMR1, 0xFFFFU, 0x6868U, 0U);

    // CH1, CH2 출력 활성화
    Macro_Set_Bit(TIM5->CCER, 0U);
    Macro_Set_Bit(TIM5->CCER, 4U);

    // 동기화 및 타이머 시작
    Macro_Set_Bit(TIM5->EGR, 0U);
    Macro_Set_Bit(TIM5->CR1, 0U);
}

// TIM5 CH1, CH2 PWM Duty 비 설정 (0~100%)
void TIM5_Set_Duty(int ch1_duty, int ch2_duty)
{
    TIM5->CCR1 = (unsigned int)(TIM5->ARR * (ch1_duty / 100.0));
    TIM5->CCR2 = (unsigned int)(TIM5->ARR * (ch2_duty / 100.0));
}
```

# [Interrupt]

[Key]

```c
void Key_ISR_Enable(int en)
{
	if (en)
	{
		Macro_Set_Bit(RCC->AHB1ENR, 2);
		Macro_Write_Block(GPIOC->MODER, 0x3, 0x0, 26);

		// SYSCFG 장치 Clock On
		Macro_Set_Bit(RCC->APB2ENR, 14U);
		// PC13을 EXTI 13의 소스가 되도록 설정
		// PA13, PB13, PC13 등 여러 13번 핀들 중 사용할 PC13 핀 설정
		// 0000: A, 0001: B, 0010: C, 0011: D, 0100: E, 0111: H
		Macro_Write_Block(SYSCFG->EXTICR[3], 0xF, 0x2, 4U);
		// EXTI 13을 Falling Edge Trigger로 설정
		// 풀업 스위치는 평소 high로 있으니까 Falling Edge 때 감지
		Macro_Set_Bit(EXTI->FTSR, 13U);
		// EXTI 13 Pending Clear
		// 노이즈 떄문에 비트가 1로 이미 올라가 있을 수 있어, 클리어 작업 수행
		EXTI->PR = (1U << 13U);
		// NVIC EXTI15_9 Interrupt Pending Clear
		// EXTI 모듈 레지스터뿐만 아니라 NVIC 차원에 대기 중이던 것도 클리어
		NVIC_ClearPendingIRQ(EXTI15_10_IRQn);
		// EXTI 13 Interrupt Enable
		// EXTI 모듈 내부의 차단막(Mask)을 열어줌
		Macro_Set_Bit(EXTI->IMR, 13U);
		// NVIC EXTI15_9 Interrupt Enable
		// NVIC을 열어줌으로써 Interrupt Enable
		NVIC_EnableIRQ(EXTI15_10_IRQn);
	}
	else
	{
		NVIC_DisableIRQ(EXTI15_10_IRQn);
	}
}

extern volatile int Key_Pressed;

void EXTI15_10_IRQHandler(void)
{
	Key_Pressed = 1;

	EXTI->PR = (0x1U << 13U);
	NVIC_ClearPendingIRQ(EXTI15_10_IRQn);
}
```

[UART]

```c
void Uart2_RX_Interrupt_Enable(int en)
{
  if (en)
  {
    // USART2 RX Interrupt Enable
    Macro_Set_Bit(USART2->CR1, 5U);
    // NIVC Pending Clear
    NVIC_ClearPendingIRQ(USART2_IRQn);
    // NVIC Interrupt Enable
    NVIC_EnableIRQ(USART2_IRQn);
  }
  else
  {
    Macro_Clear_Bit(USART2->CR1, 5);
    NVIC_DisableIRQ(USART2_IRQn);
  }
}

extern volatile int Uart_Data_In;
extern volatile unsigned char Uart_Data;

void USART2_IRQHandler(void)
{
		// 수신된 데이터는 Uart_Data에 저장
		Uart_Data = USART2->DR;
		// Uart_Data_In Flag Setting
		Uart_Data_In = 1;
		// NVIC Pending Clear
		NVIC_ClearPendingIRQ(USART2_IRQn);
}
```

[TIMER]

```c
void TIM4_Repeat_Interrupt_Enable(int en, int time)
{
	if (en)
	{
		// TIM4 Clock On
		Macro_Set_Bit(RCC->APB1ENR, 2U);

		TIM4->CR1 = (1 << 4) | (0 << 3);
		TIM4->PSC = (unsigned int)(TIMXCLK / (double)TIM4_FREQ + 0.5) - 1;
		TIM4->ARR = TIME4_PLS_OF_1ms * time;
		Macro_Set_Bit(TIM4->EGR, 0);

		// TIM4 Pending Clear
		Macro_Clear_Bit(TIM4->SR, 0U);
		// NVIC Pending Clear
		NVIC_ClearPendingIRQ(TIM4_IRQn);

		// TIM4 Interrupt Enable
		Macro_Set_Bit(TIM4->DIER, 0U);
		// NVIC Interrupt Enable
		NVIC_EnableIRQ(TIM4_IRQn);

		// TIM4 Start
		Macro_Set_Bit(TIM4->CR1, 0U);
	}
	else
	{
		NVIC_DisableIRQ(TIM4_IRQn);
		Macro_Clear_Bit(TIM4->CR1, 0U);
		Macro_Clear_Bit(TIM4->DIER, 0U);
	}
}

extern volatile int TIM4_Expired;

void TIM4_IRQHandler(void)
{
	// TIM4 Interrupt Pending Clear
	Macro_Clear_Bit(TIM4->SR, 0U);
	// NVIC Pending Clear
	NVIC_ClearPendingIRQ(TIM4_IRQn);

	TIM4_Expired = 1;
}
```

