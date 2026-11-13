# \[RTOS\] FreeRTOS 기초·태스크·스케줄링

> 날짜: 2026-11-12
> 원본 노션: [링크](https://app.notion.com/p/RTOS-FreeRTOS-4161d46c18fc80db9aeec7f777fad4be)

<!-- notion-page-id: 4161d46c18fc80db9aeec7f777fad4be -->
<!-- notion-title: "[RTOS] FreeRTOS 기초·태스크·스케줄링" -->

---

<a id="notion-d0887a3597ef4b02b8b94a20892b11f1"></a>

# FreeRTOS 기초·태스크·스케줄링

> 💡 RTOS의 핵심은 단순히 빠르게 실행하는 것이 아니라, **정해진 시간 안에 필요한 처리를 예측 가능하게 수행하는 것**이다.<br>기능을 Task로 나누고, 기다리는 Task는 Blocked 상태로 두어 다른 Task가 CPU를 사용할 수 있게 한다.

<a id="notion-a69415abb5104209b545a8e1498ef2e0"></a>

## RTOS 한눈에 보기

- <strong>RTOS(Real-Time Operating System)</strong>: 정해진 시간 요구를 만족하는 <strong>결정성(Determinism)</strong>이 중요
- **Bare-metal**: 보통 하나의 while(1)에서 기능을 순차 처리 → 한 작업이 오래 걸리면 뒤 작업도 지연될 수 있음
- **RTOS**: 기능을 여러 Task로 분리하고 Scheduler가 상태와 우선순위에 따라 실행 순서를 결정
- 한 Task가 기다릴 때 다른 Ready Task가 실행될 수 있어 응답성과 주기 관리가 쉬워짐

<a id="notion-982b9dba934744b0af5edc22e48c8f6c"></a>

## Task와 Scheduler

- **Task ≈ MCU 환경의 Thread**
- 각 Task는 <strong>자기 Stack + TCB(Task Control Block)</strong>를 가짐
- Code/Data/Heap은 같은 주소 공간을 공유하므로 전역 변수와 Peripheral은 공유 자원이 될 수 있음
- FreeRTOS는 **우선순위 기반 선점형 스케줄링**을 사용
- STM32F411은 **single-core**이므로 한 순간에 실제 Running인 Task는 하나이며, Scheduler가 실행할 Task를 선택하고 Context Switching으로 교대함
- 높은 우선순위 Task가 Ready가 되면 낮은 우선순위 Task를 선점할 수 있음
- Task Priority는 **숫자가 클수록 높음**
- 같은 우선순위 Task가 여러 개 Ready이면 **configUSE\_TIME\_SLICING=1**일 때 Time Slicing으로 CPU를 나눠 사용
- 높은 우선순위 Task가 계속 Ready 상태이면 낮은 Task에 **Starvation**이 발생할 수 있음

| 상태 | 의미 |
| --- | --- |
| Running | 현재 CPU에서 실행 중 |
| Ready | 실행 가능하지만 CPU 차례를 기다림 |
| Blocked | 시간·이벤트·데이터 등을 기다림. CPU 사용 안 함 |
| Suspended | 명시적으로 중단됨. Resume 전까지 실행 대상에서 제외 |

- Blocked 조건이 해제되면 먼저 **Ready**가 되며, Scheduler 선택을 받아야 Running이 됨
- 실행 가능한 사용자 Task가 없으면 **Idle Task**가 실행됨

**핵심:** 기다려야 할 때 Busy-wait하지 말고 가능한 한 Blocked 상태로 CPU를 양보한다.

<a id="notion-c544fc86556f4bccb3679c3283ced296"></a>

## Tick과 Context Switching

- **Tick**: RTOS의 시간 기준. 예: configTICK\_RATE\_HZ = 1000이면 1 Tick = 1 ms
- **SysTick**: Kernel Tick을 증가시키고 Delay가 끝난 Task 등을 Ready로 전환해 스케줄링 계기를 만듦
- **PendSV**: ARM Cortex-M의 Exception. FreeRTOS가 실제 Context Switching에 사용
- **SVC**: 첫 Task 시작 등에 사용

PendSV Handler의 핵심 흐름:

**현재 Task Context 저장 → vTaskSwitchContext()로 다음 Task 선택 → 다음 Task Context 복원 → 실행 재개**

Context Switching은 SysTick뿐 아니라 현재 Task가 Blocked되거나 taskYIELD()를 호출하는 상황 등에서도 발생할 수 있다.

<a id="notion-3e177b203af5479a810dc894d8f225de"></a>

## FreeRTOS Native API와 CMSIS-RTOS2

| 역할 | FreeRTOS Native | CMSIS-RTOS2 |
| --- | --- | --- |
| Task 생성 | xTaskCreate() | osThreadNew() |
| Delay | vTaskDelay() | osDelay() |
| Scheduler 시작 | vTaskStartScheduler() | osKernelStart() |

- **CMSIS**: ARM이 정의한 Cortex-M 공통 소프트웨어 인터페이스
- **CMSIS-RTOS2**: FreeRTOS 같은 RTOS 위에 공통 RTOS API를 제공하는 계층
- Scheduler가 정상적으로 시작되면 보통 이후 main() 코드로 돌아오지 않음
- Native API와 CMSIS-RTOS2를 이해하는 것은 좋지만, **Scheduler 시작 경로는 중복 호출하지 않는다.**

<a id="notion-5f55f3d5c5c2474e9ef170fa67c1f271"></a>

## xTaskCreate() 핵심

```c
xTaskCreate(
    vTask,          // Task 함수
    "TaskName",     // 이름
    128,            // Stack depth
    NULL,           // 전달 인자
    1,              // Priority
    &hTask          // Task Handle
);
```

| 항목 | 핵심 |
| --- | --- |
| Task 함수 | return하면 안 됨. 보통 무한 루프로 동작하거나 필요 시 vTaskDelete(NULL)로 종료 |
| Stack depth | byte가 아니라 StackType\_t 단위 |
| Parameter | Task 함수에 전달할 void \* 인자 |
| Priority | 숫자가 클수록 높음 |
| Handle | 생성된 Task를 참조·제어할 때 사용 |

- Cortex-M4에서는 보통 **1 StackType\_t = 4 byte** → 128 word ≈ 512 byte
- 동적 생성 시 **TCB + Task Stack**이 FreeRTOS Heap에서 할당됨
- 생성 성공 시 pdPASS, Heap 부족 등으로 실패할 수 있음

<a id="notion-78b40edd39e54413acaa036e9fd307b6"></a>

## Stack과 Heap

**Task Stack**

- Task마다 독립
- 지역 변수, 함수 호출 정보, Return Address, Context 저장 등에 사용
- printf/sprintf나 큰 지역 배열은 Stack 사용량을 크게 늘릴 수 있음

**FreeRTOS Heap**

- 동적 Task 생성 시 TCB와 Task Stack 할당
- Queue, Semaphore, Timer 등 동적 RTOS 객체 생성에도 사용

확인:

- uxTaskGetStackHighWaterMark(): **실행 이후 가장 적게 남았던 Stack 여유량**. 반환 단위도 StackType\_t 기준
- configCHECK\_FOR\_STACK\_OVERFLOW: Stack Overflow 감지 설정

<a id="notion-001b26abdcfe400ba474c3869ccd2874"></a>

## Delay와 Blocking

```c
vTaskDelay(pdMS_TO_TICKS(500));
```

- <strong>vTaskDelay()</strong>: 현재 Task를 일정 시간 Blocked → 그동안 다른 Ready Task가 CPU 사용
- <strong>pdMS\_TO\_TICKS(ms)</strong>: ms를 현재 FreeRTOS Tick으로 변환
- <strong>osDelay()</strong>: CMSIS-RTOS2 방식의 Task Delay
- <strong>HAL\_Delay()</strong>: HAL Tick 기반 Busy-wait 성격의 지연. Task를 Blocked시키는 RTOS Delay가 아니므로 Task 내부에서는 가급적 vTaskDelay()/osDelay() 사용

<a id="notion-4833fe7f639c43e6999da05f3d47b600"></a>

## STM32 + FreeRTOS 기본 설정

NUCLEO-F411RE:

- LD2: PA5
- B1: PC13
- USART2: PA2(TX), PA3(RX) → ST-Link Virtual COM

CubeMX:

- SYS → Timebase Source: **TIM11 등 별도 Timer**
- Middleware → FREERTOS 활성화
- Interface: CMSIS\_V2

역할 분리:

- **SysTick** → FreeRTOS Kernel Tick
- **HAL Timebase** → TIM11 등 별도 Timer

같은 SysTick을 RTOS와 HAL 시간 기준으로 함께 사용하지 않도록 분리하는 구조다.

> ➡️ 다음 학습: \[RTOS\] FreeRTOS 통신·동기화·디버깅<br>[\[RTOS\] FreeRTOS 통신·동기화·디버깅](https://app.notion.com/p/4161d46c18fc801d913cdd4a267b84a5)

<a id="notion-df3b06bcc8794cb6ad24af8c6f336cf3"></a>

## 실습 체크

- Task Stack 크기를 byte로 착각하지 않기
- Task 함수는 그냥 return하지 않고 반복 실행하거나 vTaskDelete() 사용
- 기다림은 Busy-wait보다 vTaskDelay()/osDelay() 등 Blocking API 사용
- Scheduler 시작 함수는 한 번만 호출
- xTaskCreate() 실패 가능성을 고려해 필요하면 반환값 확인
- UART 출력 문제 시 COM Port, Baud Rate, \_write() 설정 확인
