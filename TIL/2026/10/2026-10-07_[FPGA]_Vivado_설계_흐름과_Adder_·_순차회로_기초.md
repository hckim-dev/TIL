# \[FPGA\] Vivado 설계 흐름과 Adder · 순차회로 기초

> 날짜: 2026-10-07
> 원본 노션: [링크](https://app.notion.com/p/FPGA-Vivado-Adder-3f11d46c18fc801bbefaece8b6089a37)

<!-- notion-page-id: 3f11d46c18fc801bbefaece8b6089a37 -->
<!-- notion-title: "[FPGA] Vivado 설계 흐름과 Adder · 순차회로 기초" -->

---

<a id="notion-3f21d46c18fc802db4d5cfb71a839851"></a>

# Vivado 기본 설계 흐름

```text
Project 생성
→ Verilog RTL 작성
→ XDC Constraints 설정
→ Test Bench / Simulation
→ Synthesis
→ Implementation
→ Generate Bitstream
→ Hardware Manager
→ FPGA Programming
→ 실제 Board 동작 확인
```

Vivado에서는 RTL 작성부터 Simulation, 합성, 배치·배선, Bitstream 생성, 실제 FPGA Programming 순서로 진행한다.

<a id="notion-3f21d46c18fc80d5ae39fd904d9453c1"></a>

## Basys3 환경

Vivado 2026.1에서는 Basys3 Board File을 Vivado Store에서 설치할 수 있다.

```text
Tools
→ Vivado Store
→ Boards
→ Basys3
→ Install
```

- **Board File**: Vivado가 Basys3 보드를 인식하도록 함
- **XDC**: Verilog의 Port를 실제 FPGA Pin과 연결

```text
Verilog Port
→ XDC
→ FPGA Pin
→ Switch / LED / Button / Clock
```

<a id="notion-3f21d46c18fc805b9ea8d5db48743d5e"></a>

# Verilog 기본 구조

```text
module gates (
    input  wire [1:0] sw,
    output wire [5:0] led
);

    assign led[0] =  sw[0] & sw[1];
    assign led[1] =  sw[0] | sw[1];

endmodule
```

<a id="notion-3f21d46c18fc8049beb9c4f8ef5f7067"></a>

## `wire`

`wire`는 값을 저장하는 변수가 아니라 \*\*신호를 전달하는 연결선(Net)\*\*이다.

```text
input wire a;
```

Verilog의 `input`은 기본적으로 `wire`이므로 다음도 가능하다.

```text
input a;
```

학습 단계에서는 신호의 성격을 명확하게 보기 위해 `wire`를 명시하는 것이 이해하기 쉽다.

<a id="notion-3f21d46c18fc80d485bcd7da2928f08b"></a>

## `assign`

```text
assign y = a & b;
```

`assign`은 변수 선언이나 일회성 대입이 아니라 \*\*Continuous Assignment(연속 할당)\*\*이다.

```text
a ─┐
   AND ──→ y
b ─┘
```

즉 `a` 또는 `b`가 바뀌면 `y`도 계속 새로운 결과를 따라간다.

```text
assign cout = carry[4];
```

도 `carry[4]`와 `cout`을 계속 연결해 둔 것으로 이해하면 된다.

<a id="notion-3f21d46c18fc80e0bb24ddaef8da135b"></a>

# Bus

```text
input wire [1:0] sw;
```

→ 2bit Bus

```text
sw[1]
sw[0]
```

```text
output wire [5:0] led;
```

→ `led[0] ~ led[5]`, 총 6bit

<a id="notion-3f21d46c18fc807daa63fe2b65aeffbc"></a>

# Module Instantiation

상위 Module 안에서 하위 Module을 실제 회로 블록으로 연결해 사용하는 것.

```text
full_adder u_full_adder_0 (
    .a   (a[0]),
    .b   (b[0]),
    .cin (carry[0]),
    .sum (sum[0]),
    .cout(carry[1])
);
```

기본 형태:

```text
.하위모듈의_Port(상위모듈의_신호)
```

신호 방향은 Port의 `input / output`으로 결정된다.

```text
input
a[0] → a

output
cout → carry[1]
```

`u_`는 문법이 아니라 **Module Instance임을 나타내는 네이밍 컨벤션**이다.

```text
RTL 내부 Instance → u_...
Test Bench DUT     → dut
```

<a id="notion-3f21d46c18fc800895aadb52ee3b5b48"></a>

# Test Bench / Simulation

실제 FPGA에 Programming하기 전에 가상의 환경에서 회로 동작을 검증한다.

```text
Test Bench 작성
→ DUT 연결
→ Run Behavioral Simulation
→ Waveform 확인
```

- **DUT**: 검증할 실제 RTL Module
- **Test Bench**: DUT에 입력을 만들어 넣는 검증용 Module
- Test Bench 자체에는 외부 `input/output` Port가 없음

<a id="notion-3f21d46c18fc8025b9d9fda9aee2a6c9"></a>

## 기본 구조

```text
`timescale 1ns / 1ps

module tb_gates;

    reg  [1:0] sw;
    wire [5:0] led;

    gates dut (
        .sw  (sw),
        .led (led)
    );

    initial begin
        sw = 2'b00;
        #10 sw = 2'b01;
        #10 sw = 2'b10;
        #10 sw = 2'b11;
        #10 $finish;
    end

endmodule
```

<a id="notion-3f21d46c18fc804d8854efe1c29dce35"></a>

## Test Bench의 `reg / wire`

```text
reg  [1:0] sw;
wire [5:0] led;
```

- `reg`: Test Bench가 직접 값을 변경하는 DUT 입력
- `wire`: DUT가 만들어내는 출력을 받는 신호

<a id="notion-3f21d46c18fc80728e0ed9dbf8ddbc34"></a>

## 숫자 표현

```text
2'b01
```

```text
2  → Bit 수
b  → Binary
01 → 값
```

예:

```text
2'b00
2'b01
2'b10
2'b11
```

<a id="notion-3f21d46c18fc80939a4dc4e9aa7ab779"></a>

## `timescale`

```text
`timescale 1ns / 1ps
```

- `1ns`: Simulation 시간 단위
- `1ps`: Simulation 시간 정밀도

따라서:

```text
#10
```

→ Simulation 시간으로 **10ns 후 다음 동작 수행**

```text
0ns  : 00
10ns : 01
20ns : 10
30ns : 11
```

실제 FPGA가 10ns 동안 쉬는 것이 아니다.

<a id="notion-3f21d46c18fc8047baabd6e84b37339a"></a>

## `initial / $finish`

```text
initial begin
    ...
end
```

→ Simulation 시작 시 Test stimulus 생성

```text
$finish;
```

→ Simulation 종료

<a id="notion-3f21d46c18fc80a4af2cd28eeb743f83"></a>

# Synthesis / Implementation

<a id="notion-3f21d46c18fc80839876dc737c0e1f79"></a>

## Synthesis

```text
Verilog RTL
→ Logic 최적화
→ LUT / Flip-Flop 등 FPGA Resource로 Mapping
```

즉 **RTL을 실제 구현 가능한 논리회로 구조로 변환**한다.

<a id="notion-3f21d46c18fc80e28ba9e5e90b4590f2"></a>

## Implementation

합성된 회로를 실제 FPGA 내부 자원에 배치하고 연결한다.

```text
Place
→ FPGA 내부 자원의 위치 결정

Route
→ 자원 사이의 실제 연결 경로 결정
```

<a id="notion-3f21d46c18fc80a9b1b6e8deaf7b9d7d"></a>

# Bitstream / FPGA Programming

```text
Generate Bitstream
→ Hardware Manager
→ Open Target
→ Auto Connect
→ Program Device
```

`.bit` 파일을 FPGA에 Programming하면 즉시 회로가 구성된다.

FPGA의 일반 Configuration은 휘발성이므로 전원을 끄면 사라진다.

<a id="notion-3f21d46c18fc80eba110e4829004ef98"></a>

# Flash Memory Programming

전원을 다시 켰을 때 자동으로 회로가 구성되게 하려면 Flash Memory에 저장한다.

```text
JP1 → SPI Mode
→ Settings → Bitstream → -bin_file
→ Synthesis
→ Implementation
→ Generate Bitstream
→ Hardware Manager
→ Program Configuration Memory Device
→ .bin Programming
```

Flash는 비휘발성이므로 전원이 꺼져도 저장된 Configuration을 유지한다.

<a id="notion-3f21d46c18fc80b99a99c4effaba5e91"></a>

## `.bit` vs `.bin`

| 구분 | `.bit` | `.bin` |
| --- | --- | --- |
| 용도 | FPGA 직접 Programming | Flash Programming |
| 실행 | `Program Device` | `Program Configuration Memory Device` |
| 전원 OFF | FPGA 구성 소멸 | Flash 데이터 유지 |
| 전원 ON | 다시 Programming 필요 | SPI 설정 시 자동 구성 |

<a id="notion-3f21d46c18fc8093b7a7cefae5c412a8"></a>

# 조합회로와 순차회로

<a id="notion-3f21d46c18fc8017a6f8f21d86422148"></a>

## 조합회로

**현재 입력만으로 출력이 결정되는 기억소자가 없는 회로**

예:

- Logic Gate
- Half Adder
- Full Adder

<a id="notion-3f21d46c18fc800989afc4006627c0b0"></a>

## 순차회로

**현재 입력 + 이전 상태에 의해 출력이 결정되는 기억소자를 포함한 회로**

예:

- Flip-Flop
- Register
- Counter

<a id="notion-3f21d46c18fc801fbb82de4d1eb60b41"></a>

# Half Adder

두 개의 1bit 입력을 더하는 가장 기본적인 덧셈기.

```text
입력 : a, b
출력 : sum, cout
```

1bit + 1bit의 결과는 최대 `10₂`이므로 결과가 2bit까지 필요하다.

```text
1 + 1 = 10₂

cout = 1
sum  = 0
```

<a id="notion-3f21d46c18fc80b6a181fb105527ff77"></a>

## 회로

```text
assign sum  = a ^ b;
assign cout = a & b;
```

<a id="notion-3f21d46c18fc80e6bca3d5c9aa9f1c78"></a>

### `sum = XOR`

```text
a b | sum
0 0 |  0
0 1 |  1
1 0 |  1
1 1 |  0
```

현재 자리의 합은 XOR의 결과와 같다.

<a id="notion-3f21d46c18fc80cdb9ade51d52bcc935"></a>

### `cout = AND`

```text
a b | cout
0 0 |  0
0 1 |  0
1 0 |  0
1 1 |  1
```

Carry는 `1 + 1`일 때만 발생하므로 AND와 같다.

<a id="notion-3f21d46c18fc80fe9e5cd43b82777bba"></a>

# Full Adder

Half Adder는 `a + b`만 처리하지만 Full Adder는 **이전 자리에서 전달된 Carry까지 함께 계산**한다.

```text
Half Adder : a + b

Full Adder : a + b + cin
```

입력:

```text
a
b
cin
```

출력:

```text
sum
cout
```

<a id="notion-3f21d46c18fc80d2a6a8cc80bc336ceb"></a>

## Full Adder 논리식

```text
assign sum  = a ^ b ^ cin;
assign cout = (a & b) | (b & cin) | (a & cin);
```

<a id="notion-3f21d46c18fc80a68cd0ca9a09fea178"></a>

### `sum`

세 입력에서 `1`의 개수가 홀수일 때 `sum=1`.

→ XOR

<a id="notion-3f21d46c18fc801da365fd32ecdf5e79"></a>

### `cout`

세 입력 중 **2개 이상이 1이면 Carry 발생**.

```text
a와 b가 1      → a & b
b와 cin이 1    → b & cin
a와 cin이 1    → a & cin
```

이 중 하나라도 참이면 Carry가 발생하므로 OR로 연결한다.

```text
(a & b) | (b & cin) | (a & cin)
```

<a id="notion-3f21d46c18fc80c683a0f3a2256e4258"></a>

# Half Adder로 Full Adder 구성

Full Adder는 Half Adder 2개와 OR Gate로 구성할 수도 있다.

```text
a + b
 ↓
Half Adder 1
 ↓
중간 sum + cin
 ↓
Half Adder 2
 ↓
최종 sum

HA1 cout ─┐
          OR → cout
HA2 cout ─┘
```

즉:

```text
1차 : a + b
2차 : 중간 sum + cin
최종 Carry : 두 Half Adder의 Carry를 OR
```

<a id="notion-3f21d46c18fc80d9b327f80445e7b429"></a>

# 4bit Full Adder

1bit Full Adder를 4개 연결한다.

```text
cin
 ↓
FA0 → carry[1]
       ↓
      FA1 → carry[2]
             ↓
            FA2 → carry[3]
                   ↓
                  FA3 → cout
```

이처럼 Carry가 낮은 자리에서 높은 자리로 전달되는 구조를 **Ripple Carry Adder**라고 한다.

<a id="notion-3f21d46c18fc80b58cd6ffaa4b7ec2c7"></a>

## Carry Bus 구조

```text
wire [4:0] carry;

assign carry[0] = cin;
assign cout     = carry[4];
```

```text
carry[0] → 최초 cin
carry[1] → FA0 Carry
carry[2] → FA1 Carry
carry[3] → FA2 Carry
carry[4] → 최종 cout
```

<a id="notion-3f21d46c18fc80deb7eafdfc9715ed93"></a>

# Latch와 Flip-Flop

둘 다 데이터를 저장하는 기억소자지만 **입력값을 받아들이는 시점**이 다르다.

<a id="notion-3f21d46c18fc80fc9da0c6e43dbad17a"></a>

## Latch

**Level Triggered**

```text
EN = 1
→ D 변화가 Q에 계속 반영

EN = 0
→ Q 값 유지
```

<a id="notion-3f21d46c18fc8007b083c1fc0a75c364"></a>

## Flip-Flop

**Edge Triggered**

예: Rising Edge

```text
CLK 0 → 1 순간
→ D를 Q에 저장
→ 다음 Edge까지 Q 유지
```

핵심:

```text
Latch     → Level에 반응
Flip-Flop → Edge에 반응
```

<a id="notion-3f21d46c18fc8009a7ebc251ebd427c9"></a>

# Blocking / Non-blocking

<a id="notion-3f21d46c18fc80d2a81df809f8af6cd2"></a>

## Blocking `=`

```text
always @(posedge clk) begin
    q0 = d;
    q1 = q0;
    q2 = q1;
    q3 = q2;
end
```

위 문장이 값을 즉시 갱신하므로 아래 문장이 **갱신된 값을 사용할 수 있다.**

```text
q0 = d
↓
q1 = 새 q0
↓
q2 = 새 q1
↓
q3 = 새 q2
```

따라서 작성 순서가 결과에 영향을 줄 수 있다.

<a id="notion-3f21d46c18fc801f8b4eda51e42844b6"></a>

## Non-blocking `<=`

```text
always @(posedge clk) begin
    q0 <= d;
    q1 <= q0;
    q2 <= q1;
    q3 <= q2;
end
```

Clock Edge에서:

```text
RHS를 기존 값 기준으로 평가
→ 이후 LHS를 갱신
```

따라서:

```text
q0 ← 이전 d
q1 ← 이전 q0
q2 ← 이전 q1
q3 ← 이전 q2
```

가 되어 Shift Register처럼 한 단계씩 이동한다.

<a id="notion-3f21d46c18fc8024bb18d00c9f427c2d"></a>

## 기본 사용 기준

```text
조합논리 always 블록
→ Blocking (=)

Clock 기반 순차논리
→ Non-blocking (<=)
```

현재 단계에서는 이 기준으로 기억하면 된다.

<a id="notion-3f21d46c18fc80989996db2701492cf5"></a>

# 오늘 배운 내용 요약

- **Vivado Flow**: RTL → Simulation → Synthesis → Implementation → Bitstream → FPGA
- **Board File**: Vivado가 Basys3 보드를 인식하도록 함
- **XDC**: HDL Port ↔ 실제 FPGA Pin 연결
- **wire**: 신호 연결선
- **assign**: Continuous Assignment, 회로 연결
- **Instantiation**: 상위 Module에서 하위 Module 연결
- **Test Bench**: DUT 기능을 Simulation으로 검증
- <strong>`timescale`</strong>: Simulation 시간 단위 / 정밀도
- **Half Adder**: `a+b`, `sum=XOR`, `cout=AND`
- **Full Adder**: `a+b+cin`
- **Ripple Carry Adder**: 각 자리 Carry를 다음 자리로 전달
- **Latch**: Level Triggered
- **Flip-Flop**: Edge Triggered
- <strong>Blocking</strong> <strong>`=`</strong>: 즉시 갱신, 순서 영향 가능
- <strong>Non-blocking</strong> <strong>`<=`</strong>: 이전 값 기준 평가 후 갱신
- <strong>`.bit`</strong>: FPGA 직접 Programming
- <strong>`.bin`</strong>: Flash Programming
