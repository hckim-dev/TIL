# \[STM32\] Interrupt 제어

> 날짜: 2026-07-23
> 원본 노션: [링크](https://app.notion.com/p/STM32-Interrupt-3a61d46c18fc80429654d835f382db67)

<!-- notion-page-id: 3a61d46c18fc80429654d835f382db67 -->
<!-- notion-title: "[STM32] Interrupt 제어" -->

---

<a id="notion-3a61d46c18fc8087a168fc5e16effa4d"></a>

## 💡 폴링(Polling) vs 인터럽트(Interrupt)

|  |  |  |
| --- | --- | --- |
| **구분** | **폴링 (Polling)** | **인터럽트 (Interrupt)** |
| **비유** | 편지가 왔는지 대문 앞 우체통을 **매초 확인하러 감** | 우편배달부가 **벨을 누르면(알림)** 그때 나감 |
| **CPU 사용** | `for(;;)` 루프 안에서 비트 상태를 계속 체크 (CPU 낭비) | 메인 루프는 다른 일을 하거나 **Sleep 모드로 대기** |
| **반응 속도** | 메인 루프에 딜레이(`TIM4_Delay`)가 있으면 반응이 늦어짐 | <strong>즉시(수십</strong> **$ns$** <strong>내)</strong> 메인 루프를 멈추고 반응함 |

<a id="notion-3a61d46c18fc808b9630da43ed4b213e"></a>

## ⚙️ 인터럽트 동작 과정 (Hardware Mechanism)

버튼을 누르거나 타이머 시간이 완료되는 등 이벤트가 발생했을 때 하드웨어 내부에서 일어나는 과정입니다.

**1\. 이벤트 발생 (Event Trigger):**

하드웨어 신호.

외부 스위치 신호(Falling/Rising Edge)나 타이머 Overflow 등이 발생하여 인터럽트 펜딩 플래그(Pending Flag)가 `1`로 셋 됩니다.

**2\. NVIC 우선순위 판단:**

Interrupt Controller.

ARM Cortex-M의 핵심 중추인 \*\*NVIC(Nested Vectored Interrupt Controller)\*\*가 해당 인터럽트가 활성화되어 있는지, 현재 실행 중인 코드보다 우선순위가 높은지 판단합니다.

**3\. Context Save (레지스터 자동 백업):**

하드웨어 자동 처리.

CPU가 현재 하던 일(Main 루프의 주소, 레지스터 `R0~R3`, `R12`, `LR`, `PC`, `xPSR`)을 스택(Stack) 메모리에 **하드웨어적으로 자동으로 저장**합니다.

**4\. ISR (Interrupt Service Routine) 실행:**

소프트웨어 핸들러.

벡터 테이블(Vector Table)을 참조하여 약속된 핸들러 함수(예: `EXTI9_5_IRQHandler()`)로 자프하여 코드를 실행합니다. **(이때 펜딩 플래그를 반드시 클리어해줘야 함\!)**

**5\. Context Restore 및 복귀:**

하드웨어 자동 처리.

ISR 실행이 끝나면 스택에 보관해둔 레지스터들을 복원하고, 원래 멈췄던 메인 루프 위치로 돌아가 하던 일을 계속합니다.

<a id="notion-3a61d46c18fc80348745c66dd1ecc136"></a>

## 🧠 핵심 개념 4가지

<a id="notion-3a61d46c18fc8000803cded2c1a3ee48"></a>

### 1\. NVIC (Nested Vectored Interrupt Controller)

- ARM Cortex-M 내부에 존재하는 **인터럽트 총괄 관리자**입니다.
- 모든 주변장치(GPIO, TIM, UART)의 인터럽트는 NVIC를 거쳐 CPU로 들어갑니다.
- **중첩(Nested) 지원:** 실행 중인 인터럽트보다 더 높은 우선순위의 인터럽트가 오면 새 인터럽트를 먼저 처리합니다.

<a id="notion-3a61d46c18fc806cb511e04319f8f785"></a>

### 2\. EXTI (Extended Interrupt Controller)

- GPIO 핀의 신호 변화(Falling/Rising Edge)를 감지하여 NVIC로 전달해 주는 **외부 인터럽트 모듈**입니다.
- 예: `PC7` 핀의 신호가 High에서 Low로 떨어질 때(Falling Edge) EXTI7 라인이 트리거됩니다.

<a id="notion-3a61d46c18fc806192d3fc6e36a6f966"></a>

### 3\. ISR (Interrupt Service Routine / 핸들러)

- 인터럽트가 발생했을 때 **자동으로 실행되는 전용 함수**입니다.
- `startup_stm32f4xx.s` 같은 스타트업 파일에 함수 이름(예: `EXTI9_5_IRQHandler`)이 미리 정해져 있어서, C 코드에서 동일한 이름으로 함수를 만들면 알아서 연결됩니다.

<a id="notion-3a61d46c18fc80e89450c932cf924d7a"></a>

### 4\. `volatile` 키워드

- 메인 루프와 ISR 사이에서 공유하는 변수에는 반드시 `volatile`을 붙여야 합니다.
- 컴파일러가 "어? 메인 루프에서는 이 변수를 바꾸는 코드가 없네?" 하고 변수를 레지스터에 캐싱(최적화)해 버리는 버그를 방지해 줍니다.

<a id="notion-3a61d46c18fc80d59714e80ea58e2aa3"></a>

## 🚨 ISR(인터럽트 함수) 작성 시 3대 절대 수칙

> <strong>1\. 지연 함수(</strong><strong>`TIM4_Delay`</strong><strong>)나 무거운 연산(</strong><strong>`printf`</strong><strong>)을 절대 넣지 말 것\!</strong>
>
> ISR 내부가 길어지면 다른 중요한 인터럽트나 전체 시스템 딜레이가 꼬입니다. ISR 안에서는 <strong>플래그(</strong><strong>`flag = 1`</strong><strong>)만 켜고 즉시 탈출</strong>하는 것이 정석입니다.
>
> **2\. 인터럽트 펜딩 플래그(Pending Flag)를 반드시 클리어할 것\!**
>
> 플래그를 안 지우면 ISR이 끝나는 순간 "어? 아직 인터럽트 남았네?" 하고 **무한 반복해서 ISR만 실행**되어 MCU가 먹통이 됩니다.
>
> <strong>3\. 공유 변수는</strong> **`volatile`** <strong>키워드 사용하기\!</strong>
>
> `static volatile int g_key_flag = 0;` 처럼 선언해야 최적화 오류를 막을 수 있습니다.

<a id="notion-3a61d46c18fc807590a0feade618348a"></a>

## 🌟 핵심 3대 함수 (가장 자주 쓰임)

실무 프로젝트에서 가장 빈번하게 사용되는 3가지 필수 함수입니다.

<a id="notion-3a61d46c18fc80a097fec256656b8492"></a>

### 1\. `NVIC_EnableIRQ()` ⭐⭐⭐ \[매우 중요\]

- **역할:** 특정 인터럽트를 최종 활성화(Enable)시킵니다.
- **설명:** 타이머나 EXTI 같은 주변장치 레지스터에서 인터럽트를 켜더라도, **NVIC 수준에서 이 함수를 호출해주지 않으면 CPU로 인터럽트 신호가 전달되지 않습니다.**
- **사용 예시:**

  ```c
  NVIC_EnableIRQ(EXTI9_5_IRQn); // PC7 버튼 인터럽트 허용
  NVIC_EnableIRQ(TIM5_IRQn);    // TIM5 타이머 인터럽트 허용
  ```

<a id="notion-3a61d46c18fc80d0bcf2faeb24b6facf"></a>

### 2\. `NVIC_DisableIRQ()` ⭐⭐⭐ \[매우 중요\]

- **역할:** 특정 인터럽트를 비활성화(Disable)시킵니다.
- **설명:** 더 이상 인터럽트를 받지 않아야 하는 상황(예: 임계 영역 접근, 모터 비상 정지 후 인터럽트 차단)에서 사용합니다.
- **사용 예시:**

  ```c
  NVIC_DisableIRQ(EXTI9_5_IRQn); // 스위치 인터럽트 차단
  ```

<a id="notion-3a61d46c18fc8099ad57dbe15ddca5e1"></a>

### 3\. `NVIC_ClearPendingIRQ()` ⭐⭐⭐ \[매우 중요\]

- **역할:** 대기 중인(Pending) 인터럽트 플래그를 강제로 클리어(제거)합니다.
- **설명:** 인터럽트가 발생하면 NVIC 내부 'Pending 레지스터'에 깃발이 꼽힙니다. <strong>인터럽트를 활성화(</strong><strong>`EnableIRQ`</strong><strong>)하기 전이나 ISR 처리 직후 남아있는 잔여 플래그에 의해 의도치 않은 인터럽트가 바로 터지는 것을 방지</strong>할 때 반드시 사용해야 하는 매우 중요한 함수입니다.
- **사용 예시:**

  ```c
  // EXTI 초기화 설정 시, 기존에 남아있던 오작동 플래그를 미리 청소
  NVIC_ClearPendingIRQ(EXTI9_5_IRQn);
  NVIC_EnableIRQ(EXTI9_5_IRQn);
  ```

<a id="notion-3a61d46c18fc80a6b9f8f49a58329473"></a>

## 🛠️ 그 외 주요 NVIC CMSIS 함수들

|  |  |
| --- | --- |
| **함수명** | **역할 및 특징** |
| **`NVIC_SetPriority(IRQn_Type IRQn, uint32_t priority)`** | 특정 인터럽트의 **우선순위(Priority)를 지정**합니다. (숫자가 작을수록 높은 우선순위) |
| **`NVIC_GetPriority(IRQn_Type IRQn)`** | 해당 인터럽트에 설정된 우선순위 값을 읽어옵니다. |
| **`NVIC_SetPendingIRQ(IRQn_Type IRQn)`** | \*\*소프트웨어적으로 강제로 인터럽트를 발생(트리거)\*\*시킵니다. (테스트용) |
| **`NVIC_GetPendingIRQ(IRQn_Type IRQn)`** | 해당 인터럽트가 대기(Pending) 상태인지 확인합니다. (반환값 `0` 또는 `1`) |

<a id="notion-3a61d46c18fc8072a4ede79c466cbede"></a>

## 💡 실무 적용 종합 코드 예시

외부 스위치 인터럽트(`EXTI9_5_IRQn`)를 안전하게 초기화하고 활성화하는 정석 흐름입니다.

```c
void Key_Interrupt_Init(void){
    // ... GPIO 및 EXTI 레지스터 설정 코드 ...

    // 1. 스위치 인터럽트 우선순위 설정 (0 ~ 15 중 1번으로 지정)
    NVIC_SetPriority(EXTI9_5_IRQn, 1U);

    // 2. ⭐ [중요] 기존 대기 플래그가 남아있다면 깔끔히 청소
    NVIC_ClearPendingIRQ(EXTI9_5_IRQn);

    // 3. ⭐ [중요] NVIC 인터럽트 최종 활성화
    NVIC_EnableIRQ(EXTI9_5_IRQn);
}
```

<a id="notion-3a61d46c18fc80fb8ba6fcaba84e42ac"></a>

# ⚡ 외부 인터럽트 (EXTI: Extended Interrupt) 정리

> **💡 한 줄 요약**
>
> GPIO 핀의 전기적 신호 변화(Rising/Falling Edge)를 하드웨어적으로 감지하여, CPU가 즉시 정해진 함수(ISR)를 실행하도록 알림을 보내는 외부 인터럽트 모듈.

<a id="notion-3a61d46c18fc80b58adec87b1a09bbcf"></a>

## 1\. EXTI 기본 개념 및 특징

- **EXTI (Extended Interrupt and Event Controller)**

  - GPIO 핀의 신호 상태 변화를 감지하여 NVIC(인터럽트 컨트롤러)로 전달하는 하드웨어 블록.
  - CPU가 메인 루프에서 `for(;;)`로 버튼 상태를 계속 감시하는 **폴링(Polling) 방식의 자원 낭비를 해결**.
- **트리거 조건 (Trigger Edge)**

  - **Rising Edge (상승 모서리):** $0\text{V} \rightarrow 3.3\text{V}$ (버튼을 뗄 때, Pull-up 기준)
  - **Falling Edge (하강 모서리):** $3.3\text{V} \rightarrow 0\text{V}$ (버튼을 누를 때, Pull-up 기준)
  - **Both Edge (양방향):** 누를 때와 뗄 때 모두 발생

<a id="notion-3a61d46c18fc80e8b9fede7e968129e6"></a>

## 2\. GPIO 핀과 EXTI 라인 매핑 (SYSCFG)

STM32는 핀 번호와 EXTI 라인 번호가 **1:1로 매핑**됩니다.

- `PA0`, `PB0`, `PC0` $\rightarrow$ 모두 **`EXTI0`** <strong>라인 공유</strong>
- `PA7`, `PB7`, `PC7` $\rightarrow$ 모두 **`EXTI7`** <strong>라인 공유</strong>

> ⚠️ **중요 제약 사항**
>
> 동일한 핀 번호를 가진 GPIO는 **동시에 EXTI로 사용할 수 없습니다.**
>
> (예: `PA7`과 `PC7`을 동시에 외부 인터럽트로 사용 불가 $\rightarrow$ **SYSCFG 레지스터**로 둘 중 하나만 선택해야 함)

<a id="notion-3a61d46c18fc80aeb96ec6dfc68497ca"></a>

## 3\. EXTI 라인과 NVIC ISR 함수 매핑

EXTI 라인은 NVIC 핸들러 함수와 다음과 같이 묶여서 연결됩니다.

|  |  |  |
| --- | --- | --- |
| **EXTI 라인** | **NVIC ISR 함수 이름** | **비고** |
| **EXTI0 \~ EXTI4** | `EXTI0_IRQHandler()` \~ `EXTI4_IRQHandler()` | 라인당 전용 핸들러 1개씩 존재 |
| **EXTI5 \~ EXTI9** | `EXTI9_5_IRQHandler()` | 5개 라인이 **1개의 함수 공유** |
| **EXTI10 \~ EXTI15** | `EXTI15_10_IRQHandler()` | 6개 라인이 **1개의 함수 공유** |

> 💡 **Tip:** `EXTI9_5_IRQHandler`처럼 공용 함수를 쓸 때는 함수 내부에서 **"몇 번 라인에서 인터럽트가 터졌는지"** 레지스터 플래그(`PR` 비트)를 직접 체크해야 합니다.

<a id="notion-3a61d46c18fc80338841c0571f24ebec"></a>

## 4\. EXTI 인터럽트 신호 흐름

```text
[ GPIO 핀 입력 (PC7) ]
       │
       ▼
[ SYSCFG 멀티플렉서 ] ──> PC7을 EXTI7 라인에 연결
       │
       ▼
[ EXTI 트리거 설정 ]  ──> Falling Edge / Rising Edge 지정
       │
       ▼ (Pending Flag Set: PR7 = 1)
[ NVIC 컨트롤러 ]     ──> EXTI9_5_IRQn 우선순위 판별 및 Enable 체크
       │
       ▼
[ CPU / ISR 실행 ]    ──> EXTI9_5_IRQHandler() 호출
                           ⚠️ (반드시 ISR 내부에서 PR7 플래그 클리어!)
```

<a id="notion-3a61d46c18fc804c878fffedadd23af7"></a>

## 5\. EXTI 실전 C 언어 코드 (PC7 스위치 기준)

<a id="notion-3a61d46c18fc8093b44bef8ec8d091d7"></a>

### 📌 1) EXTI 및 SYSCFG 초기화 (`key.c`)

```c
#include "device_driver.h"

void Key_EXTI_Init(void){
    // 1. GPIOC 및 SYSCFG 클럭 활성화
    Macro_Set_Bit(RCC->AHB1ENR, 2U);  // GPIOC (PC7)
    Macro_Set_Bit(RCC->APB2ENR, 14U); // SYSCFG 활성화 (EXTI 매핑용)

    // 2. PC7 입력 모드 & 내부 풀업 저항 설정
    Macro_Write_Block(GPIOC->MODER, 0x3U, 0x0U, 14U); // Input Mode
    Macro_Write_Block(GPIOC->PUPDR, 0x3U, 0x1U, 14U); // Pull-up

    // 3. EXTI7 라인에 PC7 연결 (SYSCFG->EXTICR[1] 조작)
    // EXTICR[1]의 비트 12~15를 0x2(GPIOC)로 설정
    Macro_Write_Block(SYSCFG->EXTICR[1], 0xFU, 0x2U, 12U);

    // 4. EXTI7 트리거 조건 설정 (Falling Edge: 버튼 눌림 감지)
    Macro_Set_Bit(EXTI->FTSR, 7U);   // Falling Trigger 활성화
    Macro_Clear_Bit(EXTI->RTSR, 7U); // Rising Trigger 비활성화

    // 5. EXTI7 인터럽트 마스크 해제 (Unmask)
    Macro_Set_Bit(EXTI->IMR, 7U);

    // 6. NVIC 설정
    NVIC_SetPriority(EXTI9_5_IRQn, 2U);   // 우선순위 설정 (숫자가 작을수록 높음)
    NVIC_ClearPendingIRQ(EXTI9_5_IRQn);   // 잔여 펜딩 플래그 청소
    NVIC_EnableIRQ(EXTI9_5_IRQn);         // NVIC 인터럽트 최종 활성화
}
```

<a id="notion-3a61d46c18fc800684c3fc62f27dd525"></a>

### 📌 2) ISR 핸들러 구현 (`main.c` 또는 `key.c`)

```c
// 공유 변수는 반드시 volatile 선언!
volatile int g_key_pressed_flag = 0;

/**
 * @brief EXTI Line [9:5] 통합 인터럽트 핸들러
 */
void EXTI9_5_IRQHandler(void){
    // EXTI7 라인(PC7)에서 인터럽트가 발생했는지 확인
    if (Macro_Check_Bit_Set(EXTI->PR, 7U))
    {
        // 1. ⭐ [필수] 펜딩 비트 클리어 (STM32 EXTI는 1을 써야 클리어됨!)
        Macro_Set_Bit(EXTI->PR, 7U);

        // 2. 수행할 최소한의 동작 (플래그만 변경)
        g_key_pressed_flag = 1;
    }
}
```

<a id="notion-3a61d46c18fc8029afcdfe4966d28031"></a>

## 🚨 EXTI 작성 시 3대 주의사항 (면접/실무 필수)

> **PR(Pending Register) 비트 클리어 방식:**<br>    ◦ STM32의 EXTI PR 레지스터는 `0`을 쓰는 게 아니라 \*\*`1`을 써야 비트가 `0`으로 클리어(W1C: Write 1 to Clear)\*\*됩니다.<br>    ◦ 플래그를 안 지우면 ISR이 무한 루프로 재귀 호출되어 시스템이 멈춥니다.**ISR 내부 지연 금지:**<br>    ◦ ISR 안에서 `TIM4_Delay()`나 `printf()` 같은 길고 무거운 코드를 넣으면 안 됩니다.<br>    ◦ **ISR에서는 플래그만 켜고 탈출**한 뒤, 실제 작업은 `main()` 루프에서 처리합니다.**채터링(Chattering / Bouncing) 대책:**<br>    ◦ 스위치를 누를 때 하드웨어 접점이 미세하게 떨려 EXTI가 수십 번 연속 터질 수 있습니다.<br>    ◦ ISR 진입 시 인터럽트를 잠시 끄거나(`NVIC_DisableIRQ`), 소프트웨어 타이머로 디바운싱을 처리해야 합니다.

\[key.c\]

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

void EXTI15_10_IRQHandler(void)
{
	// KEY Pressed 메시지 인쇄
	printf("KEY Pressed");
	// KEY(EXTI) Pending Clear
	// Pending을 수동으로 클리어해줘야 함(Interrupt 무한루프 방지)
	EXTI->PR = (1U << 13U);
	// NVIC Pending Clear
	// EXTI 뿐만아니라 NVCI Pending 도 클리어 해줘야 함
	NVIC_ClearPendingIRQ(EXTI15_10_IRQn);
}
```
