# \[FPGA\] Verilog HDL 기본 문법과 조합·순차논리회로

> 날짜: 2026-10-14
> 원본 노션: [링크](https://app.notion.com/p/FPGA-Verilog-HDL-3f81d46c18fc809e9c38dc9cfda5766b)

<!-- notion-page-id: 3f81d46c18fc809e9c38dc9cfda5766b -->
<!-- notion-title: "[FPGA] Verilog HDL 기본 문법과 조합·순차논리회로" -->

---

<a id="notion-3f81d46c18fc80c196a3d44d2f06e348"></a>

# \[FPGA\] Verilog 기본 문법과 조합·순차논리회로

<a id="notion-3f81d46c18fc800aad2bc84949d1a212"></a>

## HDL 기본 개념

- \*HDL (Hardware Description Language)\*\*은 디지털 논리회로를 문자로 표현하는 언어이다.
- Verilog 문법은 C와 비슷하지만 **프로그래밍 언어처럼 생각하면 안 됨**
- C: 명령을 순차적으로 실행
- HDL: 여러 하드웨어가 **병렬로 동시에 동작**
- HDL 설계 시 코드만 보는 것이 아니라 **어떤 회로가 만들어지는지 생각하는 것이 중요**

```text
C   : Source → Compile → 실행파일
HDL : Source → Compile → Simulation → Synthesis → Hardware
```

---

<a id="notion-3f81d46c18fc804f8529c09fb8903619"></a>

## Verilog 논리값

| 값 | 의미 |
| --- | --- |
| `0` | Logic 0 |
| `1` | Logic 1 |
| `x` | Unknown |
| `z` | High-Impedance |

`x`는 값이 결정되지 않은 상태, `z`는 회로가 연결되지 않은 것과 같은 High-Impedance 상태이다.

---

<a id="notion-3f81d46c18fc8066bb48dc00417d687c"></a>

## 상수 표현

기본 형식:

```text
<비트 수>'<진수><값>
```

진수:

- `b`: Binary
- `d`: Decimal
- `h`: Hexadecimal
- `o`: Octal

예:

```text
4'b0101    // 4bit 이진수 0101
7'd8       // 7bit 십진수 8 = 0001000
16'd255    // 16bit 십진수 255
12'h3AD    // 12bit 16진수 3AD
```

`'` 앞의 숫자는 **값이 아니라 비트 수**를 의미한다.

---

<a id="notion-3f81d46c18fc8055b653f5a5084cc6a0"></a>

## wire와 reg

<a id="notion-3f81d46c18fc801ab027c829e5d63cc6"></a>

### wire

회로의 \*\*물리적인 연결선(Net)\*\*을 표현한다.

```text
wire y;
assign y = ~a;
```

- 값을 저장하지 않음
- 계속 다른 회로에 의해 Drive되어야 함
- 모듈 간 연결에 사용
- `assign`으로 만든 조합논리 출력에 사용
- `input`은 기본적으로 wire 속성

<a id="notion-3f81d46c18fc80e68847cbc9f149a865"></a>

### reg

`always`, `initial` 등의 절차 블록에서 값을 할당받는 자료형이다.

```text
reg out;
```

`reg`라는 이름 때문에 무조건 Register나 Flip-Flop이 만들어지는 것은 아니다.

- 순차논리에서 사용 → Flip-Flop 등으로 합성 가능
- 조합논리에서 사용 → 논리 게이트나 연결 구조로 합성 가능

즉 <strong>`reg`</strong>**라는 문법만 보고 실제 FF라고 판단하면 안 됨**.

---

<a id="notion-3f81d46c18fc807fa983dcf512b7e823"></a>

## Vector

여러 비트를 하나의 신호로 묶을 때 `[ ]`를 사용한다.

```text
wire [3:0] data;
reg  [7:0] value;
```

```text
[3:0] → 4bit
[6:0] → 7bit
[7:0] → 8bit
```

각 비트도 개별 접근 가능하다.

```text
data[0]
data[3]
```

---

<a id="notion-3f81d46c18fc80588c92f5b4c9a61839"></a>

## Verilog 모델링 방식

<a id="notion-3f81d46c18fc80968724e709f165573e"></a>

### Dataflow Modeling

`assign`을 사용해 **데이터 흐름을 수식으로 표현**한다.

간단한 조합논리에 주로 사용한다.

```text
assign y = a & b;
```

<a id="notion-3f81d46c18fc80ccb9cfcb4219b6209f"></a>

### Behavioral Modeling

`always`와 `if`, `case` 등을 이용해 회로의 동작을 표현한다.

```text
always @(*) begin
    if (sel)
        out = a;
    else
        out = b;
end
```

복잡한 조합논리를 작성할 때 유용하며, 조합논리에서는 모든 입력 변화를 감지해야 한다. `always @(*)`를 사용하면 관련 입력 신호를 자동으로 감지할 수 있다.

---

<a id="notion-3f81d46c18fc80a3a4deea4b60b2acaa"></a>

## Module

`module`은 Verilog 설계의 기본 블록 단위이다.

```text
module module_name (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = a & b;

endmodule
```

- `module`로 시작
- `endmodule`로 종료
- `input`: 입력
- `output`: 출력
- `inout`: 양방향 포트

---

<a id="notion-3f81d46c18fc807c8c93c26f658d2707"></a>

## Module Instantiation

이미 만든 모듈을 다른 모듈 내부에서 사용하여 더 큰 회로를 구성할 수 있다.

```text
Top Module
 ├─ Sub Module
 ├─ Sub Module
 └─ Sub Module
```

예를 들어 1bit Full Adder 여러 개를 연결하면 4bit, 7bit Full Adder 같은 구조를 만들 수 있다.

<a id="notion-3f81d46c18fc80218353c904e2951f67"></a>

### Named Port Mapping

```text
full_adder u_full_adder_0 (
    .a   (a[0]),
    .b   (b[0]),
    .cin (carry[0]),
    .sum (sum[0]),
    .cout(carry[1])
);
```

형식:

```text
.하위모듈_port(현재모듈_signal)
```

포트 이름을 직접 지정하므로 연결 관계를 확인하기 쉽다. 자료에서는 Ordered Port 방식과 Named Port 방식을 구분하며, Named Port는 포트 이름과 연결 신호를 명시적으로 지정한다.

---

<a id="notion-3f81d46c18fc80269d46c99e30bafd08"></a>

## 조합논리회로와 순차논리회로

| 구분 | 조합논리회로 | 순차논리회로 |
| --- | --- | --- |
| 상태 저장 | X | O |
| Clock | 사용하지 않음 | 주로 사용 |
| 출력 변화 | 입력 변화에 따라 | Clock Edge를 기준으로 |
| 예 | Gate, Adder, MUX, Decoder | FF, Register, Counter, FSM |

조합논리는 현재 입력으로 출력이 결정되고, 순차논리는 Flip-Flop/Register 등을 이용해 이전 상태를 저장한다.

---

<a id="notion-3f81d46c18fc803e8810c78797bf13e2"></a>

## 조합논리회로 작성

<a id="notion-3f81d46c18fc8031ac27ce8384cbdfc8"></a>

### assign 사용

간단한 조합논리는 주로 `assign`을 사용한다.

```text
wire out;

assign out = sel ? a : b;
```

<a id="notion-3f81d46c18fc808599b0d276a780b276"></a>

### always 사용

조건이 복잡하면 `always`와 `if`, `case`를 사용할 수 있다.

```text
reg out;

always @(*) begin
    if (sel)
        out = a;
    else
        out = b;
end
```

조합논리 `always` 안에서는 일반적으로 \*\*Blocking Assignment `=`\*\*를 사용한다.

---

<a id="notion-3f81d46c18fc8022a97ae54e80b6085c"></a>

## Latch 발생 주의

⚠️ **중요**

조합논리 `always`에서 `if` 또는 `case`의 모든 경우에 출력값을 지정하지 않으면, Verilog는 **이전 값을 유지해야 하는 것으로 해석**할 수 있다.

이 경우 의도하지 않은 **Latch**가 합성될 수 있다.

잘못된 예:

```text
always @(*) begin
    if (en)
        out = a;
end
```

`en = 0`일 때 `out`을 어떻게 할지 정의되지 않았다.

방지 방법:

```text
always @(*) begin
    if (en)
        out = a;
    else
        out = 0;
end
```

또는 블록 시작에서 기본값을 먼저 지정한다.

```text
always @(*) begin
    out = 0;

    if (en)
        out = a;
end
```

즉 **조합논리는 모든 입력 조건에서 출력값이 결정되어야 한다.**

---

<a id="notion-3f81d46c18fc803489afd12b9d29fe10"></a>

## 순차논리회로

순차논리는 Clock Edge를 기준으로 값을 저장한다.

대표적인 D Flip-Flop:

```text
reg q;

always @(posedge clk)
    q <= d;
```

의미:

```text
Clock Rising Edge
       ↓
D 값 → Flip-Flop에 저장 → Q 출력
```

순차논리에서는 일반적으로 \*\*Non-blocking Assignment `<=`\*\*를 사용한다.

---

<a id="notion-3f81d46c18fc80cd8186e921d9d78159"></a>

## Reset

<a id="notion-3f81d46c18fc8082a292df4d868cd996"></a>

### 비동기 Reset

Clock과 관계없이 Reset이 들어오면 즉시 Reset된다.

```text
always @(posedge clk or negedge rst) begin
    if (!rst)
        q <= 0;
    else
        q <= d;
end
```

`negedge rst`가 있으므로 `rst`가 `1 → 0`으로 변할 때도 블록이 동작한다.

<a id="notion-3f81d46c18fc80fcb3b4faed978b45f3"></a>

### Enable

```text
always @(posedge clk or negedge rst) begin
    if (!rst)
        q <= 0;
    else if (en)
        q <= d;
end
```

- `en = 1` → Clock Edge에서 새로운 `d` 저장
- `en = 0` → 기존 값 유지

---

<a id="notion-3f81d46c18fc80509a8bc941c8148016"></a>

## Blocking과 Non-blocking

<a id="notion-3f81d46c18fc803abc46d44bfa2744e1"></a>

### Blocking `=`

문장이 작성된 순서에 따라 값이 즉시 변경된다.

```text
a = b;
b = a;
```

주로:

```text
조합논리 always
Test Bench
```

에서 사용한다.

<a id="notion-3f81d46c18fc80fe85f8df94ab372dc4"></a>

### Non-blocking `<=`

Clock Edge 시점의 오른쪽 값을 기준으로 각 레지스터의 갱신이 예약된다.

```text
q0 <= d;
q1 <= q0;
q2 <= q1;
q3 <= q2;
```

이 구조는 4개의 Flip-Flop이 연결된 Shift Register가 된다.

**기본 규칙**

```text
조합논리 → =
순차논리 → <=
```

---

<a id="notion-3f81d46c18fc80a28a37fee8ca999bc3"></a>

## 출력 신호의 Driver

하나의 신호를 여러 `always` 블록이나 여러 회로에서 동시에 출력하려 하면 **Multiple Driver** 문제가 발생할 수 있다.

따라서 일반적인 RTL 설계에서는 하나의 출력 신호를:

```text
하나의 assign
또는
하나의 always 블록
```

에서 구동하도록 작성한다.

---

<a id="notion-3f81d46c18fc801aa251f3f28a1fbcbb"></a>

## Test Bench

Test Bench는 실제 FPGA에 들어가는 회로가 아니라 **DUT를 Simulation으로 검증하기 위한 가상의 실험 환경**이다.

```text
Stimulus Generator
       ↓
      DUT
       ↓
Response / Waveform
```

- **Stimulus Generator**: 입력 신호 생성
- <strong>DUT (Design Under Test)</strong>: 실제 검증 대상 회로
- **Monitor**: DUT 출력 및 Waveform 확인

Test Bench 자체는 합성하지 않으므로 다음과 같은 Simulation 전용 문법을 사용할 수 있다.

```text
initial
#10
$display
$monitor
$stop
```

Test Bench에서는 일반적으로:

```text
DUT 입력  → reg
DUT 출력  → wire
```

로 선언한다.

---

<a id="notion-3f81d46c18fc806bbd52cf85ced61d5b"></a>

## RTL 작성 시 기본 구분

| 목적 | 작성 방식 | 출력 자료형 | 할당 |
| --- | --- | --- | --- |
| 간단한 조합논리 | `assign` | `wire` | `=` |
| 복잡한 조합논리 | `always @(*)` | `reg` | `=` |
| 순차논리 | `always @(posedge/negedge ...)` | `reg` | `<=` |
| Test Bench | `initial`, `always` 등 | 입력 `reg`, 출력 `wire` | 주로 `=` |

코드를 작성할 때는 문법 자체보다 **이 코드가 실제로 어떤 조합논리, Flip-Flop, Register, 연결선으로 합성되는지 생각하는 것이 핵심**이다.

<a id="notion-3f81d46c18fc80f0a355fac112fb2189"></a>

## 요약 정리

- **HDL**: 하드웨어를 문자로 표현하는 언어, 병렬 동작
- **wire**: 신호 연결용 Net, 값 저장 X
- **reg**: `always` 등에서 값을 할당받는 자료형
- **Vector**: `[n:0]` 형태로 여러 bit 표현
- **상수**: `<비트수>'<진수><값>` 형태
- **Module**: Verilog 설계의 기본 블록
- **Instantiation**: 하위 Module을 연결해 더 큰 회로 구성
- **조합논리**: 상태 저장 X, 입력 변화가 출력에 반영
- <strong>`assign`</strong>: 간단한 조합논리, 출력 `wire`
- <strong>`always @(*)`</strong>: 복잡한 조합논리, 출력 `reg`
- **Latch 방지**: 조합논리에서 모든 조건의 출력값 지정
- **순차논리**: Clock Edge에서 상태 저장
- **Flip-Flop**: Clock Edge에서 입력값 저장
- <strong>Blocking</strong> <strong>`=`</strong>: 조합논리·Test Bench에서 주로 사용
- <strong>Non-blocking</strong> <strong>`<=`</strong>: 순차논리에서 사용
- **Reset**: Flip-Flop 값을 초기 상태로 설정
- **Test Bench**: DUT의 입력을 생성하고 Simulation으로 동작 검증
