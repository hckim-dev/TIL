# \[FPGA\] Shift Register와 FSM을 이용한 1010111 Pattern Detector

> 날짜: 2026-10-21
> 원본 노션: [링크](https://app.notion.com/p/FPGA-Shift-Register-FSM-1010111-Pattern-Detector-3ff1d46c18fc80989a98df2246d30d8b)

<!-- notion-page-id: 3ff1d46c18fc80989a98df2246d30d8b -->
<!-- notion-title: "[FPGA] Shift Register와 FSM을 이용한 1010111 Pattern Detector" -->

---

<a id="notion-3ff1d46c18fc8067b1b5ef8d98e4683e"></a>

## 설계 목표

1bit 입력 `din`을 Clock Rising Edge마다 한 bit씩 받아 특정 Pattern을 검출한다.

검출 Pattern:

```text
1010111
```

동작 조건:

- `din` : 1bit 입력
- `clk` : Clock 입력
- `rst` : System Reset, Active-Low
- `dout` : 1bit 출력
- 평소 `dout = 0`
- `1010111`이 순서대로 입력되면 `dout = 1`

---

<a id="notion-3ff1d46c18fc8062a627df9de1d9ec1b"></a>

## 입력 Pattern 조건

입력은 `1010111`의 **왼쪽 bit부터 먼저 들어온다.**

```text
1 → 0 → 1 → 0 → 1 → 1 → 1
```

Pattern 앞뒤에는 `0` 또는 Random Data가 존재할 수 있다.

Pattern이 연속될 경우 앞 Pattern의 마지막 `1`을 다음 Pattern의 첫 `1`로 다시 사용할 수 있다.

```text
...1010111010111...
        ↑
     overlap
```

즉 **Overlapping Pattern Detection**을 고려해야 한다.

---

<a id="notion-3ff1d46c18fc8074ae0cd4ee0d1730bf"></a>

## 구현 방법

동일한 `1010111` Pattern Detector를 두 가지 방법으로 구현할 수 있다.

<a id="notion-3ff1d46c18fc80d1a33ec993912183ae"></a>

### Shift Register 방식

```text
7bit Shift Register
        +
7bit Comparator
```

<a id="notion-3ff1d46c18fc80bc991ae3abf3089586"></a>

### FSM 방식

```text
3bit State Register
        +
Next State Logic
```

FSM 방식에서는 State `0 ~ 6`을 사용한다.

---

<a id="notion-3ff1d46c18fc803eb7aee5e8d03a5cf6"></a>

## Shift Register 방식

7bit Shift Register에 입력을 한 bit씩 저장한 뒤 전체 값이 `1010111`인지 비교한다.

```text
din
 ↓
[0] → [1] → [2] → [3] → [4] → [5] → [6]
                         ↓
                7bit Pattern 비교
                         ↓
                       dout
```

새로운 입력 bit는 `sr7[0]`에 들어오고 기존 Data는 Clock마다 오른쪽으로 한 칸씩 이동한다.

따라서 가장 먼저 들어온 bit는 최종적으로 `sr7[6]`에 위치한다.

Pattern 비교:

```verilog
sr7 == 7'b1010111
```

조건을 만족하면 `dout = 1`이 된다.

<a id="notion-3ff1d46c18fc8003a3e5ec9bc37e1840"></a>

### Bit 순서 주의

그림에서는 Data가:

```text
sr7[0] → sr7[1] → ... → sr7[6]
```

방향으로 이동한다.

Verilog 벡터를 `sr7[6:0]` 순서로 읽으면 최종 Pattern이:

```text
1010111
```

이 된다.

---

<a id="notion-3ff1d46c18fc80dbb13ec25a91b40671"></a>

## Shift Register 출력 Timing

7개의 입력 bit가 들어와:

```text
sr7 = 1010111
```

이 되는 Clock 이후 `dout = 1`이 된다.

다음 Clock에서 Shift되어:

```text
sr7 = 0101110
```

이 되면 다시 `dout = 0`이 된다.

따라서 해당 Simulation에서는 Pattern이 한 번 검출될 때 `dout`이 **1 Clock 폭으로 출력**된다.

`dout`은 `sr7` 값을 비교하는 조합회로 출력이므로 `sr7` 값과 같은 시점에 변한다.

---

<a id="notion-3ff1d46c18fc8000b815e020910cc784"></a>

## Basys3 Button 입력 사용 시

자료에서는:

```text
btnU → 1 입력
btnD → 0 입력
```

으로 사용한다.

Basys3의 `clk = 100 MHz`를 그대로 사용하면 버튼을 누르고 있는 동안 같은 값이 매우 빠르게 반복 입력될 수 있다.

따라서 버튼을 한 번 입력했을 때 발생하는 **1 Clock Pulse를 Enable로 사용하여 그 순간에만 Shift**해야 한다.

또한 Pattern Detector의 `rst`는:

```text
Active-Low
```

이지만 Basys3 Reset Button은 Active-High이므로 극성을 맞춰야 한다.

```verilog
~reset
```

---

<a id="notion-3ff1d46c18fc809094f3f540dc13b0d7"></a>

## FSM 기본 개념

FSM은 유한한 개수의 State로 구성되는 제어회로이다.

`N bit` State Register로:

```text
2^N개의 State
```

를 표현할 수 있다.

예:

```text
3bit → 000 ~ 111 → 최대 8개 State
```

Clock이 발생할 때 State가 이동하며 현재 State와 입력에 따라 다음 State를 결정한다.

---

<a id="notion-3ff1d46c18fc8035b9e1d848556ca44c"></a>

## FSM 기본 구조

```text
              ┌────────────────────┐
              │                    ↓
din ──→ Next State Logic ──→ State Register
 │                               │
 │                               ↓
 └──────────────────────→ Output Logic ──→ dout
                              ↑
                         Current State
```

State Register는 `clk`, `rst`에 의해 갱신된다.

이번 설계에서는 출력이 <strong>현재 State와 입력</strong> <strong>`din`</strong>**으로 결정**된다.

```text
fsm == 6 && din == 1
        ↓
      dout = 1
```

---

<a id="notion-3ff1d46c18fc8027a0c1f18a6c2777a9"></a>

## 1010111 FSM

Pattern:

```text
1010111
```

을 검출하기 위해 State `0 ~ 6`을 사용한다.

Pattern과 입력이 일치하면 다음 State로 이동한다.

하지만 중간에 다른 bit가 들어왔다고 항상 State 0으로 돌아가면 **이미 입력된 Data 중 다시 활용할 수 있는 부분까지 버리게 된다.**

따라서 Overlap을 고려하여 다음 원칙으로 State를 결정한다.

> **입력이 Pattern과 어긋나더라도 현재 입력의 끝부분이 목표 Pattern의 앞부분과 일치하면 해당 State로 이동한다.**

---

<a id="notion-3ff1d46c18fc8018bb31e078c9973230"></a>

## Overlap을 고려한 주요 State 전이

<a id="notion-3ff1d46c18fc80578bdfcdc1970c8430"></a>

### State 5에서 `0` 입력

State 5에서 지금까지 입력된 Pattern:

```text
10101
```

여기에서 `0`이 들어오면:

```text
101010
```

전체 Pattern 검출에는 실패하지만 마지막:

```text
1010
```

은 새로운 Pattern의 앞부분으로 다시 사용할 수 있다.

따라서:

```text
State 5 + 0
→ State 4
```

로 이동한다.

<a id="notion-3ff1d46c18fc8007a306e82cd35bc1f8"></a>

### State 6에서 `0` 입력

State 6에서 지금까지 입력된 Pattern:

```text
101011
```

여기에서 `0`이 들어오면:

```text
1010110
```

마지막:

```text
10
```

을 다음 Pattern 검출에 다시 사용할 수 있다.

따라서:

```text
State 6 + 0
→ State 2
```

로 이동한다.

<a id="notion-3ff1d46c18fc801ebe04e18145fa8364"></a>

### State 6에서 `1` 입력

```text
101011 + 1
→ 1010111
```

목표 Pattern이 완성되므로:

```text
dout = 1
```

이 된다.

동시에 마지막 `1`은 다음 Pattern의 첫 번째 `1`로 재사용할 수 있으므로:

```text
State 6 + 1
→ State 1 / dout = 1
```

로 이동한다.

---

<a id="notion-3ff1d46c18fc80b68b8eea30eba8aaac"></a>

## State Table

| 현재 State | `din = 0` → 다음 State / 출력 | `din = 1` → 다음 State / 출력 |
| --- | --- | --- |
| 0 | 0 / 0 | 1 / 0 |
| 1 | 2 / 0 | 1 / 0 |
| 2 | 0 / 0 | 3 / 0 |
| 3 | 4 / 0 | 1 / 0 |
| 4 | 0 / 0 | 5 / 0 |
| 5 | 4 / 0 | 6 / 0 |
| 6 | 2 / 0 | 1 / 1 |

특히 중요한 전이:

```text
State 5 + 0 → State 4
State 6 + 0 → State 2
State 6 + 1 → State 1 / dout = 1
```

---

<a id="notion-3ff1d46c18fc80488898dbd3294c7d1d"></a>

## FSM Verilog 핵심

State Register:

```verilog
reg [2:0] fsm;
```

Reset은 Active-Low 방식이다.

```verilog
always @(negedge rst or posedge clk) begin
  if (rst == 0)
    fsm <= 0;
  else
    ...
end
```

Overlap을 고려한 주요 State 전이:

```verilog
3'd5:
  if (din == 1)
    fsm <= 6;
  else
    fsm <= 4;

3'd6:
  if (din == 1)
    fsm <= 1;
  else
    fsm <= 2;
```

출력:

```verilog
if ((fsm == 6) && (din == 1))
  dout <= 1;
else
  dout <= 0;
```

즉 `State 6`에서 마지막 `1`이 들어오면 `1010111` Pattern이 완성되어 `dout = 1`이 된다.

---

<a id="notion-3ff1d46c18fc8010a720da77827d5826"></a>

## Test Pattern

<a id="notion-3ff1d46c18fc8066ab4feeac839b8bfa"></a>

### Pattern A

입력:

```text
101010111
```

State 변화:

```text
1 → 2 → 3 → 4 → 5 → 4 → 5 → 6 → 1
```

마지막 Clock에서:

```text
dout = 1
```

<a id="notion-3ff1d46c18fc80ff830dc2d899cefb63"></a>

### Pattern B

입력:

```text
101011010111
```

State 변화:

```text
1 → 2 → 3 → 4 → 5 → 6 → 2 → 3 → 4 → 5 → 6 → 1
```

마지막 Clock에서:

```text
dout = 1
```

두 Test Pattern 모두 중간에 Pattern이 어긋나더라도 **유효한 끝부분을 재사용하여 정상적으로 검출**한다.

---

<a id="notion-3ff1d46c18fc804d94ccc4c76e80e5db"></a>

## Shift Register vs FSM

| 구분 | Shift Register | FSM |
| --- | --- | --- |
| 구조 | 7bit Shift Register + 7bit Comparator | 3bit State Register + Next State Logic |
| 장점 | 설계가 단순하고 설계 시간이 적게 걸림 | 회로 크기를 줄일 수 있음 |
| 단점 | Pattern 길이가 길어질수록 회로가 커짐 | State 전이 설계가 복잡하고 오류 가능 |
| 검증 | 비교적 단순 | State 전이를 Simulation으로 검증하는 것이 중요 |
