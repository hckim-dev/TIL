# \[AVR\] ATmega128A GPIO 제어의 모든 것: 저항 회로 설계부터 모듈화 FSM 패턴 구현까지

> 날짜: 2026-06-10
> 원본 노션: [링크](https://app.notion.com/p/AVR-ATmega128A-GPIO-FSM-37b1d46c18fc8026be3ad550e290a032)

<!-- notion-page-id: 37b1d46c18fc8026be3ad550e290a032 -->
<!-- notion-title: "[AVR] ATmega128A GPIO 제어의 모든 것: 저항 회로 설계부터 모듈화 FSM 패턴 구현까지" -->

---

<a id="notion-37b1d46c18fc8012903dc83185cfd1d7"></a>

# 📊 풀업(Pull-up) vs 풀다운(Pull-down) 저항 도식화

> 💡 **도식화를 보는 팁**
>
> - **VCC:** 5V (전원 높은 곳)
> - **GND:** 0V (바닥)
> - **입력 핀:** ATmega128A의 GPIO 핀 (데이터를 읽는 눈)
> - **R (저항):** 전기를 제어하는 밧줄 역할

<a id="notion-37b1d46c18fc80d49275ecf7d792ff63"></a>

## 🎈 1. 풀업(Pull-up) 저항 도식화

저항이 VCC(위쪽)에 매달려 있어서 신호를 위로 끌어올리는 구조입니다.

<a id="notion-37b1d46c18fc8086a177c20d68e38a54"></a>

### ① 스위치가 열려 있을 때 (대기 상태)

전류가 VCC에서 저항을 거쳐 **그대로 입력 핀**으로 들어갑니다. 스위치 쪽은 길이 끊겨 있어서 GND로 갈 수 없습니다.

```text
  VCC (5V)
    │
   [R]  <-- 저항이 여기에!
    │
    ├───────➡️ [ 입력 핀 ] ─── 💡 높은 전압 감지: Logic '1' (High)
    │
   ─── (스위치 열림: 👐)
    │
   GND (0V)
```

<a id="notion-37b1d46c18fc8015a5a1c963a4e240a4"></a>

### ② 스위치가 닫혀 있을 때 (버튼 누름)

스위치가 닫히면 전기는 저항이 없는 아주 편하고 넓은 길인 GND(바닥)로 쏟아져 내려갑니다. 입력 핀은 바닥(GND)과 완전히 연결된 상태가 됩니다.

```text
  VCC (5V)
    │
   [R]  (저항이 쇼트/과전류 방지)
    │
    ├───────➡️ [ 입력 핀 ] ─── 📉 바닥 전압 감지: Logic '0' (Low)
    │
   ─── (스위치 닫힘: 🛑)
    │
   GND (0V)  <-- 전기가 모두 일로 빠져나감
```

<a id="notion-37b1d46c18fc806eba03fb142c08bc74"></a>

## ⚓ 2. 풀다운(Pull-down) 저항 도식화

저항이 GND(아래쪽)에 매달려 있어서 신호를 바닥으로 붙잡아두는 구조입니다.

<a id="notion-37b1d46c18fc804e9c10d7fc196ea595"></a>

### ① 스위치가 열려 있을 때 (대기 상태)

위쪽 VCC가 끊겨 있어서 회로에 전기가 공급되지 않습니다. 입력 핀은 저항을 통해 바닥(GND)과 묶여 있습니다.

```text
  VCC (5V)
    │
   ─── (스위치 열림: 👐)
    │
    ├───────➡️ [ 입력 핀 ] ─── 📉 바닥 전압 감지: Logic '0' (Low)
    │
   [R]  <-- 저항이 여기에!
    │
   GND (0V)
```

<a id="notion-37b1d46c18fc80e5acb4cc390aad73c7"></a>

### ② 스위치가 닫혀 있을 때 (버튼 누름)

스위치가 닫히면 VCC에서 5V 전기가 힘차게 쏟아져 들어옵니다. 전기는 입력 핀으로 곧장 들어가고, 아래쪽 GND 방향은 저항(R)이 가로막고 있어서 전류가 과도하게 새는 것을 막아줍니다.

```text
  VCC (5V)  <-- 5V 전기 돌입!
    │
   ─── (스위치 닫힘: 🛑)
    │
    ├───────➡️ [ 입력 핀 ] ─── 💡 높은 전압 감지: Logic '1' (High)
    │
   [R]  (GND로 전기가 다 도망가지 못하게 막아줌)
    │
   GND (0V)
```

<a id="notion-37b1d46c18fc808bbc69ced2e72ca532"></a>

## 📌 한눈에 보는 작동 결과 요약

|  |  |  |  |
| --- | --- | --- | --- |
| **방식** | **저항의 위치** | **스위치 안 누를 때 (Default)** | **스위치 누를 때 (Active)** |
| **🎈 풀업 (Pull-up)** | 입력 핀과 **VCC** 사이 | **`1`** <strong>(High)</strong> | **`0`** <strong>(Low)</strong> |
| **⚓ 풀다운 (Pull-down)** | 입력 핀과 **GND** 사이 | **`0`** <strong>(Low)</strong> | **`1`** <strong>(High)</strong> |

<br>

<a id="notion-37b1d46c18fc803fb479f0f4cd422595"></a>

# 🤖 시스템 설계의 나침반: FSM (유한 상태 기계)

> 💡 **한 줄 요약:** 시스템이 가질 수 있는 상태들의 시나리오를 미리 정해두고, 이벤트(입력)에 따라 정해진 상태로만 움직이게 만드는 설계 지도입니다.

<a id="notion-37b1d46c18fc80ebae76d7e2863f02eb"></a>

## 1\. 직관적인 비유: 지하철 개찰구 (Turnstile)

FSM을 설명할 때 전 세계 전산학 교과서에서 가장 먼저 드는 예시가 바로 **지하철 개찰구**입니다. 개찰구의 상태는 딱 2가지로 제한(유한)되어 있습니다.

1. **🔒 닫힘(Locked) 상태 (기본 상태)**

   - 사람이 밀어도? ➡️ 안 열림 (상태 유지)
   - 💳 카드를 태그하면(이벤트)? ➡️ **\[열림\] 상태로 전환**
2. **🔓 열림(Unlocked) 상태**

   - 카드를 또 태그하면? ➡️ 무시하고 계속 열림 (상태 유지)
   - 사람이 밀고 지나가면(이벤트)? ➡️ **다시 \[닫힘\] 상태로 전환**

개찰구는 절대로 '반쯤 열린 상태'나 '동시에 닫히고 열린 상태'가 될 수 없습니다. 오직 **정해진 상태** 안에서 **정해진 이벤트**가 일어날 때만 움직입니다.

<a id="notion-37b1d46c18fc8003936be35c9069e7ab"></a>

## 🛠️ 2. 왜 써야 하나요? (if-else 지옥 탈출하기)

우리가 방금 선언한 **스위치 4개와 LED 8개 회로**로 프로젝트를 만든다고 가정해 봅시다.

스위치를 누를 때마다 `[모두 깜빡임]` ➡️ `[순차 점등]` ➡️ `[숨쉬기 모드]` ➡️ `[OFF]` 순서로 모드가 바뀌어야 합니다.

<a id="notion-37b1d46c18fc8007a79ac065562df916"></a>

### ❌ FSM을 안 쓴 나쁜 코드 (스파게티 코드)

변수 몇 개로 땜질하다 보면 코드가 아래처럼 괴물이 됩니다.

```cpp
if (button_pressed && mode == 1 && sub_mode == 0) {
    // ... 복잡해지면 내가 뭘 짜고 있는지 길을 잃음 ...
} else if (mode == 2 || is_led_on == false) {
    // 버그 발생 시 디버깅이 불가능에 가까워짐
}
```

<a id="notion-37b1d46c18fc80939577fd12bbe46322"></a>

### ⭕ FSM을 쓴 예쁜 코드 (C언어 표준 스타일)

C언어의 `enum` (열거형 자료형)과 <strong>`switch-case`</strong>**문**의 조합이 바로 FSM 구현의 정석입니다

```cpp
// 1. 상태(State)의 종류를 명확하게 정의함 (유한한 상태)
typedef enum {
    STATE_LED_OFF = 0,
    STATE_LED_ALL_ON,
    STATE_LED_FLICKER,
    STATE_LED_FLOW
} LedState_e;

LedState_e current_state = STATE_LED_OFF; // 처음 시작 상태

void update_fsm(void){
    // 2. 현재 상태에 따라서만 작동 제어
    switch (current_state)
    {
        case STATE_LED_OFF:
            PORTA = 0x00;
            if (BUTTON0_PRESSED) current_state = STATE_LED_ALL_ON; // 상태 전환(Transition)
            break;

        case STATE_LED_ALL_ON:
            PORTA = 0xFF;
            if (BUTTON0_PRESSED) current_state = STATE_LED_FLICKER; // 다음 상태로
            break;

        case STATE_LED_FLICKER:
            // 깜빡이는 코드 구현
            if (BUTTON0_PRESSED) current_state = STATE_LED_FLOW;
            break;

        case STATE_LED_FLOW:
            // 물 흐르듯 켜지는 코드 구현
            if (BUTTON0_PRESSED) current_state = STATE_LED_OFF; // 다시 처음으로
            break;
    }
}
```

<a id="notion-37b1d46c18fc80d0adf0cd055a0dccf5"></a>

## 🚀 3. 내 개인 프로젝트에 어떻게 녹여낼 수 있을까?

아까 안드로이드와 ATmega128A를 블루투스로 연결해 **스마트 도어락**이나 **스마트 가전**을 만들면 좋겠다고 이야기 나눴었죠? 그때 이 FSM이 기가 막히게 들어갑니다.

- **ATmega128A의 상태 가질 수 있는 예시:**

  `[대기 상태(IDLE)]` ➡️ (앱에서 비밀번호 전송 수신) ➡️ `[인증 중(AUTH)]` ➡️ (일치하면) ➡️ `[문 열림(OPEN)]` ➡️ (3초 타이머 종료) ➡️ `[다시 경보/대기(IDLE)]`
- **안드로이드 앱의 상태 가질 수 있는 예시:**

  `[블루투스 미연결]` ➡️ (연결 버튼 클릭) ➡️ `[연결 중]` ➡️ (연결 성공) ➡️ `[제어 대시보드 화면]`

이렇게 설계를 미리 스케치북에 동그라미와 화살표(상태 천이도)로 그려두고 코딩을 시작하면, 코드가 꼬일 수가 없고 줄 수도 획기적으로 줄어듭니다.

<a id="notion-37b1d46c18fc805e9976fdcbbc06ecab"></a>

## 📌 한 줄 요약

> <strong>"FSM은 기계의 행동 시나리오다\!</strong> <strong>`enum`</strong><strong>으로 상태 이름을 지어주고,</strong> <strong>`switch-case`</strong>**문으로 구역을 나눠 관리하면 복잡한 IoT 시스템도 버그 없이 깔끔하게 통제할 수 있다."**

<br>

<a id="notion-37b1d46c18fc808d9316c96a2229abb3"></a>

# ⏱️ 입력 처리의 두 축: 폴링(Polling) vs 인터럽트(Interrupt)

> 💡 **한 줄 요약**
>
> - **폴링 (Polling):** CPU가 주기적으로 "혹시 이벤트 일어났니?" 하고 **계속 물어보며** 확인하는 방식
> - **인터럽트 (Interrupt):** CPU는 자기 할 일 하고 있다가, 이벤트가 발생하면 하드웨어가 "저기요\!" 하고 **CPU를 가로막아** 알려주는 방식

<a id="notion-37b1d46c18fc80f58d95e8ad0980e154"></a>

## 📦 1. 일상 비유로 단번에 이해하기: 택배 기다리기

우리가 쿠팡에서 택배를 주문하고 기다리는 상황으로 비유해 보겠습니다.

<a id="notion-37b1d46c18fc80489ea0dddcb324ef60"></a>

### 🔄 ① 폴링 (Polling) 방식

- 택배가 언제 올지 몰라 불안해서 **3분마다 한 번씩 현관문을 열고 나가서 확인**합니다.
- **현실:** 문 앞에 가보는 동안에는 방 청소(내 할 일)를 제대로 할 수 없고, 계속 왔다 갔다 하느라 다리도 아프고 체력(CPU 자원)이 낭비됩니다. 택배가 안 왔더라도 이 짓을 무한 반복합니다.

<a id="notion-37b1d46c18fc80f19702cff532523942"></a>

### ⚡ ② 인터럽트 (Interrupt) 방식

- 현관문에 초인종(Interrupt Pin)을 달아두고, 나는 방에서 편하게 유튜브를 보거나 공부(내 할 일)를 합니다.
- 택배 기사님이 오셔서 초인종을 **"딩동(Event)"** 누르면, 하던 일을 잠깐 멈추고 나가서 택배를 받은 뒤(인터럽트 서비스 루틴), 다시 방으로 들어와 아까 보던 유튜브를 이어서 봅니다.
- **현실:** 내 할 일에 100% 집중할 수 있고 체력(CPU 자원) 낭비가 전혀 없습니다.

<a id="notion-37b1d46c18fc809c95afcf912bd5837d"></a>

## 💻 2. C언어 코드로 보는 차이점

우리가 아까 짰던 **스위치 입력 코드**에 대입해 보면 두 방식의 소스 코드 구조가 완전히 달라집니다.

<a id="notion-37b1d46c18fc80f099fde648f15196f2"></a>

### ❌ 폴링 방식의 코드 구조 (`while`문 뺑뺑이)

CPU가 무한 루프 안에서 스위치 상태를 감시하느라 다른 일을 전혀 못 합니다. 만약 `_delay_ms(1000)` 같은 딜레이가 중간에 걸려있으면, 그 1초 동안 스위치를 눌렀다 떼도 CPU가 인식하지 못하고 씹히는 치명적인 문제가 있습니다.

```cpp
int main(void){
    button_init();

    while(1) {
        // CPU가 쉴 새 없이 계속 확인 ("눌렸냐? 눌렸냐?")
        if (BUTTON_PIN & (1 << BUTTON_0_PIN)) {
            button_process_fsm();
        }

        // 만약 여기에 긴 작업이 있다면 스위치 입력이 씹힙니다.
        do_something_heavy();
    }
}
```

<a id="notion-37b1d46c18fc8033846ccb7ac97004cb"></a>

### ⭕ 인터럽트 방식의 코드 구조 (ISR 활용)

`main` 함수의 `while`문은 텅 비워두거나 다른 메인 로직을 돌립니다. 스위치가 눌리는 순간 하드웨어 신호가 CPU의 목덜미를 잡고 <strong>`ISR`</strong>**이라고 불리는 특수 함수**로 강제 강림시킵니다.

```cpp
// 스위치가 눌리는 순간 자동으로 호출되는 '초인종 전담 함수'
ISR(INT0_vect)
{
    // 스위치가 눌렸을 때 할 일만 딱 하고 메인으로 돌아감
    button_process_fsm();
}

int main(void){
    interrupt_init(); // 초인종(외부 인터럽트) 활성화 설정

    while(1) {
        // CPU는 스위치 신경 끄고 완전히 자기 할 일만 편하게 함
        display_lcd_screen();
        run_main_motor();
    }
}
```

<a id="notion-37b1d46c18fc80e488f7fd975e33fd34"></a>

## 📊 3. 한눈에 비교하는 장단점 테이블 (노션 정리용)

|  |  |  |
| --- | --- | --- |
| **비교 항목** | **🔄 폴링 (Polling)** | **⚡ 인터럽트 (Interrupt)** |
| **작동 원리** | 무한 루프(`while`)로 끊임없이 감시 | 하드웨어 신호(`ISR`)로 비동기적 알림 |
| **CPU 효율** | **낮음** (감시하느라 자원 낭비 심함) | **높음** (이벤트가 없을 땐 자원 소모 0%) |
| **반응 속도** | 딜레이 코드 등이 있으면 **반응이 느리거나 씹힘** | 신호가 들어오는 즉시 반응하므로 **매우 빠름** |
| **구현 난이도** | 단순함 (`if`문 몇 줄이면 끝) | 복잡함 (레지스터 설정 및 `ISR` 예외처리 필요) |
| **추천 상황** | 센서 값이 언제나 일정하게 계속 들어올 때 | 스위치, 비상 정지 버튼, 통신 데이터 수신 등 **언제 일어날지 모르는 긴급 상황** |

<a id="notion-37b1d46c18fc80498dbdecca5309ee7e"></a>

## 📌 한 줄 요약

> **"폴링은 5분 대기조처럼 계속 문 앞을 지키며 확인하는 노가다 방식이고, 인터럽트는 하던 일 편하게 하다가 벨소리(초인종)가 울리면 나가는 스마트한 방식이다. 임베디드의 꽃은 인터럽트다\!"**

<br>

\[main.c\]

```c
/**
* @file    main.c
* @brief   상태 기반 다중 스위치 입력 및 LED 시나리오 제어 메인 루프
*/

// 시스템 주파수 정의
#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#include <avr/io.h>      // AVR 입출력 레지스터 정의 (PORTA, DDRA 등)
#include <util/delay.h>  // 시간 지연 함수 라이브러리 (_delay_ms 등)

#include "button.h"
#include "led.h"

int main(void)
{
	init_button();
	init_led();
	
	while (1)
	{
		if (get_button(BUTTON_0, BUTTON_0_PIN))
		{
			on_button_0_press();
		}
		else if (get_button(BUTTON_1, BUTTON_1_PIN))
		{
			on_button_1_press();
		}
		else if (get_button(BUTTON_2, BUTTON_2_PIN))
		{
			on_button_2_press();
		}
		else if (get_button(BUTTON_3, BUTTON_3_PIN))
		{
			on_button_3_press();
		}
	}
}
```

\[button.h\]

```c
/**
* @file    button.h
* @brief   풀다운 스위치 입력 제어 매크로 및 함수 선언
* @date    2026-06-10
* @author  kccistc
*/

#ifndef BUTTON_H_
#define BUTTON_H_

#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#include <avr/io.h>
#include <util/delay.h>

/* ========================================================================== */
/* 스위치(BUTTON) 하드웨어 제어 정의                                          */
/* ========================================================================== */

/* 1. 사용할 포트 및 레지스터 지정 */
#define BUTTON_DDR          DDRD            /* 버튼 방향 설정 레지스터 */
#define BUTTON_PIN          PIND            /* 버튼 입력 상태 읽기 레지스터 (5V:1, 0V:0) */
#define BUTTON_COUNT        4               /* 연결된 총 버튼 개수 */

/* 2. 물리적인 하드웨어 핀 번호 매핑 (PORTD.3 ~ PORTD.6) */
#define BUTTON_0_PIN        3               /* 첫 번째 스위치 연결 핀 */
#define BUTTON_1_PIN        4               /* 두 번째 스위치 연결 핀 */
#define BUTTON_2_PIN        5               /* 세 번째 스위치 연결 핀 */
#define BUTTON_3_PIN        6               /* 네 번째 스위치 연결 핀 */

/* 3. 소스 코드에서 사용할 가상 인덱스 번호 (ID) */
#define BUTTON_0            0
#define BUTTON_1            1
#define BUTTON_2            2
#define BUTTON_3            3

/* 4. 스위치 작동 논리 상태 정의 (풀다운 구조이므로 Active-High) */
#define BUTTON_PRESS        1               /* 버튼을 누른 상태 (High) */
#define BUTTON_RELEASE      0               /* 버튼을 뗀 상태 (Low) */

/* --- 외부 공개 함수 원형 선언 --- */
void init_button(void);
int get_button(int button_num, int button_pin);

#endif /* BUTTON_H_ */
```

\[button.c\]

```c
/**
* @file    button.c
* @brief   채터링 방지 및 스위치 입력 상태 머신 구현
*/

#include "button.h"

void init_button(void)
{
	BUTTON_DDR &= ~((1 << BUTTON_0_PIN) | (1 << BUTTON_1_PIN) | (1 << BUTTON_2_PIN) | (1 << BUTTON_3_PIN));
}

int get_button(int button_num, int button_pin)
{
	/* 함수가 끝나도 이전 상태를 유지하는 정적 지역 배열 변수 */
	static int button_status[BUTTON_COUNT] = {
		BUTTON_RELEASE, BUTTON_RELEASE, BUTTON_RELEASE, BUTTON_RELEASE
	};
	
	int current_state;
	
	/* 1. 하드웨어 핀 읽기 후 자릿수 1의 자리로 정렬 */
	current_state = (BUTTON_PIN & (1 << button_pin)) >> button_pin;

	/* 2. 상태 머신 기반 디바운싱 및 엣지 디텍션 */
	/* Case 1: 스위치가 처음 눌렸을 때 */
	if (current_state == BUTTON_PRESS && button_status[button_num] == BUTTON_RELEASE)
	{
		_delay_ms(15); /* 전압 출렁임 노이즈 대기 */
		button_status[button_num] = BUTTON_PRESS;
		return 0;
	}
	/* Case 2: 누르고 있다가 떼어지는 순간 (Falling Edge 클릭 인정) */
	else if (current_state == BUTTON_RELEASE && button_status[button_num] == BUTTON_PRESS)
	{
		button_status[button_num] = BUTTON_RELEASE;
		_delay_ms(15); /* 뗄 때 발생하는 노이즈 대기 */
		return 1; /* 완전히 1번 클릭됨을 반환 */
	}
	
	return 0;
}
```

\[led.h\]

```c
/**
* @file    led.h
* @brief   LED 저수준 제어 및 시나리오 제어 함수 선언
*/

#ifndef LED_H_
#define LED_H_

#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#include <avr/io.h>
#include <util/delay.h>

void init_led(void);
void led_all_on(void);
void led_all_off(void);
void led_right_on(void);
void led_left_on(void);
void led_odd_on(void);
void led_even_on(void);

void on_button_0_press(void);
void on_button_1_press(void);
void on_button_2_press(void);
void on_button_3_press(void);

#endif /* LED_H_ */
```

\[led.c\]

```c
/**
* @file    led.c
* @brief   LED 패턴 매핑 및 가상 시나리오 상태 머신 구현
*/

#include "led.h"

int button_0_state = 0;
int button_1_state = 0;

void init_led(void)
{
	DDRA = 0xFF;  /* PORTA 출력 모드 */
	PORTA = 0x00; /* 초기 상태 All Off */
}

void led_all_on(void)
{
	PORTA = 0xFF;
}

void led_all_off(void)
{
	PORTA = 0x00;
}

void led_right_on(void)
{
	PORTA = 0x0F;
}

void led_left_on(void)
{
	PORTA = 0xF0;
}

void led_odd_on(void)
{
	int temp = 0x00;
	
	for (int i = 0; i < 8; i++)
	{
		if (i % 2 == 1)
		{
			temp |= (1 << i);
		}
	}
	
	PORTA = temp;
}

void led_even_on(void)
{
	int temp = 0x00;
	
	for (int i = 0; i < 8; i++)
	{
		if (i % 2 == 0)
		{
			temp |= (1 << i);
		}
	}
	
	PORTA = temp;
}

void on_button_0_press(void)
{
	button_0_state = (button_0_state + 1) % 4;
	
	switch(button_0_state)
	{
		case 0:
		led_all_off();
		break;
		case 1:
		led_all_on();
		break;
		case 2:
		led_right_on();
		break;
		case 3:
		led_left_on();
		break;
	}
}

void on_button_1_press(void)
{
	button_1_state = (button_1_state + 1) % 4;
	
	switch(button_1_state)
	{
		case 0:
		led_all_off();
		break;
		case 1:
		led_odd_on();
		break;
		case 2:
		led_even_on();
		break;
		case 3:
		led_all_on();
		break;
	}
}

void on_button_2_press(void)
{
	
}

void on_button_3_press(void)
{
	button_0_state = 0;
	button_1_state = 0;
	led_all_off();
}
```

<br>
