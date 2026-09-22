# \[STM32\] Peripheral 레퍼런스 노트

> 날짜: 2026-07-24
> 원본 노션: [링크](https://app.notion.com/p/STM32-Peripheral-3a71d46c18fc807ab94bfa5c3d16fab0)

<!-- notion-page-id: 3a71d46c18fc807ab94bfa5c3d16fab0 -->
<!-- notion-title: "[STM32] Peripheral 레퍼런스 노트" -->

---

<a id="notion-3a71d46c18fc8060abd9c1610cdba102"></a>

# \[LED\]

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

<a id="notion-3a71d46c18fc80e18237cf2d17fd1580"></a>

# \[Type Qualifier\]

\[volatile\]

1. \[ISR 공유 변수\] 메인 루프와 인터럽트 서비스 루틴(ISR)이 함께 쓰는 전역 변수
2. \[하드웨어 레지스터\] Memory-Mapped I/O (MMIO) 레지스터 주소 포인터
3. \[멀티태스킹 / DMA\] RTOS 태스크 간 공유 변수 및 DMA가 직접 변경하는 메모리

\[const\]

1. \[Flash 저장 (메모리 절약)\] 배열, 룩업 테이블(LUT) 등을 RAM 대신 Flash(ROM)에 배치할 때
2. \[포인터 매개변수 보호\] 함수 내부에서 읽기만 하고 입력 데이터를 수정하지 않음을 보장할 때
3. \[상수 정의 및 하드웨어 읽기\] 값이 절대 변경되면 안 되는 하드웨어 스펙/설정값을 정의할 때

<!-- list break -->

- <strong>`const int *ptr`</strong>: 포인터가 가리키는 '값(내용물)'을 변경할 수 없음 (`ptr = 10;` ❌)
- <strong>`int * const ptr`</strong>: 포인터 '주소 자체'를 변경할 수 없음 (`ptr = &other;` ❌)
- <strong>`const int * const ptr`</strong>: **주소와 값 둘 다** 변경할 수 없음 ❌

<a id="notion-3a71d46c18fc801bb18eec58fca5c0e9"></a>

# \[Key\]

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

<a id="notion-3a71d46c18fc8039ae34e5a0db99a478"></a>

# \[USART1\]

PA9 = TX, PA10 = RX

- **`SR`** <strong>Bit 7 (</strong><strong>`TXE`</strong><strong>, Transmit Data Register Empty)</strong>

  - `1`: DR 레지스터가 비어있어서 다음 데이터를 **쓸(Write) 수 있는 상태**
- **`SR`** <strong>Bit 5 (</strong><strong>`RXNE`</strong><strong>, Read Data Register Not Empty)</strong>

  - `1`: 수신 버퍼에 데이터가 도착해서 **읽을(Read) 수 있는 상태**

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

<a id="notion-3a71d46c18fc801888f4d1ffbaef79f1"></a>

# \[SysTick\]

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

<a id="notion-3a71d46c18fc8061b4c8dc3e4e419f14"></a>

# \[Timer\]

CR1 0번 레지스터(CEN): 1: On, 2: Off

Timeout 발생 시 SR의 0번 레지스터(UIF)가 1로 Set (수동으로 clear 해야 함)

\[TIM2\]

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
	TIM2->ARR = TIM2_MAX - 1U;
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

\[TIM4\]

```c
void TIM4_Repeat(int time)
{
	Macro_Set_Bit(RCC->APB1ENR, 2U);

	// TIM4 CR1: ARPE=0, down counter, repeat mode
	TIM4->CR1 = (0x1U << 4U) | (0x0U << 3U);
	// PSC(50KHz), ARR(reload 시 값) 설정
	TIM4->PSC = (unsigned int)(TIMXCLK / TIM2_FREQ + 0.5) - 1U;
	TIM4->ARR = (unsigned int)(TIM2_1ms_Pls * time) - 1U;
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

<a id="notion-3a71d46c18fc8064937bdd22b5fce566"></a>

# \[PWM\]

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

<a id="notion-3a71d46c18fc8096ae19ead8cc9199d7"></a>

# \[Interrupt\]

\[Key\]

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

\[UART\]

```c
volatile int Uart_Data_In = 0;
volatile unsigned char Uart_Data = 0;

char Uart2_Read_Byte(void)
{
  if (Uart_Data_In)
  {
    Uart_Data_In = 0;
    return (char)Uart_Data;
  }
  return 0;
}

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

\[TIMER\]

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

\[TIMER\_PRJ\]

```javascript
// TIM2 초기화 (롱클릭 타임아웃용, 단발성)
void TIM2_Init(void)
{
    Macro_Set_Bit(RCC->APB1ENR, 0U);     // TIM2 클럭 활성화
    TIM2->CR1 = (1U << 4U) | (1U << 3U); // Down-counter, One-Pulse Mode
    TIM2->PSC = (unsigned int)(TIMXCLK / (double)TIM_FREQ + 0.5) - 1U;
}

// TIM2 원샷 타이머 시작 (ms)
void TIM2_Start(int delay_ms)
{
    TIM2->ARR = (unsigned int)(TIM_1MS_PLS * delay_ms) - 1U;
    Macro_Set_Bit(TIM2->EGR, 0U);  // 레지스터 동기화
    Macro_Clear_Bit(TIM2->SR, 0U); // 펜딩 플래그 클리어

    NVIC_ClearPendingIRQ(TIM2_IRQn);
    Macro_Set_Bit(TIM2->DIER, 0U); // 인터럽트 허용
    NVIC_EnableIRQ(TIM2_IRQn);

    Macro_Set_Bit(TIM2->CR1, 0U); // 타이머 시작
}

// TIM2 정지 및 인터럽트 차단
void TIM2_Stop(void)
{
    Macro_Clear_Bit(TIM2->CR1, 0U);
    Macro_Clear_Bit(TIM2->DIER, 0U);
    NVIC_DisableIRQ(TIM2_IRQn);
}

// TIM4 초기화 (1ms 주기 시스템 틱)
void TIM4_Init(void)
{
    Macro_Set_Bit(RCC->APB1ENR, 2U);     // TIM4 클럭 활성화
    TIM4->CR1 = (1U << 4U) | (0U << 3U); // Down-counter, Repeat Mode
    TIM4->PSC = (unsigned int)(TIMXCLK / (double)TIM_FREQ + 0.5) - 1U;
    TIM4->ARR = (unsigned int)(TIM_1MS_PLS * 1) - 1U; // 1ms 주기 설정

    Macro_Set_Bit(TIM4->EGR, 0U);
    Macro_Clear_Bit(TIM4->SR, 0U);

    NVIC_ClearPendingIRQ(TIM4_IRQn);
    Macro_Set_Bit(TIM4->DIER, 0U); // 인터럽트 허용
    NVIC_EnableIRQ(TIM4_IRQn);

    Macro_Set_Bit(TIM4->CR1, 0U); // 타이머 시작
}
```

<a id="notion-3a91d46c18fc808c8ae2eab554dbfdde"></a>

## ⚡ 자동 Clear 해주는 레지스터 / 비트

읽기(Read)나 쓰기(Write) 동작을 수행하는 순간 하드웨어가 내부적으로 알아서 `0`으로 클리어해 주는 비트들입니다. (수동으로 0을 쓸 필요가 없음)

|  |  |  |
| --- | --- | --- |
| **레지스터 / 비트** | **설명** | **자동 Clear 조건 (트리거)** |
| **`USART->DR`** <strong>읽기</strong><br><br>(수신 시) | `USART_SR`의 **`RXNE`** (Bit 5) | `USART->DR` 레지스터에서 **데이터를 읽는 순간** `RXNE` 비트가 자동으로 `0`이 됨. |
| **`USART->DR`** <strong>쓰기</strong><br><br>(송신 시) | `USART_SR`의 **`TXE`** (Bit 7) | `USART->DR` 레지스터에 **데이터를 쓰면** `TXE` 비트가 자동으로 `0`이 됨. (데이터가 전송 완료되어 버퍼가 비면 하드웨어가 다시 `1`로 만듦) |
| **`TIMx->EGR`** | **`UG`** (Bit 0, Update Generation) | 소프트웨어로 `1`을 써서 이벤트를 발생시키면, 하드웨어가 레지스터 동기화를 마치고 <strong>즉시</strong> <strong>`0`</strong>**으로 자동 클리어**됨. |
| **`SysTick->CTRL`** | **`COUNTFLAG`** (Bit 16) | `SysTick->CTRL` 레지스터의 값을 **읽기(Read)만 하면** 자동으로 `0`으로 클리어됨. |
| **`SysTick->VAL`** | **`VAL`** (Current Value Register) | `SysTick->VAL = 0;` 처럼 **어떤 값이라도 쓰기(Write)하면** 현재 카운트 값이 `0`으로 자동 초기화 및 `COUNTFLAG`가 클리어됨. |

<a id="notion-3a91d46c18fc800db180cec7e3df79ac"></a>

## 🛠️ 수동으로 Clear 해줘야 하는 레지스터 / 비트

수동으로 Clear 해주지 않으면 **인터럽트가 무한 반복 호출**되거나 **타이머/스위치 상태가 계속 켜져 있어 시스템이 먹통**이 되는 핵심 레지스터들입니다.

|  |  |  |
| --- | --- | --- |
| **레지스터 / 비트** | **Clear 방법** | **안 헸을 때 발생하는 문제** |
| **`TIMx->SR`**<br><br>(<strong>`UIF`</strong>: Bit 0) | `Macro_Clear_Bit(TIMx->SR, 0U);`<br><br>또는 `TIMx->SR = ~1U;` | 타이머 ISR이 끝난 후 **무한으로 ISR에 다시 진입**하여 메인 루프가 멈춤. |
| **`EXTI->PR`**<br><br>(Pending Register) | **`EXTI->PR = (1U << Pin);`**<br><br>⚠️ **특이사항:** `1`을 써서 클리어함\! | 외부 스위치 인터럽트 ISR이 **무한 반복 실행**됨. |
| **`NVIC`** <strong>Pending</strong> | **`NVIC_ClearPendingIRQ(IRQn);`** | NVIC 차원에 대기 중인 인터럽트 플래그가 남아있어 불필요한 예외가 발생할 수 있음. |

<a id="notion-3a91d46c18fc801dadb6d30bb198096b"></a>

## 💡 3. ⭐ EXTI 레지스터의 특별한 클리어 규칙 (시험 단골\!)

보통 레지스터 비트를 끄기 위해서는 `0`을 적거나 `Macro_Clear_Bit`을 사용하지만, EXTI 펜딩 레지스터(`EXTI->PR`)는 동작 방식이 다릅니다.

- **`EXTI->PR`** <strong>클리어 방법:</strong>

  ```c
  // ❌ 틀린 방법: 0을 쓴다고 켜진 비트가 꺼지지 않음
  // EXTI->PR &= ~(1U << 13U);

  // ⭕ 정답 (Correct): 1을 덮어씌워야 하드웨어가 0으로 릴리즈함 (Write 1 to Clear)
  EXTI->PR = (1U << 13U);
  ```

  > **이유:** 하드웨어 가속 구조상 `1`을 써주어야 레지스터의 펜딩 락이 풀리도록 설계되어 있습니다.

<a id="notion-3a91d46c18fc805ca4c2dc2539e36543"></a>

## 📝 한눈에 암기하는 체크리스트

1. **타이머 ISR 내부:** `TIMx->SR` 0번 비트(`UIF`) 클리어했는가? (`Macro_Clear_Bit(TIM4->SR, 0U);`)
2. **외부 인터럽트(EXTI) ISR 내부:** `EXTI->PR`에 `1U << Pin`을 할당해 클리어했는가? (`EXTI->PR = (1U << 13U);`)
3. **NVIC 예외 처리:** `NVIC_ClearPendingIRQ(...)`를 호출해 주었는가?
4. **UART 수신:** `DR` 레지스터에서 값을 읽어서 `RXNE`가 자동으로 날아갔는가? (변수에 `DR` 값을 대입하면 끝\!)

<br>
