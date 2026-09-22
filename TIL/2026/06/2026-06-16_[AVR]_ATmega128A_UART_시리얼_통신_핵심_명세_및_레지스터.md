# \[AVR\] ATmega128A UART 시리얼 통신 핵심 명세 및 레지스터

> 날짜: 2026-06-16
> 원본 노션: [링크](https://app.notion.com/p/AVR-ATmega128A-UART-3801d46c18fc807da598dc0942103520)

<!-- notion-page-id: 3801d46c18fc807da598dc0942103520 -->
<!-- notion-title: "[AVR] ATmega128A UART 시리얼 통신 핵심 명세 및 레지스터" -->

---

<a id="notion-3811d46c18fc80ca9e64d2ef18382f6b"></a>

# 📟 UART 시리얼 통신 핵심 요약 노트

<a id="notion-3811d46c18fc80319e6bc9aeae5b9cb0"></a>

## 1\. UART란 무엇인가?

- **정의:** **U**niversal **A**synchronous **R**eceiver-**T**ransmitter (범용 비동기 송수신기)
- **역할:** 임베디드 시스템(MCU)에서 컴퓨터나 다른 장치와 데이터를 주고받을 때 사용하는 가장 기본적이고 널리 쓰이는 **직렬(Serial) 통신** 규격입니다.
- **직렬(Serial) 통신이란?** 데이터를 한 번에 여러 비트씩 보내는 병렬(Parallel) 방식과 달리, **선 한 가닥을 통해 데이터를 1비트씩 차례대로 줄 세워서 보내는 방식**입니다.

<a id="notion-3811d46c18fc80c99312e0f7ef218ac0"></a>

## 2\. UART의 핵심 특징 3가지

- 통신할 때 동기화를 위한 **클록(Clock) 신호선이 없습니다.**

<a id="notion-3811d46c18fc8041bf5bccd2478ba011"></a>

### ① 비동기 방식 (Asynchronous)

- 클록선이 없는 대신, 송신측과 수신측이 "우리 1초에 몇 비트씩 주고받자\!"라고 미리 약속(Baud Rate)을 하고 통신을 시작합니다.

<a id="notion-3811d46c18fc8050a3eddad1a8568d3d"></a>

### ② 최소한의 핀(선) 연결

- 데이터를 보내는 선 Tx(Transmit)와 받는 선 <strong>Rx(Receive)</strong>, 그리고 기준 전압을 맞춰줄 GND(Ground)선까지 **딱 3개의 선**만 있으면 통신이 가능합니다.
- ⚠️ **주의 (교차 연결):** 장치끼리 연결할 때는 내 Tx가 상대방의 Rx로, 내 Rx가 상대방의 Tx로 엇갈리게(Cross) 연결해야 합니다.

<a id="notion-3811d46c18fc803c8738d8514b12576f"></a>

### ③ 1:1 통신 (Peer-to-Peer)

- I2C나 SPI 통신처럼 여러 장치를 버스 형태로 묶을 수 없고, **오직 1개의 마스터와 1개의 슬레이브가 1:1로만 통신**할 수 있습니다.

<a id="notion-3811d46c18fc80ee8111deb8c1bd7aff"></a>

## 3\. UART 데이터 프레임 (Data Frame) 구조

클록선이 없는데 수신측은 데이터가 언제 들어올지 어떻게 알까요? 바로 데이터 앞뒤에 "시작"과 "끝"을 알리는 특별한 신호를 붙여서 보냅니다. 이를 **데이터 프레임**이라고 합니다.

1. **Idle 상태 (대기 상태):** 데이터를 보내지 않을 때 신호선은 항상 **High(5V 또는 3.3V)** 상태를 유지합니다.
2. **Start Bit (시작 비트):** 데이터를 보내기 시작하는 순간, 선을 **Low(0V)로 뚝 떨어뜨려** 수신측에 "이제 데이터 들어간다\! 준비해\!"라고 신호를 줍니다. (무조건 1비트 부피)
3. **Data Bits (데이터 비트):** 실제 전송할 데이터입니다. 보통 **8비트(1바이트)** 크기를 사용하며, 가벼운 데이터는 5\~7비트, 많게는 9비트까지 설정 가능합니다. (보낼 때는 LSB, 즉 낮은 자릿수 비트부터 전송합니다.)
4. **Parity Bit (패리티 비트 - 선택 사항):** 데이터가 오다가 깨졌는지 검사하는 에러 체크용 1비트입니다. (실무에서는 복잡해서 `None`, 즉 안 쓰는 경우가 많습니다.)
5. **Stop Bit (정지 비트):** 데이터 전송이 끝났음을 알리며 선을 다시 **High**로 올립니다. 보통 1비트 또는 2비트 폭을 사용합니다.

<a id="notion-3811d46c18fc80a5994bed1b8b0579e4"></a>

## 4\. 실무 필수 용어 정리

- **보레이트 (Baud Rate):** 1초 동안 전송되는 비트의 수(통신 속도)입니다. 단위는 `bps`(bits per second)를 씁니다.

  - *가장 많이 쓰는 표준 속도:* <strong>`9600 bps`</strong>, **`115200 bps`** (송수신 장치의 보레이트가 1Hz라도 어긋나면 글자가 완전히 깨지는 꽥꽥이 현상이 발생합니다.)
- **TTL 레벨 vs RS-232 레벨:** \* **TTL:** MCU(ATmega128A 등) 내부에서 쓰는 디지털 전압 레벨입니다. (`5V/3.3V = 1`, `0V = 0`)

  - **RS-232:** 컴퓨터 시리얼 포트나 옛날 장비에서 쓰던 레벨로, 노이즈에 강하게 하려고 먼 거리용 음양 전압을 씁니다. (`3V~-15V = 1`, `+3V~+15V = 0`)
  - ⚠️ 컴퓨터와 MCU를 그냥 선으로 연결하면 전압 차이 때문에 칩이 타버리므로, 중간에 **CP2102나 CH340 같은 USB-to-UART 컨버터 칩**을 거쳐서 컴퓨터 USB 포트에 꽂아야 합니다.

<br>

```c
/**
* @file    uart0.c
* @brief   UART0 초기화(9600bps, RX INT, TX Polling) 및 전송 구현
* @date    2026-06-16
* @author  kccistc
*/

#include "uart0.h"

/**
* @brief  UART0 초기화 함수
* - 속도: 9600bps (2배속 모드 모드 설정)
* - 데이터: 8비트, 패리티 없음, 정지 비트 1비트 (AVR 기본값 사양)
* - 송수신: 송신(TX) 및 수신(RX) 활성화
* - 인터럽트: 수신 완료(RX) 인터럽트 허용
*/
void UART0_init(void)
{
	/* 1. 보레이트 레이트 설정: 9600bps (16MHz, U2X0=1 기준 UBRR=207) */
	UBRR0H = 0x00;
	UBRR0L = 207;
	
	/* 2. UCSR0A: 2배속 모드 활성화 (U2X0 = 1) */
	UCSR0A |= 1 << U2X0;
	
	/* 3. UCSR0B: RX/TX 활성화 및 RX 완료 인터럽트 허용
	- RXEN0: 수신기 활성화
	- TXEN0: 송신기 활성화
	- RXCIE0: 수신 완료 인터럽트 켜기 */
	UCSR0B |= 1 << RXEN0 | 1 << TXEN0 | 1 << RXCIE0;
}

/**
* @brief  UART0로 1바이트를 전송하는 함수 (표준 출력 printf 연동 규격)
* @param  data   : 전송할 8비트 문자 데이터 (printf 엔진이 쪼개서 보내준 한 글자)
* @param  stream : 표준 출력 스트림 포인터 (fdev_setup_stream 연동용, 여기선 내부적으로 자동 처리됨)
* @return int    : 전송 성공 시 0을 반환 (표준 입출력 함수들의 정상 종료 약속)
*/
int UART0_transmit(char data, FILE *stream)
{
	/* UDRE0(UART Data Register Empty) 플래그 감시
	- UDR0 송신 버퍼가 비워질 때까지 (1이 될 때까지) while 루프로 대기합니다. */
	while (!(UCSR0A & (1 << UDRE0)));
	
	/* 하드웨어 버퍼에 데이터를 집어넣으면 즉시 송신선(TX)으로 쏴집니다. */
	UDR0 = data;
	
	return 0;
}
```

```c
FILE OUTPUT = FDEV_SETUP_STREAM(UART0_transmit, NULL, _FDEV_SETUP_WRITE);

stdout = &OUTPUT; // printf 가 동작할 수 있도록 stdout 을 설정
	
while (1)
{
	printf("Hello hckim\n");
	_delay_ms(1000);
}
```

<a id="notion-3811d46c18fc80c9be83ea2946dce47e"></a>

# 🗺️ UART 레지스터 이름 완벽 해부 노트

UART 통신을 하려면 MCU 내부에 <strong>\[속도 조절 담당\]</strong>, <strong>\[환경 설정 담당\]</strong>, \[데이터 보관함\]이라는 3가지 방(레지스터)이 필요합니다.

<a id="notion-3811d46c18fc800996bbd08d81d48efb"></a>

## ⏳ 1. 속도 조절 담당: UBRR (Baud Rate Register)

- **풀네임:** **U**SART **B**aud **R**ate **R**egister
- **뜻:** UART의 통신 속도(Baud Rate)를 결정하는 등록부(Register)입니다.
- <strong>뒤에 붙은 수식어들의 의미 (</strong><strong>`0`</strong><strong>,</strong> <strong>`H`</strong><strong>,</strong> <strong>`L`</strong><strong>):</strong>

  - <strong>`0`</strong>: ATmega128A에는 UART 포트가 2개(0번, 1번) 있습니다. 우리는 지금 **0번 포트**를 쓰니까 0이 붙은 겁니다. (1번 포트면 `UBRR1`이 됨)
  - **`H`** <strong>&amp;</strong> <strong>`L`</strong>: ATmega128A는 한 번에 8비트(1바이트)씩 처리하는 8비트 컴퓨터입니다. 그런데 속도 조절 숫자는 8비트(최대 255)보다 큰 숫자가 필요할 때가 많아서 **16비트 방**을 씁니다. 그래서 방을 반으로 쪼개서 **H**igh(상위 8비트), **L**ow(하위 8비트)로 나누어 부르는 것입니다.
- **쉽게 이해하기:** `UBRR0L = 207;` ➡️ **"0번 UART 속도 조절기 하위 방에 207이라는 속도 비율 값을 넣겠다\!"**

<a id="notion-3811d46c18fc804f908efc37ee2b2502"></a>

## 🎛️ 2. 환경 설정 및 제어 담당: UCSR (Control and Status Register)

이 녀석이 가장 골치 아프게 생겼죠? 단어를 쪼개면 아무것도 아닙니다.

- **풀네임:** **U**SART **C**ontrol and **S**tatus **R**egister
- **뜻:** UART의 제어(Control, 명령 내리기)와 상태(Status, 현재 하드웨어 상황 확인)를 담당하는 레지스터입니다.
- <strong>뒤에 붙은 알파벳</strong> <strong>`A`</strong><strong>,</strong> <strong>`B`</strong><strong>,</strong> **`C`** <strong>설정 방들의 차이:</strong>

  설정해야 할 비트(스위치)가 총 24개나 되는데, 우리 컴퓨터는 한 방에 8개 스위치밖에 못 넣습니다. 그래서 **A번 방, B번 방, C번 방**으로 쪼개놓은 것입니다.

<a id="notion-3811d46c18fc80d9a2dede1a465766b5"></a>

### 🅰️ UCSR0A (Status 위주의 방)

- 주로 UART의 현재 상태(데이터가 도착했는지, 송신이 끝났는지)를 나타내는 센서 깃발들이 모여있는 방입니다.
- **내부 비트 이름들:**

  - **`U2X0`** (**U**SART **2**X **X**peed): 속도를 2배(2X)로 올리겠다는 스위치입니다.
  - **`UDRE0`** (**U**SART **D**ata **R**egister **E**mpty): 송신 버퍼(Data Register)가 **비어있는지(Empty)** 알려주는 하드웨어 센서입니다. 비어있어야(`1`) 다음 글자를 채워 넣을 수 있으니까요.

<a id="notion-3811d46c18fc803488c0c075c68ffbd9"></a>

### 🅱️ UCSR0B (Control 위주의 방 - 기능 켜고 끄기)

- 주로 송수신 기능을 활성화(Enable)하거나 인터럽트를 제어하는 스위치들이 모여있습니다.
- **내부 비트 이름들:**

  - **`RXEN0`** (**R**ecei**v**e **E**n**able**): 수신(RX) 기능을 켜겠다\! (컴퓨터로부터 글자 받기 시작)
  - **`TXEN0`** (**T**ransmit **E**n**able**): 송신(TX) 기능을 켜겠다\! (컴퓨터로 글자 쏘기 시작)
  - **`RXCIE0`** (**R**ecei**v**e **C**omplete **I**nterrupt **E**nable): 수신이 완료(Complete)되면 메인 루프를 깨우는 인터럽트(Interrupt) 기능을 켜겠다(Enable)는 뜻입니다.

<a id="notion-3811d46c18fc80e987c7d0d8f111e583"></a>

## 📦 3. 데이터 임시 보관함: UDR (Data Register)

- **풀네임:** **U**SART **D**ata **R**egister
- **뜻:** 실제 송수신되는 데이터(글자 1바이트)가 임시로 머무는 물리적인 보관함(하드웨어 버퍼)입니다.
- **쉽게 이해하기:** \* `UDR0 = data;` ➡️ 0번 데이터 보관함에 글자를 던져 넣으면 하드웨어가 그걸 감지하고 Tx선으로 글자를 가차 없이 발사합니다.

  - 반대로 컴퓨터가 보낸 글자를 읽을 때도 `received = UDR0;` 코드를 통해 이 보관함에서 글자를 꺼내옵니다.

<a id="notion-3811d46c18fc80009c69c5e05b278cab"></a>

# 💡 결론

앞으로 데이터시트를 보거나 코딩할 때 이 그리스어 같은 단어들을 마주치면 아래 단어 조합 공식만 떠올리세요. 전혀 외울 필요가 없어집니다.

- **U** = USART (UART 통신 부품)
- **CSR** = Control &amp; Status Register (설정/상태 방)
- **BRR** = Baud Rate Register (속도 조절 방)
- **DR** = Data Register (글자 담는 바구니)
- **EN** = Enable (스위치 ON)
- **IE** = Interrupt Enable (인터럽트 ON)
- **C** = Complete (완료됨)

<br>

<br>
