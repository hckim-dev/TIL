# \[FPGA\] FSM과 Moore · Mealy FSM

> 날짜: 2026-10-19
> 원본 노션: [링크](https://app.notion.com/p/FPGA-FSM-Moore-Mealy-FSM-3fd1d46c18fc80d5a824f71ad0c58b1d)

<!-- notion-page-id: 3fd1d46c18fc80d5a824f71ad0c58b1d -->
<!-- notion-title: "[FPGA] FSM과 Moore · Mealy FSM" -->

---

<a id="notion-3fe1d46c18fc80c2bc46f8ce710e7432"></a>

# \[FPGA\] FSM과 Moore · Mealy FSM

<a id="notion-3fe1d46c18fc8008ae56de23e3cd6536"></a>

## FSM이란?

FSM(Finite State Machine, 유한 상태 머신)은 **유한한 개수의 상태(State)를 가지고 상태를 전환하면서 동작하는 순차회로**이다.

- 현재 상태를 기억함
- 입력과 현재 상태에 따라 다음 상태가 결정됨
- 현재 상태 또는 현재 상태 + 입력에 따라 출력이 결정됨

기본 흐름:

`Input + Present State → Next State → Clock Edge → 새로운 Present State`

조합회로와 달리 \*\*현재 상태를 저장하는 State Register(F/F)\*\*가 필요하다.

---

<a id="notion-3fe1d46c18fc80609700c2cfd3ccee79"></a>

## FSM의 기본 구조

FSM은 크게 3개의 부분으로 구성된다.

<a id="notion-3fe1d46c18fc8009aeeacb385c7aad6b"></a>

### Next State Logic

조합회로.

`Input + Present State → Next State`

현재 상태와 입력을 이용하여 다음 상태를 계산한다.

<a id="notion-3fe1d46c18fc803a9277c6bf93593d2e"></a>

### State Register

순차회로.

`Next State → Clock Edge → Present State`

Clock Edge에서 다음 상태를 현재 상태로 저장한다.

<a id="notion-3fe1d46c18fc8040b690e333cac29a7b"></a>

### Output Logic

출력을 결정하는 조합회로.

- Moore → 현재 상태만 사용
- Mealy → 현재 상태 + 입력 사용

---

<a id="notion-3fe1d46c18fc806687fde57f62550231"></a>

## Present State와 Next State

- `Present State` → 현재 저장되어 있는 상태
- `Next State` → 다음 Clock Edge에서 이동할 상태

예:

현재 채널이 `CH3`이고 UP 버튼을 누르면

`Present State = CH3`

`Next State = CH4`

Next State가 계산되어도 상태가 즉시 바뀌는 것은 아니며, **Clock Edge에서 State Register가 갱신될 때 Present State가 CH4로 변경된다.**

---

<a id="notion-3fe1d46c18fc80d38803cb2b0564ca77"></a>

## TV Channel FSM 예제

채널:

`CH0 ~ CH9`

UP:

`CH0 → CH1 → CH2 → ... → CH9 → CH0`

DN:

`CH0 → CH9 → CH8 → ... → CH1 → CH0`

즉 다음 상태는 **현재 채널 상태 + UP/DN 입력**으로 결정된다.

---

<a id="notion-3fe1d46c18fc80aa8f6de8c04ed6f8c4"></a>

## Moore FSM

Moore Machine:

`Output = f(State)`

출력이 **현재 상태만으로 결정**된다.

특징:

- 입력이 직접 출력에 영향을 주지 않음
- 상태가 변경되면 출력이 변경됨
- 상태가 유지되면 출력도 유지됨
- 출력이 비교적 안정적
- 같은 기능의 Mealy FSM보다 상태가 많아질 수 있음

<a id="notion-3fe1d46c18fc802388d3fae38b4a4dae"></a>

### 상태도 표기

출력을 상태 내부에 표시한다.

예:

`S3 / y=1`

→ 현재 상태가 S3이면 `y=1`

---

<a id="notion-3fe1d46c18fc808e87b6dd4265b73b7f"></a>

## Mealy FSM

Mealy Machine:

`Output = f(State, Input)`

출력이 **현재 상태 + 현재 입력**으로 결정된다.

특징:

- 입력이 출력에 직접 영향을 줄 수 있음
- 상태가 바뀌지 않아도 입력 변화만으로 출력이 변할 수 있음
- 같은 Cycle 안에서 빠르게 반응 가능
- Moore보다 상태 수를 줄일 수 있음
- 입력 Glitch가 출력으로 전달될 가능성이 있음

<a id="notion-3fe1d46c18fc80e8960cc02c8d7a0c0e"></a>

### 상태도 표기

전이선에:

`입력 / 출력`

형태로 표시한다.

예:

`1 / 1`

→ 해당 상태에서 입력이 `1` 이면 전이와 함께 출력이 `1`

---

<a id="notion-3fe1d46c18fc80dc8884fab7bce2a1ff"></a>

## Moore와 Mealy 핵심 비교

| 구분 | Moore | Mealy |
| --- | --- | --- |
| 출력 결정 | 현재 상태 | 현재 상태 + 입력 |
| 출력식 | `Y = g(S)` | `Y = g(S, X)` |
| 상태도 출력 표기 | 상태 내부 | 전이선 |
| 상태 수 | 상대적으로 많음 | 상대적으로 적음 |
| 입력 반응 | 상태 변경 후 출력 반영 | 입력 변화에 같은 Cycle 반응 가능 |
| Glitch 영향 | 상대적으로 적음 | 입력 Glitch 영향 가능 |

⚠️ 중요

**Moore와 Mealy 모두 State 자체는 Clock Edge에서 변경된다.**

차이는 State가 바뀌는 속도가 아니라 **출력이 무엇을 기준으로 바뀌는지**이다.

`Moore → 상태가 바뀌어야 출력이 바뀜`

`Mealy → 상태가 그대로여도 입력이 바뀌면 출력이 바뀔 수 있음`

---

<a id="notion-3fe1d46c18fc803ea4dcccb7492e44cd"></a>

## Moore와 Mealy의 대표적인 활용

Moore가 잘 어울리는 경우:

- 신호등 Controller
- 모터 동작 단계 제어
- 자판기 상태 제어
- 안정적인 출력이 중요한 제어회로

예:

`State = GREEN → Green LED ON`

Mealy가 잘 어울리는 경우:

- Serial Pattern Detector
- 즉시 ACK/READY 응답
- Handshake Logic
- 입력에 빠르게 반응해야 하는 제어

예:

`현재 "10"까지 검출 + 입력 1 → 즉시 "101" 검출`

실제 설계에서는 Moore와 Mealy 방식을 혼합해서 사용하는 경우도 있다.

---

<a id="notion-3fe1d46c18fc8068872ac032135b6ae0"></a>

## 상태 다이어그램(State Diagram)

FSM의 상태와 상태 전이를 그림으로 표현한 것.

- 원 → State
- 화살표 → State Transition
- Moore 출력 → 상태 안에 표시
- Mealy 출력 → 전이선에 `입력 / 출력` 표시

상태도 자체가 정해진 공식은 아니며 **구현하려는 기능에 따라 직접 설계한다.**

---

<a id="notion-3fe1d46c18fc8017be04da95944d5b26"></a>

## 상태표(State Table)

FSM 동작을 표로 나타낸 것.

기본 구성:

`입력 | 현재 상태 | 다음 상태 | 출력`

일반 Truth Table과 달리 FSM에서는 **현재 상태와 다음 상태**가 포함된다.

---

<a id="notion-3fe1d46c18fc80a0b461f7b9b6b7cebf"></a>

## Verilog FSM 기본 구현

<a id="notion-3fe1d46c18fc8063862cc302ded7bc44"></a>

### State Register

순차회로:

`always @(posedge clk ...)`

- Clock Edge에서 상태 갱신
- Nonblocking Assignment `<=` 사용

예:

`curr_state <= next_state;`

<a id="notion-3fe1d46c18fc8022a6e7d7037810b12c"></a>

### Next State Logic

조합회로:

`always @(*)`

- 현재 상태와 입력으로 Next State 계산
- Blocking Assignment `=` 사용

예:

`next_state = ...;`

⚠️ 조합회로에서는 **모든 실행 경로에서 출력값이 할당되어야 Latch가 발생하지 않는다.**

예를 들어 `case`의 모든 상태와 `default`에서 `next_state`를 할당한다면 별도의

`next_state = curr_state;`

기본값은 반드시 필요한 것은 아니다.

---

<a id="notion-3fe1d46c18fc8026ba82fc390594ff92"></a>

## `101` Sequence Detector

Serial Input에서 `101` 패턴을 찾는 FSM.

중첩(Overlapping)을 허용하면:

`10101`

에서 `101`이 두 번 검출된다.

```text
10101
^^^
  ^^^
```

---

<a id="notion-3fe1d46c18fc80bea9d9eb0ba9f886e6"></a>

## Moore 방식의 `101` 검출

상태:

- `S0` → 아무것도 검출되지 않음
- `S1` → `"1"`까지 검출
- `S2` → `"10"`까지 검출
- `S3` → `"101"` 검출 완료

상태 전이:

`S0: x=1 → S1 / x=0 → S0`

`S1: x=1 → S1 / x=0 → S2`

`S2: x=1 → S3 / x=0 → S0`

`S3: x=1 → S1 / x=0 → S2`

S3에서만:

`y = 1`

<a id="notion-3fe1d46c18fc80e39201f7c79d056af0"></a>

### S3에서 S0가 아닌 S1/S2로 이동하는 이유

중첩 검출을 위해 **이미 입력받은 Bit 중 다음 패턴에 재사용할 수 있는 부분을 남기기 때문**이다.

`101 + 1 = 1011`

마지막 `1`을 새로운 `"101"`의 시작으로 사용할 수 있으므로:

`S3 + x=1 → S1`

`101 + 0 = 1010`

마지막 `10`을 새로운 `"101"`의 시작으로 사용할 수 있으므로:

`S3 + x=0 → S2`

즉 상태 전이를 외우는 것이 아니라:

**현재 입력의 끝부분이 찾고 있는 Pattern의 어디까지 일치하는지 판단하여 다음 상태를 결정한다.**

---

<a id="notion-3fe1d46c18fc806ca020e296f9761a27"></a>

## Mealy 방식의 `101` 검출

상태:

- `S0` → IDLE
- `S1` → `"1"` 검출
- `S2` → `"10"` 검출

S2 상태에서:

`x = 1`

이 들어오는 순간 `"101"`이 완성되므로 바로:

`y = 1`

을 출력한다.

따라서 Moore처럼 `"101"` 검출을 나타내는 별도의 S3 상태가 필요하지 않다.

---

<a id="notion-3fe1d46c18fc80e19a4cf4d31233d13c"></a>

## Moore와 Mealy의 `101` 검출 차이

입력:

`1 → 0 → 1`

Mealy:

`S2 + x=1 → 즉시 y=1`

Moore:

`S2 + x=1 → S3 → y=1`

즉 Mealy는 마지막 `1`이 들어오는 **같은 Cycle에 출력**할 수 있고, Moore는 `"101"`을 나타내는 State에 들어간 뒤 출력된다.

---

<a id="notion-3fe1d46c18fc806da68ad99e92e9662b"></a>

## 실제 FPGA에서 Moore와 Mealy 출력 차이

Moore에서 S3에 들어가면:

`State = S3 → y=1`

상태가 다음 입력까지 유지된다면 LED도 계속 HIGH 상태를 유지한다.

Mealy에서는:

`State = S2 + x=1 → y=1`

처럼 입력 조건이 만족되는 동안 바로 출력되기 때문에 출력 Pulse가 매우 짧을 수 있다.

따라서 실제 Basys3에서:

- Moore LED → 눈으로 확인하기 쉬움
- Mealy LED → Pulse가 너무 짧으면 눈으로 확인하기 어려울 수 있음

이 경우 LED 확인용으로 Pulse Stretch 또는 별도 Register/Latch를 추가할 수 있다.

---

<a id="notion-3fe1d46c18fc805da79cede8e0e10363"></a>

## 버튼으로 Serial Data 입력하기

실제 Basys3에서 `101`을 입력하려면 버튼을 데이터 입력으로 사용할 수 있다.

예:

`btnU → 1 입력`

`btnD → 0 입력`

따라서:

`btnU → btnD → btnU`

는:

`1 → 0 → 1`

을 의미한다.

Moore와 Mealy를 비교하려면 **같은 입력 Data를 두 FSM에 동시에 전달**한다.

```text
             ┌→ Moore FSM → LED0
Button Input ┤
             └→ Mealy FSM → LED1
```

두 FSM이 동일한 입력을 받기 때문에 출력 시점의 차이를 비교할 수 있다.

---

<a id="notion-3fe1d46c18fc80a6ae1ed4532009a9a1"></a>

## Data와 Step 신호

버튼 입력에서는 다음 두 정보를 구분해야 한다.

`data(x)` → 어떤 값을 입력했는가 (`0` 또는 `1`)

`step` → 새로운 Bit가 지금 입력되었는가

예:

btnU를 한 번 누르면:

`x = 1`

`step = 1` (1 Clock)

그 후 버튼을 계속 누르고 있어도:

`x = 1`

`step = 0`

FSM에서는:

`step = 1`

일 때만 상태를 갱신한다.

예:

`else if (step) curr_state <= next_state;`

<a id="notion-3fe1d46c18fc80128803de7b5300989f"></a>

### Step이 필요한 이유

Debounce된 `x=1`이 계속 유지되면 FSM이 100 MHz Clock마다 같은 `1`을 계속 새로운 입력처럼 처리하게 된다.

```text
x    = 1 1 1 1 1 1 ...
step = 1 0 0 0 0 0 ...
```

따라서 버튼 한 번을 **정확히 한 개의 Serial Bit 입력**으로 처리하려면 Step과 같은 Valid Pulse가 필요하다.

특히 `x=0`만으로는:

- 새로운 `0`을 입력한 것인지
- 아무 입력도 없어서 계속 `0`인 것인지

구분할 수 없기 때문에 Step이 필요하다.

---

<a id="notion-3fe1d46c18fc809797bbd12438b9fa80"></a>

## Rising Edge 검출

버튼의 이전 값을 저장해 두고:

`현재 버튼 = 1`

`이전 버튼 = 0`

인 경우만 검출하면 Low → High Rising Edge를 한 번만 감지할 수 있다.

예:

`btn && !prev_btn`

버튼을 계속 누르고 있어도 Rising Edge는 처음 한 번만 발생한다.

---

<a id="notion-3fe1d46c18fc8009a5aad9280913b6a6"></a>

## Nonblocking Assignment와 이전 값

순차회로에서:

`prev_btn <= btn;`

다음 줄에서:

`if (btn && !prev_btn)`

를 사용하면 `prev_btn`은 아직 **이전 Clock의 값**을 사용한다.

`<=`는 다음 Clock에서 적용된다는 뜻이 아니라:

**현재 Clock Edge에서 새로운 값을 예약하고, 현재 계산이 끝난 뒤 갱신한다.**

따라서 Rising Edge 검출이 가능하다.

---

<a id="notion-3fe1d46c18fc80c6ae34e2162a15c8f6"></a>

## Test Bench에서 입력과 출력 확인 시점

DUT가 `posedge clk`에서 상태를 갱신한다면 TB에서는 보통:

`negedge → 입력 변경`

`posedge → DUT 상태 갱신`

`posedge 이후 → 출력 확인`

방식을 사용한다.

입력을 `negedge`에서 변경하면 다음 `posedge`까지 입력이 안정된 상태로 유지되어 DUT와 TB 사이의 Race Condition을 줄일 수 있다.

---

<a id="notion-3fe1d46c18fc80039487eeefcce9f2a7"></a>

## Test Bench의 `#1`

예:

`@(posedge clk);`

`#1;`

`#1`은 단순히 쉬기 위한 것이 아니라 **Nonblocking Assignment와 출력 갱신이 완료된 뒤 값을 확인하기 위한 짧은 Simulation Delay**이다.

`timescale 1ns / 1ps`

이면:

`#1 = 1 ns`

이다.

---

<a id="notion-3fe1d46c18fc808fb7fbf283f06916f0"></a>

## Moore와 Mealy Test Bench의 차이

Moore 출력은 상태가 Clock Edge에서 바뀐 뒤 결정되므로:

`입력 변경 → posedge → 출력 확인`

방식이 자연스럽다.

Mealy 출력은 현재 상태 + 입력의 조합논리이므로:

`입력 변경 → 출력 즉시 확인 → posedge에서 State 갱신`

순서로 확인할 수 있다.

즉 Mealy 출력을 Moore처럼 항상 posedge 이후에만 검사하면 **짧게 발생한 출력 Pulse를 놓칠 수 있다.**

---

<a id="notion-3fe1d46c18fc805bb5d9f054bebccfd2"></a>

## Test Bench 비교 연산자

Test Bench에서는:

`!==`

를 사용할 수 있다.

`!=` → 일반적인 다름 비교

`!==` → `X`, `Z`까지 포함하여 정확하게 다름을 비교

따라서 PASS/FAIL 검사에서는 `!==`, `===`를 사용하면 Simulation의 `X/Z` 상태까지 확인할 수 있다.

---

<a id="notion-3fe1d46c18fc8083954cdc40bfb77ea0"></a>

## `task automatic`

Verilog Test Bench의 반복 동작은 `task`로 만들 수 있다.

예:

`task automatic apply_bit;`

`automatic`은 Task가 호출될 때마다 인자와 내부 변수를 독립적으로 사용하도록 한다.

Verilog-2001부터 지원되므로 순수 Verilog `.v`에서도 사용할 수 있다.

---

<a id="notion-3fe1d46c18fc80019d20ca7578b079e0"></a>

## Verilog와 SystemVerilog의 FSM 상태 정의

현재 사용하는 순수 Verilog에서는 보통:

`localparam`

으로 FSM State를 정의한다.

예:

`localparam integer S0 = 2'b00;`

SystemVerilog에서는 `enum`을 사용할 수 있어 FSM 상태를 더 명확하게 표현할 수 있다.

즉 `enum`은 FPGA의 특별한 기능이 아니라 **FSM State를 더 읽기 쉽게 표현하기 위한 언어 기능**이다.

---

<a id="notion-3fe1d46c18fc804dbcfcd27d56d7116d"></a>

## Gray Code Counter

2bit Gray Counter:

`00 → 01 → 11 → 10 → 00 → ...`

- `en = 1` → 다음 상태로 이동
- `en = 0` → 현재 상태 유지

Counter 역시 상태가 일정한 규칙으로 이동하는 FSM으로 표현할 수 있다.

---

<a id="notion-3fe1d46c18fc80818c07c69cf74c2d3a"></a>

## FSM 활용 예

FSM은 **현재 상태를 기억하면서 입력에 따라 다음 동작을 결정해야 하는 제어회로**에 사용한다.

대표적인 예:

- 신호등 Controller
- 자판기
- TV Channel Controller
- LED 순차 제어
- UART / SPI / I2C 제어
- Protocol Controller
- Handshake Logic
- Motor Control
- Serial Pattern Detector

핵심은 특정 `101` 검출기를 외우는 것이 아니라:

**복잡한 동작을 여러 State로 나누고, 어떤 조건에서 다음 State로 이동할지를 설계하는 방법을 익히는 것**이다.

---

<a id="notion-3fe1d46c18fc80ed89e3f98b889c4e1b"></a>

## 자판기 FSM 예제

조건:

- 커피 가격: 300원
- 100원 동전만 사용
- 200원 이하에서 버튼 → 동전 반환
- 300원에서 버튼 → 커피 출력
- 300원을 초과하여 동전 입력 → 반환
- `w100`과 `btn`이 동시에 들어오면 `w100` 우선

입력:

- `w100` → 100원 입력
- `btn` → 커피 버튼

출력:

- `sale` → 커피 출력
- `ret` → 동전 반환

상태:

- `st0`
- `st100`
- `st200`
- `st300`

현재 투입 금액을 State로 기억하고 입력에 따라 상태를 이동하거나 출력을 발생시킨다.
