# \[RTOS\] FreeRTOS 핵심 정리

> 날짜: 2026-11-12
> 원본 노션: [링크](https://app.notion.com/p/RTOS-FreeRTOS-4161d46c18fc80db9aeec7f777fad4be)

<!-- notion-page-id: 4161d46c18fc80db9aeec7f777fad4be -->
<!-- notion-title: "[RTOS] FreeRTOS 핵심 정리" -->

---

<a id="notion-d0887a3597ef4b02b8b94a20892b11f1"></a>

# RTOS 개념과 개발환경

<a id="notion-a69415abb5104209b545a8e1498ef2e0"></a>

## RTOS 한눈에 보기

- <strong>RTOS(Real-Time Operating System)</strong>: 단순히 빠른 OS가 아니라 <strong>정해진 시간 안에 처리를 완료할 수 있는 결정성(Determinism)</strong>이 핵심.
- Bare-metal은 하나의 `while(1)`에서 기능을 순차 실행하므로 한 작업이 오래 걸리면 뒤 작업도 함께 지연될 수 있음.
- RTOS는 기능을 **Task**로 분리하고 **Scheduler**가 우선순위와 상태에 따라 CPU 실행 순서를 결정.
- 한 Task가 대기하면 다른 Ready Task가 CPU를 사용할 수 있어 기능별 응답성과 주기를 관리하기 쉬움.

<a id="notion-982b9dba934744b0af5edc22e48c8f6c"></a>

## Task와 Scheduler

- **Task ≈ MCU 환경의 Thread**
- 각 Task는 <strong>자기 Stack + TCB(Task Control Block)</strong>를 가짐.
- Task끼리 Code/Data/Heap은 같은 주소 공간을 공유.
- Scheduler는 Ready Task 중 **가장 높은 우선순위**를 실행.
- 같은 우선순위 Task는 기본적으로 <strong>Time Slicing(Round-Robin)</strong>으로 교대.
- 높은 우선순위 Task가 계속 Ready 상태로 CPU를 놓지 않으면 낮은 Task에 **Starvation**이 발생할 수 있음.

| 상태 | 의미 |
| --- | --- |
| Running | 현재 CPU에서 실행 중 |
| Ready | 실행 준비 완료, CPU 차례 대기 |
| Blocked | 시간·이벤트·자원을 기다리는 중. CPU 사용 안 함 |
| Suspended | 명시적으로 정지. Resume 전까지 실행 대상에서 제외 |

RTOS에서는 기다려야 할 때 Busy-wait보다 **Blocked 상태로 CPU를 양보하는 방식**이 중요함.

<a id="notion-c544fc86556f4bccb3679c3283ced296"></a>

## Tick과 Context Switching

- **Tick**: RTOS의 시간 기준. `configTICK_RATE_HZ = 1000`이면 1 Tick = 1 ms.
- **SysTick**: Tick 증가 및 스케줄링 필요 여부 판단.
- **PendSV**: 실제 Task Context Switching 수행.
- **SVC**: 첫 Task 시작 등에 사용.
- Context Switching 시 현재 Task의 레지스터 상태를 Stack/TCB에 저장하고 다음 Task의 상태를 복원.

<a id="notion-3e177b203af5479a810dc894d8f225de"></a>

## FreeRTOS Native API와 CMSIS-RTOS2

| 역할 | FreeRTOS Native | CMSIS-RTOS2 |
| --- | --- | --- |
| Task 생성 | `xTaskCreate()` | `osThreadNew()` |
| Delay | `vTaskDelay()` | `osDelay()` |
| Scheduler 시작 | `vTaskStartScheduler()` | `osKernelStart()` |

- **CMSIS**: ARM이 정의한 Cortex-M용 공통 소프트웨어 인터페이스 표준.
- CMSIS-RTOS2는 FreeRTOS 같은 RTOS 위에서 공통 API를 제공하는 계층.
- `vTaskStartScheduler()` / `osKernelStart()`로 Scheduler가 정상 시작되면 이후 `main()` 코드는 일반적으로 실행되지 않음.

<a id="notion-c1beee8e14ef41f3a2f81814b6a29a7f"></a>

## `xTaskCreate()`와 메모리

```c
xTaskCreate(
    vTask,          // 실행할 Task 함수
    "TaskName",     // Task 이름
    128,            // Stack depth
    NULL,           // Task에 전달할 파라미터
    1,              // Priority
    NULL            // Task Handle 저장 위치
);
```

- Priority는 **숫자가 클수록 높음**.
- Handle을 저장하면 해당 Task의 Suspend/Resume/Delete 등에 사용 가능.
- 동적 생성 시 **TCB + Task Stack을 FreeRTOS Heap에서 할당**.
- 반환값은 생성 성공 시 `pdPASS`. Heap 부족 등으로 실패할 수 있으므로 필요하면 반환값 확인.
- Stack 크기는 byte가 아니라 `StackType_t` 단위이며 Cortex-M4에서는 보통 1 word = 4 bytes.

**Task Stack**

- Task마다 독립.
- 지역 변수, 함수 호출 정보, Return Address, Context 저장 등에 사용.

**FreeRTOS Heap**

- 동적 Task 생성 시 TCB와 Task Stack 할당.
- Queue, Semaphore, Timer 등 동적 RTOS 객체 생성에도 사용.

확인:

- `uxTaskGetStackHighWaterMark()`: Stack 여유 확인
- `configCHECK_FOR_STACK_OVERFLOW`: Stack Overflow 감지 설정

<a id="notion-001b26abdcfe400ba474c3869ccd2874"></a>

## Delay와 Blocking

```c
vTaskDelay(pdMS_TO_TICKS(500));
```

- `vTaskDelay()`: 현재 Task를 일정 시간 **Blocked** 상태로 전환 → 다른 Ready Task 실행 가능.
- `pdMS_TO_TICKS(ms)`: ms를 현재 FreeRTOS Tick 수로 변환.
- `osDelay()`: CMSIS-RTOS2 방식의 Task Delay.
- `HAL_Delay()`: HAL Tick 기반 지연. RTOS Task 내부보다는 Scheduler 시작 전 초기화 단계 등에 사용.

주기적 Task에서는 가능한 Busy-wait보다 `vTaskDelay()`, Queue/Semaphore 대기처럼 **Blocking API**를 사용.

<a id="notion-4833fe7f639c43e6999da05f3d47b600"></a>

## STM32 + FreeRTOS 기본 설정

NUCLEO-F411RE:

- LD2: PA5
- B1: PC13
- USART2: PA2(TX), PA3(RX) → ST-Link Virtual COM

CubeMX:

- `SYS → Timebase Source`: **TIM11 등 별도 Timer**
- `Middleware → FREERTOS`: 활성화
- Interface: `CMSIS_V2`

SysTick은 FreeRTOS Kernel Tick에 사용하고, HAL Timebase는 별도 Timer로 분리함.

<a id="notion-3f6f5dc5ff6e448f8096735b1645ad58"></a>

## 실습 시 체크

- Task Stack 크기를 byte로 착각하지 않기.
- Heap 부족 시 `xTaskCreate()` 실패 가능.
- Task 함수는 그냥 `return`하지 않고 반복 실행하거나 `vTaskDelete()` 사용.
- RTOS Task 내부 대기는 `vTaskDelay()` / `osDelay()` 사용.
- UART 출력 문제 시 COM Port, Baud Rate, `_write()` 설정 확인.

<br>
