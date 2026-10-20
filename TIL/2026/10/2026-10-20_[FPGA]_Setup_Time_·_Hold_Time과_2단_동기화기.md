# \[FPGA\] Setup Time · Hold Time과 2단 동기화기

> 날짜: 2026-10-20
> 원본 노션: [링크](https://app.notion.com/p/FPGA-Setup-Time-Hold-Time-2-3fe1d46c18fc8086906fd1fe33399abd)

<!-- notion-page-id: 3fe1d46c18fc8086906fd1fe33399abd -->
<!-- notion-title: "[FPGA] Setup Time · Hold Time과 2단 동기화기" -->

---

<a id="notion-3ff1d46c18fc806b8440d420a30cbc97"></a>

# Setup Time / Hold Time 기본 개념

Flip-Flop은 Clock Edge에서 입력 데이터를 Sampling하여 저장한다.

실제 하드웨어에서는 Clock Edge와 동시에 아무 조건 없이 데이터를 저장할 수 없으며, **Clock Edge 전후 일정 시간 동안 입력 데이터가 안정적으로 유지되어야 한다.**

<a id="notion-3ff1d46c18fc800ca977f7c925bfb028"></a>

### Setup Time

`Setup Time (t_su)`

Clock Edge **이전**에 입력 데이터가 안정적으로 유지되어야 하는 최소 시간.

```text
Data 안정 ──────┐
                │ Setup Time
                ↓
────────────── Clock Edge
```

Setup Time 구간에서 입력이 변하면 Flip-Flop이 데이터를 정상적으로 Capture하지 못하고 **Metastability**가 발생할 수 있다.

<a id="notion-3ff1d46c18fc800c9da0fd92efc0abee"></a>

### Hold Time

`Hold Time (t_h)`

Clock Edge **이후**에도 입력 데이터가 안정적으로 유지되어야 하는 최소 시간.

```text
Clock Edge
    ↓
────┼────────────
    │ Hold Time
    └──── Data 안정 유지
```

Hold Time 동안 입력이 유지되지 않으면 역시 Metastability가 발생할 수 있다.

---

<a id="notion-3ff1d46c18fc80458148e841b0e94fce"></a>

## 왜 Setup / Hold Time이 필요한가?

Flip-Flop 내부의 Transistor가 실제로 Switching하고 데이터를 저장하는 데는 **물리적인 시간**이 필요하기 때문이다.

<a id="notion-3ff1d46c18fc80e5b90de5c3a3e72d6a"></a>

### Setup Violation

데이터가 너무 늦게 도착하여 Clock Edge 전에 충분히 안정되지 못한 경우.

```text
Data 도착이 늦음
→ Clock Edge 도착
→ FF가 새로운 값을 정상적으로 판단하지 못함
```

<a id="notion-3ff1d46c18fc8080bad1d12a50da6148"></a>

### Hold Violation

Clock Edge 직후 데이터가 너무 빨리 변경되는 경우.

```text
Clock Edge
→ 기존 값을 저장하는 중
→ Data가 너무 빨리 변경
→ 정상적인 저장이 어려워짐
```

---

<a id="notion-3ff1d46c18fc8056bdf4cb9813586f9a"></a>

## Metastability

Setup / Hold Time 구간에서 입력이 변경되면 Flip-Flop 출력이 순간적으로:

`0도 아니고 1도 아닌 불안정한 상태`

가 될 수 있다.

이 상태를 \*\*Metastability(메타스테빌리티)\*\*라고 한다.

특징:

- 일정 시간이 지나면 0 또는 1 중 하나로 안정될 수 있음
- 어느 값으로 결정될지는 예측하기 어려움
- Timing에 따라 간헐적으로 발생 가능
- Simulation에서는 정상인데 실제 FPGA Board에서만 문제가 나타날 수 있음

---

<a id="notion-3ff1d46c18fc8011845ed246e5273267"></a>

## 비동기 입력을 FSM에 직접 넣으면 위험한 이유

버튼이나 외부 Sensor는 FPGA Clock과 관계없이 변하는 \*\*비동기 입력(Asynchronous Input)\*\*이다.

이를 FSM에 직접 연결하면 Clock Edge 근처에서 입력이 변경되어 Setup / Hold Violation이 발생할 수 있다.

```text
Button / Sensor
      ↓
     FSM
```

이 구조는 위험할 수 있다.

발생 가능한 문제:

- State Bit마다 입력을 다르게 읽을 수 있음
- 의도하지 않은 State로 이동할 수 있음
- Timing에 따라 간헐적으로 오동작할 수 있음

예를 들어 `101 FSM`의 `S1(01)` 상태에서 입력이 변할 때 State Bit가 서로 다른 값을 Capture하면 의도하지 않은 `S3(11)` 같은 상태가 만들어질 수 있다.

---

<a id="notion-3ff1d46c18fc8035b455cf5876560864"></a>

## 2단 동기화기 (2-stage Synchronizer)

1bit 비동기 입력은 일반적으로 Flip-Flop 2개를 연속으로 사용하여 FPGA Clock에 동기화한다.

```text
Asynchronous Input
        ↓
      [FF1]
        ↓
      [FF2]
        ↓
 Synchronized Input
        ↓
       FSM
```

FF1과 FF2는 **같은 Clock**을 사용한다.

<a id="notion-3ff1d46c18fc80a29e54e361ee07763e"></a>

### FF1의 역할

FF1은 비동기 입력을 처음 Sampling한다.

Clock Edge 근처에서 입력이 변경되면 FF1이 Metastability 상태에 빠질 가능성이 있다.

하지만 시간이 지나면서 FF1 출력은 내부의 물리적인 특성에 의해 0 또는 1 중 하나로 안정된다.

이때 안정화되는 데 필요한 시간을:

`Resolution Time`

이라고 한다.

<a id="notion-3ff1d46c18fc8094bc81f9d51bf1ab58"></a>

### FF2의 역할

FF2가 Metastability 상태를 직접 0이나 1로 바꾸는 것은 아니다.

FF2의 핵심 역할은:

**FF1이 Metastability에서 안정될 수 있도록 약 한 Clock 주기의 시간적 여유를 확보한 뒤 그 값을 다시 Sampling하는 것**

이다.

```text
Clock Edge 1
→ FF1이 비동기 입력 Sampling
→ FF1이 불안정할 수 있음

      Resolution Time

Clock Edge 2
→ FF2가 안정된 FF1 출력 Sampling
→ 안정된 값을 내부 Logic에서 사용
```

⚠️ 중요

**2단 동기화기는 Metastability 자체를 완전히 없애는 회로가 아니다.**

FF1의 Metastability가 해결될 시간을 확보하여 **불안정한 값이 FSM까지 전달될 가능성을 줄이는 구조**이다.

---

<a id="notion-3ff1d46c18fc8032b5dcebfbfbc87e55"></a>

## 2단 FF 동기화 타이밍

동작 흐름:

1. 비동기 입력이 Clock Edge 근처에서 변경됨
2. FF1 출력이 일시적으로 불안정해질 수 있음
3. 다음 Clock Edge까지 FF1 출력이 0 또는 1로 안정됨
4. FF2가 안정된 FF1 값을 Sampling
5. FSM에서는 FF2 출력만 사용

```text
async_in
   ↓
 FF1       ← Metastability 가능
   ↓
 FF2       ← 안정된 값 Sampling
   ↓
 FSM
```

---

<a id="notion-3ff1d46c18fc8056bbf8e13e742a13ad"></a>

## 2단 동기화기 Verilog

기본 구조:

```verilog
reg r_sync1;
reg r_sync2;

always @(posedge clk or posedge reset) begin
  if (reset) begin
    r_sync1 <= 1'b0;
    r_sync2 <= 1'b0;
  end else begin
    r_sync1 <= noisy_btn;
    r_sync2 <= r_sync1;
  end
end
```

이후 내부 Logic에서는 비동기 입력 `noisy_btn`을 직접 사용하지 않고:

```verilog
r_sync2
```

를 사용한다.

---

<a id="notion-3ff1d46c18fc80f1a466f508d85f81b8"></a>

## 2단 동기화기 사용 시 주의점

<a id="notion-3ff1d46c18fc80ba8553eeed6853455b"></a>

### 1bit 신호에 사용

2단 동기화기는 기본적으로 **1bit 비동기 신호**에 사용한다.

여러 Bit Bus를 각 Bit별로 독립적으로 동기화하면 각 Bit가 서로 다른 시점에 Capture되어 **데이터 값이 섞일 수 있다.**

따라서 Multi-bit Data는 단순히 각 Bit에 2단 동기화기를 붙이는 방식으로 처리하면 안 된다.

<a id="notion-3ff1d46c18fc80b79283fbe56b52e8f9"></a>

### 입력 반영 지연

FF를 2개 통과하므로 입력이 내부 Logic에 반영될 때 지연이 발생한다.

설계 시 입력 반영에 최대 약 `2 Clock`의 지연이 발생할 수 있음을 고려해야 한다.

<a id="notion-3ff1d46c18fc80669fbbd27d70e00992"></a>

### 짧은 Pulse

Clock 한 주기보다 짧은 Pulse는 Sampling하지 못하고 놓칠 수 있다.

따라서 버튼처럼 비교적 오래 유지되는 신호에 적합하다.

---

<a id="notion-3ff1d46c18fc8003a162cb757de2058e"></a>

## 버튼 FSM에 적용

버튼 FSM에서는 다음과 같은 흐름으로 구성한다.

```text
btnU / btnD
(비동기 입력)
      ↓
2단 FF Synchronizer
      ↓
Debouncer
(10 ms)
      ↓
Edge Detector
      ↓
FSM
```

즉 외부 Button을 FSM에 직접 연결하는 것이 아니라 **입력단에서 먼저 Clock에 동기화**한다.

---

<a id="notion-3ff1d46c18fc80e79635d709c31ffdd8"></a>

## Setup Time Violation 원인

대표적인 원인:

- 조합 논리 경로가 너무 김
- Clock 주기가 너무 짧음
- Clock Skew가 존재함

예:

```text
FF ───── 긴 조합회로 ─────→ FF
                            ↑
                   Data 도착이 늦음
```

---

<a id="notion-3ff1d46c18fc80fdbf39ded8514d1c7d"></a>

## Setup Time Violation 해결

Setup Violation은 Data가 늦게 도착하는 것이 문제이므로 **Data Path를 더 빠르게 만드는 방향**으로 해결한다.

<a id="notion-3ff1d46c18fc8039af28dbf893be5c24"></a>

### 조합 논리 최소화

FF 사이의 조합회로를 단순하게 하여 Data가 더 빨리 도착하도록 한다.

<a id="notion-3ff1d46c18fc80a0a134d9ee795327c4"></a>

### Clock 주기 늘리기

Clock Frequency를 낮춰 Data가 안정될 시간을 확보한다.

```text
Clock Frequency ↓
→ Clock Period ↑
→ Data 안정화 시간 ↑
```

단점:

`전체 동작 성능 ↓`

따라서 가장 단순하지만 성능 저하가 발생하는 방법이다.

<a id="notion-3ff1d46c18fc80bc94a2ea42adc893ba"></a>

### Pipeline 추가

긴 조합회로 중간에 Flip-Flop을 추가하여 경로를 여러 단계로 나눈다.

기존:

```text
FF → ───────── 긴 조합회로 ───────── → FF
```

Pipeline 적용:

```text
FF → 조합회로 → FF → 조합회로 → FF
```

각 FF 사이의 조합회로가 짧아져 Timing을 맞추기 쉬워진다.

단점:

`Latency 증가`

기타 해결 방법:

- 빠른 Logic Cell 사용
- Clock Tree 최적화
- 비동기 입력 동기화
- Timing Constraint 조정

---

<a id="notion-3ff1d46c18fc80ca9e65fadddf391bdc"></a>

## Hold Time Violation 원인

Hold Violation은 Data가 **너무 빨리 도착하여** Clock Edge 이후 필요한 Hold Time 동안 값이 안정적으로 유지되지 못할 때 발생한다.

대표적인 원인:

`FF 사이의 조합 논리 경로가 너무 짧음`

```text
FF → 짧은 경로 → FF
      ↑
 Data가 너무 빨리 도착
```

---

<a id="notion-3ff1d46c18fc808ea146fc2caf5e089b"></a>

## Hold Time Violation 해결

Hold Violation은 Setup과 반대로 **Data Path를 일부러 느리게 만드는 방향**으로 해결한다.

대표적인 방법:

- Buffer 추가
- 조합 논리 추가
- Clock Tree 조정
- P&amp;R Tool의 Hold Fixing 기능 사용
- `set_min_delay` 등의 Timing Constraint 사용

⚠️ 중요

**Hold Violation은 단순히 Clock Frequency를 낮추는 것만으로 해결하기 어려운 경우가 많다.**

Setup Violation은 Clock Period를 늘려 Data가 도착할 시간을 확보할 수 있지만, Hold Violation은 **같은 Clock Edge 직후에 Data가 너무 빨리 변하는 문제**이기 때문에 Data Path 자체에 Delay를 추가하는 방향으로 해결한다.

---

<a id="notion-3ff1d46c18fc80379361fb77aa4d38db"></a>

## Setup과 Hold 비교

| 구분 | Setup Violation | Hold Violation |
| --- | --- | --- |
| 문제 | Data가 너무 늦음 | Data가 너무 빠름 |
| 기준 | Clock Edge 이전 | Clock Edge 이후 |
| 상태 | Edge 전에 안정되지 않음 | Edge 직후 안정되지 않음 |
| 해결 방향 | Data Path를 빠르게 | Data Path를 느리게 |
| 대표 방법 | Pipeline, Logic 최소화 | Buffer, Delay 추가 |
| Clock 주파수 감소 | 해결에 도움 가능 | 일반적으로 근본 해결이 어려움 |

---

<a id="notion-3ff1d46c18fc80358f9ee8e6b6610482"></a>

## Verilog 관점에서의 대응

Verilog RTL에서 실제 물리적인 Gate Delay를 직접 조절하기보다는:

- 회로 구조 변경
- Pipeline 추가
- Timing Constraint
- Synthesis
- Place &amp; Route

등을 통해 Timing을 맞춘다.

<a id="notion-3ff1d46c18fc8034ac58c349e9a030e1"></a>

### Setup 해결 구조 예

```verilog
always @(posedge clk) begin
  stage1 <= input_data;
  stage2 <= stage1;
end
```

중간 Flip-Flop을 추가하여 긴 경로를 여러 단계로 분할한다.

<a id="notion-3ff1d46c18fc8050ad38fbddc20c86d7"></a>

### Simulation Delay

```verilog
assign #1 delayed_signal = fast_signal;
```

이와 같은 `#delay`는 **Simulation용 Delay 표현**이며 실제 FPGA의 물리적인 Delay를 직접 구현하는 용도로 사용하는 것이 아니다.

---

<a id="notion-3ff1d46c18fc8069869bdfb6e94d6b3f"></a>

## 핵심

- Setup Time → Clock Edge **전에** Data가 안정되어야 하는 최소 시간
- Hold Time → Clock Edge **후에도** Data가 안정되어야 하는 최소 시간
- Setup / Hold Violation → Metastability 발생 가능
- Metastability → FF 출력이 일시적으로 0/1을 확정하지 못하는 상태
- 버튼·센서 → FPGA Clock과 무관하게 들어오는 비동기 입력
- 비동기 입력을 FSM에 직접 연결하면 Timing 문제 가능
- 1bit 비동기 입력 → **2단 FF Synchronizer** 사용
- FF1 → Metastability 발생 가능
- FF2 → FF1이 안정될 시간을 확보한 뒤 Sampling
- 2단 동기화기는 Metastability를 없애는 것이 아니라 **전파 가능성을 줄이는 구조**
- Multi-bit Bus → 각 Bit를 독립적으로 2단 동기화하면 값이 섞일 수 있으므로 주의
- Setup Violation → Data Path를 **더 빠르게**
- Hold Violation → Data Path를 **더 느리게**
- Setup → Pipeline 적용 가능
- Hold → Buffer / Delay 추가 가능
- 실제 FPGA Timing은 RTL 구조뿐 아니라 Synthesis, P&amp;R, Timing Constraint까지 함께 고려

<a id="notion-3ff1d46c18fc8002afa7c7ca88858762"></a>

## 오늘 실습 연결

<a id="notion-3ff1d46c18fc80cb85f1fecc26df87da"></a>

### Button 입력 처리 흐름

```text
btnC
 ↓
2단 FF Synchronizer
 ↓
Debouncer
 ↓
Release Edge Detector
 ↓
FSM
 ↓
LED
```

- 외부 Button은 비동기 입력이므로 먼저 2단 FF로 Clock Domain에 동기화
- Debouncer로 Button Chattering 제거
- 이전 Button 값과 현재 값을 비교하여 Release Edge를 1 Clock Pulse로 생성
- Pulse가 한 번 발생할 때마다 FSM이 한 단계 전이

<a id="notion-3ff1d46c18fc806e851fd07074283602"></a>

### LED FSM

LED 동작:

```text
1 → 2 → 3 → 4 → 3 → 2 → 1 → 2 → ...
```

- `led[3:0]` : 현재 LED 위치
- `led[4]` : 방향

  - `0` → 순방향
  - `1` → 역방향
- `dir`도 FSM이 기억해야 하는 상태 정보의 일부로 볼 수 있음

<a id="notion-3ff1d46c18fc80aaa559e4cbf2e77600"></a>

### Moore / Mealy 출력 차이

**Moore**

```verilog
assign led = {r_curr_dir, r_curr_state};
```

- 현재 등록된 State만으로 출력 결정
- Clock Edge에서 State가 갱신된 후 출력 변경

**Mealy**

```verilog
led = {r_next_dir, r_next_state};
```

- 현재 State와 입력(`btn_pulse`)에 의해 계산된 값으로 출력 결정
- 입력 변화에 따라 Clock Edge 전에도 조합적으로 출력이 변할 수 있음

<a id="notion-3ff1d46c18fc80aeb6a4dd338aaa4b93"></a>

### FSM 조합논리 기본값

```verilog
r_next_state = r_curr_state;
r_next_dir   = r_curr_dir;
```

- `btn_pulse == 0`이면 현재 상태와 방향 유지
- 모든 조합논리 경로에 값을 할당하여 Latch 발생 방지

<a id="notion-3ff1d46c18fc80fe8dcbc5414eb7f1ed"></a>

### Testbench

실제 Debounce 값은:

```text
1,000,000 Clock = 10 ms @ 100 MHz
```

Simulation에서는 시간이 오래 걸리므로 Testbench에서만 `DebounceCount`를 작게 설정하여 검증 시간을 단축할 수 있다.
