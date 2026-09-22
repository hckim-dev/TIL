# \[AVR\] 원형 큐 기반 UART 버퍼링 &amp; HC-SR04 초음파 센서 드라이버 구현

> 날짜: 2026-06-17
> 원본 노션: [링크](https://app.notion.com/p/AVR-UART-HC-SR04-3811d46c18fc805b9454cabb42bb2bbb)

<!-- notion-page-id: 3811d46c18fc805b9454cabb42bb2bbb -->
<!-- notion-title: "[AVR] 원형 큐 기반 UART 버퍼링 & HC-SR04 초음파 센서 드라이버 구현" -->

---

```c
/**
* @file    queue.h
* @brief   원형 큐(링 버퍼) 인터페이스 선언
* @date    2026-06-17
* @author  kccistc
*/

#ifndef QUEUE_H_
#define QUEUE_H_

#include <stdint.h>

#define QUEUE_SIZE	100

/**
* @brief 원형 큐 구조체 정의
* @note  head와 tail은 인터럽트와 메인 스레드 간 공유되므로 volatile 필수 선언
*/
typedef struct {
	uint8_t buffer[QUEUE_SIZE];
	volatile uint16_t head;  /* 데이터를 읽고 제거하는 위치 (Read Index) */
	volatile uint16_t tail;  /* 데이터를 새로 저장하는 위치 (Write Index) */
} circular_queue_t;

void queue_init(circular_queue_t *q);
uint8_t queue_is_empty(const circular_queue_t *q);
uint8_t queue_is_full(const circular_queue_t *q);
uint8_t queue_enqueue(circular_queue_t *q, uint8_t data);
uint8_t queue_dequeue(circular_queue_t *q, uint8_t *data);
uint16_t queue_get_count(const circular_queue_t *q);

#endif /* QUEUE_H_ */
```

```c
/**
* @file    queue.c
* @brief   원형 큐(링 버퍼) 핵심 기능 구현
* @date    2026-06-17
* @author  kccistc
*/

#include "queue.h"

/**
* @brief  원형 큐 초기화 함수
* @param  q : 초기화할 원형 큐 구조체 포인터
*/
void queue_init(circular_queue_t *q)
{
	if (q == 0) return; // NULL
	
	q->head = 0;
	q->tail = 0;
}

/**
* @brief  큐가 비어있는지 확인하는 함수
* @param  q : 원형 큐 구조체 포인터
* @return true(비어있음), false(데이터 있음)
*/
uint8_t queue_is_empty(const circular_queue_t *q)
{
	/* head와 tail이 같은 인덱스를 가리키면 읽을 데이터가 없는 공백 상태입니다. */
	return (q->head == q->tail);
}

/**
* @brief  큐가 가득 찼는지 확인하는 함수
* @param  q : 원형 큐 구조체 포인터
* @return true(꽉 참), false(여유 공간 있음)
* @note   원형 큐 특성상 head와 tail의 구분을 위해 한 칸의 빈 공간을 버립니다.
*/
uint8_t queue_is_full(const circular_queue_t *q)
{
	/* tail의 다음 칸이 head와 일치하면 가득 찬 상태로 판단합니다. */
	return (((q->tail + 1) % QUEUE_SIZE) == q->head);
}

/**
* @brief  큐에 1바이트 데이터를 삽입하는 함수 (Push)
* @param  q    : 원형 큐 구조체 포인터
* @param  data : 삽입할 8비트 데이터
* @return true(삽입 성공), false(오버플로우로 인한 실패)
*/
uint8_t queue_enqueue(circular_queue_t *q, uint8_t data)
{
	/* 큐가 가득 찼다면 더 이상 데이터를 넣지 않고 에러(false)를 반환합니다. */
	if (queue_is_full(q))
	{
		return 0;
	}
	
	q->buffer[q->tail] = data;
	
	q->tail = (q->tail + 1) % QUEUE_SIZE;
	
	return 1;
}

/**
* @brief  큐에서 1바이트 데이터를 추출하는 함수 (Pop)
* @param  q    : 원형 큐 구조체 포인터
* @param  data : 추출한 데이터를 저장할 변수의 주소 (포인터)
* @return true(추출 성공), false(큐가 비어있어 실패)
*/
uint8_t queue_dequeue(circular_queue_t *q, uint8_t *data)
{
	/* 큐가 비어있다면 추출할 데이터가 없으므로 실패(false)를 반환합니다. */
	if (queue_is_empty(q))
	{
		return 0;
	}
	
	*data = q->buffer[q->head];
	
	q->head = (q->head + 1) % QUEUE_SIZE;
	
	return 1;
}

/**
* @brief  현재 큐에 쌓여있는 실제 데이터 개수를 반환하는 함수
* @param  q : 원형 큐 구조체 포인터
* @return 쌓여있는 데이터의 개수 (0 ~ QUEUE_SIZE-1)
*/
uint16_t queue_get_count(const circular_queue_t *q)
{
	/* tail이 head보다 작아졌을 때 대비 */
	return ((q->tail - q->head + QUEUE_SIZE) % QUEUE_SIZE);
}
```

<a id="notion-3821d46c18fc80b8a8ffc5b234259c2d"></a>

## ⏳ 원형 큐 (Circular Queue / 링 버퍼) 매커니즘

원형 큐(원형 버퍼, 환형 버퍼, 링 버퍼)는 FIFO(First In First Out, 선입선출) 구조를 가지는 핵심 자료구조

<a id="notion-3821d46c18fc80a79552e94ff82ae5ed"></a>

### MCU 통신에서 원형 큐를 쓰는 이유

- **기존 방식의 한계**: MCU에서 UART RX 인터럽트가 발생했을 때 일반 배열(`char rx_buff[80]`)에 딱 1개의 명령만 저장하도록 구현하면 , 여러 개의 명령어가 빠른 속도로 연달아 들어올 때 사용자 프로그램(`pc_command_processing`)이 이를 미처 처리하지 못하고 데이터를 놓치게 됩니다.
- **해결 책**: UART RX 인터럽트 루틴에서 일종의 완충(Buffer) 및 저수지 역할을 해주는 메모리 저장 공간이 필요합니다. 원형 큐에 데이터를 차곡차곡 버퍼링(Buffering)해 두면, 여러 명령이 한꺼번에 들어와도 사용자 프로그램에서 데이터 손실(Loss) 없이 안전하게 처리할 수 있습니다.

<a id="notion-3821d46c18fc80cf9d63fa5f03938d35"></a>

## 📡 초음파 센서 (HC-SR04) 제어 및 거리 계산

사람이 들을 수 있는 가청 주파수(20kHz) 이상의 소리를 초음파라고 합니다. HC-SR04 센서는 송신부와 수신부로 구성되어 있으며 , 송신부에서 발사한 초음파가 벽이나 물체에 반사되어 돌아오는 시간을 수신부에서 인식하여 거리를 측정합니다.

<a id="notion-3821d46c18fc8094bcc1c593ae8138db"></a>

### ① 동작 원리 및 타이밍 다이어그램 (Timing Diagram)

1. **트리거 신호 방출**: STM32 등의 MCU에서 초음파 센서의 **TRIG 핀에 최소 10us 동안 HIGH 펄스**를 가합니다.
2. **초음파 버스트 발생**: 신호를 받은 센서는 자체적으로 **40kHz 주파수의 초음파를 8번(8 Cycle Sonic Burst) 발생**시켜 공기 중으로 쏘아 올립니다.
3. **에코 신호 수신**: 발사와 동시에 **ECHO 핀이 HIGH로 상승**하며, 초음파가 물체에 반사되어 돌아올 때까지 HIGH 상태를 유지합니다.
4. **거리 측정**: 최종적으로 ECHO 핀이 HIGH를 유지한 **'시간(Pulse Width)'의 길이를 측정**하여 거리를 계산합니다.

<a id="notion-3821d46c18fc8088baf6e437b20c5a50"></a>

### ② 물리적 속도 및 거리 환산 공식

- **소리의 속도**: 초당 340m 이동 (340M/S)
- **마이크로초(us) 단위 환산**: **0.034cm / us (1us 동안 0.034cm 이동)**    
- **왕복 및 편도 소요 시간**: 초음파가 1cm 거리를 왕복 이동하는 데 소요되는 시간은 다음과 같습니다.

  **T = 2 \* 0.01 / 340 = 58.824 us (왕복 시간)**

  즉, **1cm 편도 이동 소요 시간은 약 29us**입니다.
- **최종 거리(cm) 계산 공식**: **distance = duration / 29 / 2**

<a id="notion-3821d46c18fc8039a2f6c85a60d4d1f7"></a>

### ③ 오실로스코프 기반 2cm 측정 실측 시나리오

- MCU가 TRIG 핀으로 10us 트리거 펄스를 인가합니다.
- 물체가 약 2cm 앞에 있을 때, 초음파 센서 **ECHO 단자로부터 약 140us 길이의 HIGH 펄스가 출력**됩니다.
- **연산 과정**:

  1. 140us / 2 (왕복) = 70us
  2. 2 = 70us / 29us (1초 이동하는 속도)
- 소수점 이하를 제외하면 최종적으로 **2cm**라는 정확한 물리적 데이터가 도출됩니다.

```c
/**
* @file    ultrasonic.c
* @brief   ATmega128A 타이머1 및 외부 인터럽트 기반 초음파 센서(HC-SR04) 드라이버
* @date    2026-06-17
* @author  kccistc
*/

#include "ultrasonic.h"

volatile int g_ultrasonic_distance_cm = 0; // 탐지된 거리 (cm)
volatile int g_falling_edge_flag = 0; // 하강 에지 감지 플래그

// INT4 핀 전압 변화 감지
ISR(INT4_vect)
{
	// 1. 상승 에지 감지 (Echo 신호 시작): 타이머 카운터 리셋
	if (ECHO_PORT & (1 << ECHO_PIN))
	{
		TCNT1 = 0;
	}
	// 2. 하강 에지 감지 (Echo 신호 종료): 거리 환산 연산 수행
	else
	{
		int duration_us = TCNT1 * 64; // 시간(us) = TCNT1 * 1000000.0 * 1024 / F_CPU
		g_ultrasonic_distance_cm = duration_us / 58; // 거리(cm) = 시간(us) / 58 (왕복 소요 시간 마진 반영)
		g_falling_edge_flag = 1;
	}
}

void init_ultrasonic(void)
{
	TRIG_DDR |= (1 << TRIG_PIN); // Trigger 핀: 출력 모드
	ECHO_DDR &= ~(1 << ECHO_PIN); // Echo 핀: 입력 모드
	
	// INT4 제어: 상승/하강 둘 다 감지
	EICRB = (0 << ISC41) | (1 << ISC40);
	EIMSK |= (1 << INT4); // INT4번 활성화
	
	// 타이머/카운터 1 설정: 1024 분주비 적용 (1클록 = 64us)
	TCCR1B |= (1 << CS12) | (1 << CS10);
}

// 15us 트리거 펄스 생성
void ultrasonic_make_trigger(void)
{
	TRIG_PORT &= ~(1 << TRIG_PIN); // Low 출력
	_delay_us(1);
	
	TRIG_PORT |= (1 << TRIG_PIN); // High 출력
	_delay_us(15); // 센서 규격(10us) 대비 안전 마진(Redundancy) 반영
	
	TRIG_PORT &= ~(1 << TRIG_PIN); // Low 출력 (하강 에지 마감)
}

void ultrasonic_processing(void)
{
	printf("dis: %dcm\n", g_ultrasonic_distance_cm);
	
	ultrasonic_make_trigger(); // 다음 측정을 위한 트리거 발사
}
```
