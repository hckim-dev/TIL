# \[STM32\] 타이머 구조 분석: SR, CCR부터 PWM 출력 설정

> 날짜: 2026-07-22
> 원본 노션: [링크](https://app.notion.com/p/STM32-SR-CCR-PWM-3a51d46c18fc802b89b4e1687ae8627d)

<!-- notion-page-id: 3a51d46c18fc802b89b4e1687ae8627d -->
<!-- notion-title: "[STM32] 타이머 구조 분석: SR, CCR부터 PWM 출력 설정" -->

---

<a id="notion-3a51d46c18fc80e8990fc44c60bea26a"></a>

# ⏱️ STM32 Timer 핵심 개념 정리

<a id="notion-3a51d46c18fc80afb0dce0a522164059"></a>

### 📄 1. SR 레지스터 (Status Register)

> **타이머 상태 알림 레지스터**

- 타이머 내부에서 **특정 이벤트가 발생했음을 알리는 플래그 레지스터**입니다.
- 카운터 오버플로우(카운팅 완료), 채널별 Capture/Compare 이벤트가 일어날 때 해당 비트가 `1`로 세팅됩니다.
- 이 플래그를 통해 **인터럽트를 발생**시키거나, 소프트웨어에서 처리 완료 여부를 확인합니다.

<a id="notion-3a51d46c18fc80318031ec8b2d92f384"></a>

### 🔀 2. TIMx Multi-Channel (4개 채널)

> **하나의 타이머로 다양한 동작 수행**

- 하나의 타이머 하드웨어 블록(TIMx) 내부에 독립적인 4개의 입출력 채널(CH1 \~ CH4)이 존재합니다.
- 각 채널을 서로 다른 GPIO 핀과 연결하여 **입력 캡처(Capture), 출력 비교(Compare), PWM 생성** 등의 동작을 독립적으로 동시에 수행할 수 있습니다.

<a id="notion-3a51d46c18fc807dbce5f9e1a361e964"></a>

### 📌 3. Timer Output 핀 &amp; CCR 레지스터

> **주파수 펄스 출력의 핵심 요소**

- 타이머 카운터($CNT$) 값과 $CCR$ 레지스터 값을 실시간으로 비교하여 **Timer Output 지정 핀으로 펄스 신호를 출력**합니다.
- **`ARR`** <strong>(Auto-Reload Register)</strong>

  - 카운터가 어디까지 세고 0으로 리셋될지 정하는 값으로, 신호의 <strong>전체 주기(Frequency)</strong>를 결정
- **`CCR`** <strong>(Capture/Compare Register)</strong>

  - 카운트 중간에 파형 상태를 반전시킬 기준 값으로, <strong>Duty Ratio(High 구간 비율)</strong>를 결정

<a id="notion-3a51d46c18fc8023b709cfa762fc741f"></a>

### ⚖️ 4. Capture vs Compare 기능

> **신호 측정(입력) vs 파형 생성(출력)**

- **Input Capture (입력 캡처)**

  - 외부 핀으로 들어오는 신호의 Edge(Rising/Falling)를 감지하는 순간, <strong>현재</strong> **$CNT$** <strong>값을</strong> **$CCR$** <strong>레지스터에 즉시 저장</strong>합니다.
  - *주요 용도:* 외부 신호의 주파수 측정, 펄스 폭 측정, 이벤트 발생 시간 기록
- **Output Compare (출력 비교)**

  - 카운트 값($CNT$)이 사용자가 설정한 $CCR$ 값과 **일치할 때 핀의 출력 상태(High/Low)를 변경**합니다.
  - *주요 용도:* 정밀한 딜레이 생성, 특정 주파수의 파형(Square Wave) 생성

<a id="notion-3a51d46c18fc8049b139eb8522a13ac5"></a>

### 🌊 5. PWM (Pulse Width Modulation)

> **펄스 폭 변조 기술**

- 출력 비교(Compare) 기능을 응용하여 **주기는 일정하게 유지하면서 High 구간의 비율(Duty Cycle)만 조절**하는 출력 방식입니다.
- 전압의 평균값을 제어하는 효과가 있어 **DC 모터 속도 제어, LED 밝기 조절(Dimming), 오디오 신호 출력** 등에 핵심적으로 활용됩니다.

<a id="notion-3a51d46c18fc801c970ee4851c099350"></a>

### 6\. `CCMR2` (Capture/Compare Mode Register 2)

> **"채널 3과 채널 4의 동작 모드를 결정하는 설정 레지스터"**

타이머에는 총 4개의 채널이 있는데, `CCMR1`은 CH1/CH2를, <strong>`CCMR2`</strong>**는 CH3/CH4**의 동작 모드를 담당합니다.

- **핵심 역할:** 해당 채널을 입력(Capture)으로 쓸지, 출력(Compare/PWM)으로 쓸지 선택하고 세부 모드를 설정합니다.
- **주요 설정 값 (출력/PWM 모드 기준):**

  - **`CC3S`** <strong>/</strong> **`CC4S`** <strong>(Channel Selection):</strong> `00`으로 설정 시 출력 모드(Compare/PWM)로 지정됩니다.
  - **`OC3M`** <strong>/</strong> **`OC4M`** <strong>(Output Compare Mode):</strong> PWM 모드를 선택하는 비트입니다.

    - `110` (6): **PWM Mode 1** (CNT &lt; CCR 일 때 High, CNT ≥ CCR 일 때 Low)
    - `111` (7): **PWM Mode 2** (CNT &lt; CCR 일 때 Low, CNT ≥ CCR 일 때 High)
  - **`OC3PE`** <strong>/</strong> **`OC4PE`** <strong>(Preload Enable):</strong> CCR 레지스터의 섀도우 레지스터(Shadow Register)를 활성화하여, PWM 값을 변경할 때 주기가 끝나고 안전하게 반영되도록 합니다.

<a id="notion-3a51d46c18fc807ab9f4e1c3a65f50f0"></a>

### 7\. `CCER` (Capture/Compare Enable Register)

> **"채널별 신호의 출력을 켜고 끄며(Enable), 극성(High/Low)을 결정하는 레지스터"**

`CCMR` 레지스터에서 모드를 다 만들어두었더라도, `CCER` 레지스터에서 핀 출력을 활성화(Enable)해주지 않으면 외부 핀으로 신호가 나가지 않습니다. (모든 채널 CH1\~CH4을 이 레지스터 하나로 제어합니다)

- **핵심 역할:** 최종 파형의 **출력 허용(Enable)** 및 **신호 반전(Polarity)** 제어
- **주요 비트 (CH3 기준 예시):**

  - **`CC3E`** <strong>(Capture/Compare 3 Output Enable):</strong>

    - `0`: 채널 3 **출력 비활성화** (핀으로 신호 나가지 않음)
    - `1`: 채널 3 **출력 활성화** (PWM/파형이 GPIO 핀으로 실제 출력됨)
  - **`CC3P`** <strong>(Capture/Compare 3 Output Polarity):</strong>

    - `0`: **Active High** (기본 동작: High가 유효 신호)
    - `1`: **Active Low** (신호 반전: High/Low 신호가 서로 반대로 뒤집혀서 출력됨)

<a id="notion-3a51d46c18fc80f78827c88e25951d59"></a>

### 💡 한 줄 요약 &amp; 세팅 순서

1. <strong>`CCMR2`</strong>: "이 핀(CH3/CH4)은 **PWM Mode 1**으로 동작해라\!" (모드 정의)
2. <strong>`CCR3`</strong>: "HIGH 비율(Duty Ratio)은 50%로 해라\!" (값 설정)
3. <strong>`CCER`</strong>: "이제 스위치를 켜서(`CC3E = 1`) **실제 핀으로 PWM을 출력**해라\!" (최종 출력 켜기)

```c
#define TIM_TICK (20U)                  // 틱 단위 (us)
#define TIM_FREQ (1000000.0 / TIM_TICK) // 카운트 주파수 (Hz)
#define TIM_1MS_PLS (TIM_FREQ / 1000.0) // 1ms당 카운트 펄스 수
#define TIM_MAX_PLS (0xFFFFU)           // 16비트 타이머 최대 값

#define TIM5_PWM_FREQ (20000U)               // 목표 PWM 주파수 (20kHz)
#define TIM5_CNT_FREQ (TIM5_PWM_FREQ * 100U) // 카운트 클럭 (목표 주파수 * 100)
```

```c
volatile unsigned long Sys_Tick = 0; // 시스템 틱 카운터

// 타이머 모듈 전체 초기화
void Timer_Init(void)
{
    TIM2_Init();
    TIM4_Init();
    TIM5_Init();
}

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
