# \[RTOS\] FreeRTOS 통신·동기화·디버깅

> 날짜: 2026-11-13
> 원본 노션: [링크](https://app.notion.com/p/RTOS-FreeRTOS-4161d46c18fc801d913cdd4a267b84a5)

<!-- notion-page-id: 4161d46c18fc801d913cdd4a267b84a5 -->
<!-- notion-title: "[RTOS] FreeRTOS 통신·동기화·디버깅" -->

---

<a id="notion-4171d46c18fc80509bbef35cc6e6fc6c"></a>

# FreeRTOS 통신·동기화·디버깅

> 💡 핵심은 **Task 사이의 데이터·신호·공유 자원·시간 동작에 맞는 RTOS 기능을 선택하는 것**이다.<br>인터럽트나 Timer Callback은 짧게 끝내고, 오래 걸리는 처리는 Task에 맡긴다.

> ⬅️ 선행 학습: \[RTOS\] FreeRTOS 기초·태스크·스케줄링<br>[\[RTOS\] FreeRTOS 기초·태스크·스케줄링](https://app.notion.com/p/4161d46c18fc80db9aeec7f777fad4be)

<a id="notion-aca83f524cdb4b569e0c9e88cbbcd185"></a>

## 먼저 알아둘 용어

| 용어 | 의미 |
| --- | --- |
| Task | RTOS가 스케줄링하는 실행 단위. 일반 OS의 Thread와 비슷함 |
| Running / Ready | CPU에서 실행 중 / 실행 가능하지만 CPU 차례를 기다리는 상태 |
| Blocked | 시간·이벤트·데이터 등을 기다리는 상태. CPU를 사용하지 않음 |
| ISR | Interrupt Service Routine. 인터럽트 발생 시 실행되는 짧은 처리 함수 |

<a id="notion-90f0d0c674c14b738b763461db0f23fa"></a>

## RTOS 기능 선택표

| 필요한 것 | 우선 선택 |
| --- | --- |
| 데이터 전달 | Queue |
| 1:1 단순 신호 | Task Notification |
| 이벤트 발생 여부 | Binary Semaphore |
| 이벤트 횟수 / N개 자원 | Counting Semaphore |
| 여러 상태·AND/OR 조건 | Event Group |
| 공유 자원 보호 | Mutex |
| 시간 기반 주기·원샷 | Software Timer |

<a id="notion-8069a6b290f648ceb725adc41731e65e"></a>

## 먼저 알아둘 개념

<a id="notion-17ed2d2672e4428c87ae7ae5a3bea950"></a>

### 주기 실행

- <strong>vTaskDelay()</strong>: 호출 시점부터 상대적으로 대기 → 작업 시간이 포함되면 주기가 밀릴 수 있음
- <strong>vTaskDelayUntil()</strong>: 이전 기준 시각을 바탕으로 고정 주기 유지 → 센서 샘플링·제어 루프에 적합

<a id="notion-2236ab108c234ee599443d2d7ffbc9b6"></a>

### Task 관리 API

| API | 의미 |
| --- | --- |
| xTaskCreate() | Task 생성 |
| vTaskDelete() | Task 삭제. NULL이면 자기 자신. 동적 메모리 회수는 Idle Task가 처리 |
| vTaskSuspend() / vTaskResume() | Task 일시정지 / 재개 |
| vTaskPrioritySet() | 실행 중 우선순위 변경 |
| taskYIELD() | 같은 우선순위 Task에 자발적으로 CPU 양보 |

<a id="notion-6d50895dd742436a81ed924255cf4b18"></a>

### Scheduler와 Context Switching

- **Scheduler**: Ready Task 중 다음에 실행할 Task를 결정
- **SysTick**: Kernel Tick을 증가시키고, Delay가 끝난 Task 등을 Ready로 전환해 스케줄링 계기를 만든다.
- **PendSV**: ARM Cortex-M이 제공하는 Exception. FreeRTOS가 실제 Context Switching에 사용한다.
- **SVC**: 첫 Task 시작 등에 사용

PendSV Handler의 핵심 흐름:

**현재 Task Context 저장 → vTaskSwitchContext()로 다음 Task 선택 → 다음 Task Context 복원 → 실행 재개**

Task가 Blocked되거나 `taskYIELD()`를 호출하는 경우처럼 SysTick 외의 상황에서도 Context Switching이 발생할 수 있다.

<a id="notion-4d5ecdb69be74098b0476c9285c53f36"></a>

## Task 간 데이터 전달: Queue

여러 Task가 전역 변수를 직접 공유하면 선점 시점에 따라 **Race Condition**이 생길 수 있다. 데이터 전달이 목적이면 Queue를 우선 고려한다.

Queue는 **FIFO + 데이터 복사 + Blocking 대기**를 함께 제공한다.

```c
QueueHandle_t q = xQueueCreate(5, sizeof(int));

xQueueSend(q, &value, 0);
xQueueReceive(q, &value, portMAX_DELAY);
```

- 생성 시 **길이 + 항목 크기** 지정
- 송신한 값은 Queue 내부에 **복사**됨
- 빈 Queue에서 Receive하면 데이터가 올 때까지 Blocked 가능
- 가득 찬 Queue에서 Send하면 공간이 생길 때까지 Blocked 가능
- 구조체도 그대로 전달 가능
- 큰 데이터는 포인터 전달이 가능하지만 **메모리 수명·소유권**을 반드시 정해야 한다.

<a id="notion-aaf059796a2b477bae6913cef3374d3d"></a>

### ISR에서 Queue

ISR에서는 일반 API가 아니라 반드시 **...FromISR API**를 사용한다.

```c
BaseType_t w = pdFALSE;

xQueueSendFromISR(q, &data, &w);
portYIELD_FROM_ISR(w);
```

ISR은 짧게 끝내고 실제 처리는 Task에 넘기는 **Deferred Processing** 구조가 기본이다.

<a id="notion-235cfbc0e5eb421c989ccf591bea3f27"></a>

## Semaphore와 Mutex

<a id="notion-4936f721049f44e5a921add2ce6cd695"></a>

### Binary / Counting Semaphore

- Binary: “이벤트가 발생했는가?”가 중요할 때. 생성 직후 값은 **0**.
- Counting: “몇 번 발생했는가?”까지 보존하거나 N개 자원을 관리할 때
- ISR에서는 xSemaphoreGiveFromISR() 사용

Binary Semaphore는 여러 번 Give되어도 최대 값이 1이라 **이벤트 횟수가 누락될 수 있다.**

<a id="notion-55d62bf52c734b7696f7357a4e73f68f"></a>

### Mutex

UART, I2C/SPI, 전역 버퍼처럼 **한 번에 한 Task만 사용해야 하는 자원**을 보호한다.

```c
xSemaphoreTake(xMutex, portMAX_DELAY);

/* 공유 자원 사용 */

xSemaphoreGive(xMutex);
```

- Mutex는 생성 직후 사용 가능한 상태이며, **Take한 Task가 Give해야 하는 소유권**이 있다.
- ISR에서는 사용하지 않는다.
- **우선순위 역전**: Low가 Mutex를 가진 상태에서 High가 기다리는데 Mid가 Low를 선점해 High까지 오래 지연되는 상황
- Mutex는 **Priority Inheritance**로 Low의 우선순위를 일시적으로 올려 역전을 완화한다.
- 매우 짧은 변수 갱신은 Critical Section, 비교적 긴 공유 자원 보호는 Mutex가 적합하다.
- 여러 Mutex를 서로 다른 순서로 획득하면 Deadlock이 생길 수 있으므로 **획득 순서를 통일**한다.

<a id="notion-4cfa4adef9b04d4c9cd94185f215e55f"></a>

### UART 공유: Gatekeeper 패턴

여러 Task가 직접 printf()하면 UART 접근이 충돌하거나 로그가 섞일 수 있다.<br>**Gatekeeper**는 UART를 한 Task만 소유하고, 다른 Task는 Queue로 로그만 전달하는 구조다.

권장 구조:

```text
Task A ─┐
Task B ─┼─> Log Queue ─> LogTask ─> UART
Task C ─┘
```

UART를 LogTask 하나만 소유하면 Mutex 없이도 안전하게 로그를 직렬화할 수 있다.

<a id="notion-d2748a5b09ca41a39aba4db1bbce25ba"></a>

## Event Group / Task Notification / Software Timer

<a id="notion-eeb5d4f9fa104b699a5ca039eba498f8"></a>

### Event Group

여러 상태를 **bit flag**로 관리하고 AND/OR 조건으로 기다릴 때 사용한다.

- 여러 이벤트 중 하나 → OR
- 모든 이벤트가 필요 → AND
- 하나의 비트를 여러 Task가 관찰하는 Broadcast 가능
- ISR에서는 일반 API 대신 xEventGroupSetBitsFromISR() 사용

<a id="notion-f15c5b6db6e646e986cd8e688c7b3106"></a>

### Task Notification

Task마다 가진 알림 값을 이용하는 **가벼운 1:1 통신 방식**이다.

- 별도 Queue/Semaphore 객체가 필요 없음
- Binary/Counting 신호, 값, bit 전달 가능
- RAM 사용량이 적고 빠름
- **수신 Task가 하나일 때** 적합

대표 API:

- xTaskNotifyGive() / ulTaskNotifyTake()
- xTaskNotify() / xTaskNotifyWait()
- ISR: vTaskNotifyGiveFromISR(), xTaskNotifyFromISR()

<a id="notion-b78aa9ede71643bd9e7f766502292407"></a>

### Software Timer

Task를 하나 더 만들지 않고 시간 기반 동작을 수행할 때 사용한다.

- Auto-reload: 주기 실행
- One-shot: 한 번 실행
- 콜백은 **Timer Service Task**에서 실행
- 콜백 안에서는 vTaskDelay, 긴 처리, Blocking API 사용 금지

활용:

- Heartbeat LED
- 버튼 Debounce
- Timeout / Watchdog 패턴

<a id="notion-2f6be53805e2424da59e004f09de8053"></a>

## 메모리 관리와 디버깅

<a id="notion-9c4c699695554aa0a36f046aca850d76"></a>

### FreeRTOS 메모리

- Task Stack 크기는 byte가 아니라 **StackType\_t(word) 단위**이며 Cortex-M4에서는 보통 1 word = 4 byte.
- xTaskCreate()로 동적 생성하면 **TCB + Task Stack**이 FreeRTOS Heap에서 할당된다.
- xTaskCreateStatic()은 사용자가 TCB/Stack 버퍼를 제공해 Heap 의존을 줄일 수 있다.
- Queue/Semaphore/Timer 객체도 Heap을 사용한다.
- heap\_4는 해제 + 인접 빈 블록 병합을 지원해 일반적으로 권장된다.

주요 확인 API:

```c
xPortGetFreeHeapSize();
xPortGetMinimumEverFreeHeapSize();
uxTaskGetStackHighWaterMark(handle);
```

- FreeHeap : 현재 남은 Heap
- MinimumEverFreeHeap : 실행 후 가장 적게 남았던 Heap
- StackHighWaterMark : Task별 최소 Stack 여유량

개발 중 권장:

- configCHECK\_FOR\_STACK\_OVERFLOW = 2
- configUSE\_MALLOC\_FAILED\_HOOK = 1
- Stack/Heap은 실제 측정 후 여유를 두고 조정

<a id="notion-21436c110b244b13a52c99f855e48dfe"></a>

### 인터럽트 우선순위 주의

FreeRTOS Task와 Cortex-M NVIC는 숫자 방향이 반대다.

| 구분 | 숫자 방향 |
| --- | --- |
| FreeRTOS Task Priority | 숫자가 클수록 높음 |
| Cortex-M NVIC Priority | 숫자가 작을수록 높음 |

STM32F411 예제 설정에서 configLIBRARY\_MAX\_SYSCALL\_INTERRUPT\_PRIORITY = 5이면:

- NVIC Priority **5\~15** → FreeRTOS ...FromISR API 사용 가능
- Priority **0\~4** → FreeRTOS API 사용 금지
- FreeRTOS에서는 **NVIC\_PRIORITYGROUP\_4**를 사용하고, 개발 중에는 configASSERT로 잘못된 ISR 우선순위/API 사용을 잡는다.

ISR 원칙:

- 짧게 처리
- printf, 긴 루프 금지
- 데이터/신호만 전달하고 실제 처리는 Task에서

<a id="notion-a558e8e3107845d3bd655b45d893dc22"></a>

### HardFault

주요 원인:

- Stack Overflow
- 잘못된 포인터
- 잘못된 메모리 접근
- 정렬 위반
- 0으로 나누기 등

분석 시:

- **PC / LR**: Fault가 발생한 코드 위치와 복귀 흐름 확인
- **CFSR / HFSR**: Fault 종류와 원인 확인
- **BFAR / MMFAR**: 잘못 접근한 주소 확인
- Map 파일 / Debugger로 실제 소스 위치 추적

<a id="notion-cc48a1f054944771bb20d5d905e66f60"></a>

### CPU 사용률

- Idle 비율이 높으면 CPU 여유가 큰 편이다.
- 정확한 Task별 점유율은 vTaskGetRunTimeStats() 등 Runtime Stats로 측정한다.
- Runtime Stats는 Tick보다 충분히 빠른 별도 카운터(DWT/TIM 등)를 사용한다.
- ulIdleCount 증가량은 간단한 CPU 여유 추정용으로 활용할 수 있다.

<a id="notion-8cfedc8b00d340f6999b30274c1f6b8d"></a>

## 종합 프로젝트 구조

센서 모니터링 예제는 지금까지 배운 RTOS 기능을 다음처럼 조합한다.

```text
SensorTask
   │ xSensorQ
   ▼
ProcTask ── EV_ALARM ──> AlarmTask
   │
   │ xLogQ
   ▼
LogTask ──> UART

EXTI(B1)
   │
   ▼
Debounce Timer ── Notify ──> CtrlTask
                              │
                              └─ Mutex ─> Sampling Period 설정

Heartbeat Timer ──> LD2
MonTask ── xLogQ ──> Heap/Stack 상태 로그
```

<a id="notion-ea11350f002d47549e6d5c3f0400b766"></a>

### 역할 분담

- **SensorTask**: ADC 주기 샘플링, vTaskDelayUntil() 사용
- **ProcTask**: 이동 평균 계산, 경보 상태 판단
- **AlarmTask**: Event Group을 기다려 경보 LED 제어
- **CtrlTask**: 버튼 Notification을 받아 정상/고속 모드 전환
- **LogTask**: UART 단독 소유(Gatekeeper)
- **MonTask**: Heap/Stack 상태 주기 확인
- **Software Timer**: Heartbeat와 버튼 Debounce

<a id="notion-565ff502363d4d3eadf346d1b480ed9f"></a>

### 설계 핵심

1. **주기 정확도가 중요한 Task는 높은 우선순위 + vTaskDelayUntil()**
2. 데이터 흐름은 Queue로 분리
3. 상태는 Event Group, 1:1 신호는 Notification
4. 공유 설정값은 Mutex로 보호
5. UART는 Gatekeeper Task 한 곳에서만 접근
6. ISR/Timer Callback은 짧게 끝내고 실제 처리는 Task에 위임
7. Queue 길이, Stack, Heap, 우선순위는 감으로 확정하지 않고 **측정 후 조정**
8. Sensor 주기/jitter, 버튼 응답, CPU Idle, heap minEver, Stack HighWaterMark를 실제 측정해 설계 근거로 남긴다.
