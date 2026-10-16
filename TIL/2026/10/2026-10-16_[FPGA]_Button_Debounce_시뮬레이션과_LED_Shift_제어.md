# \[FPGA\] Button Debounce 시뮬레이션과 LED Shift 제어

> 날짜: 2026-10-16
> 원본 노션: [링크](https://app.notion.com/p/FPGA-Button-Debounce-LED-Shift-3fb1d46c18fc80b9914cea5f95fa9a00)

<!-- notion-page-id: 3fb1d46c18fc80b9914cea5f95fa9a00 -->
<!-- notion-title: "[FPGA] Button Debounce 시뮬레이션과 LED Shift 제어" -->

---

<a id="notion-3fb1d46c18fc80ca85b1fbad57b2e037"></a>

## Button Debounce 시뮬레이션

- `sel = 1` → `btnU` 선택
- `clean_btn` → Debounce 처리된 버튼 신호
- `led0` → `clean_btn` 상태를 그대로 출력
- `led2` → 버튼을 누를 때마다 ON/OFF Toggle

<a id="notion-3fb1d46c18fc802fb3fdeafa791e2c7e"></a>

### 시뮬레이션 결과

- Bounce 입력 중에는 `clean_btn`이 변하지 않음
- 버튼이 일정 시간 안정되면 `clean_btn`이 HIGH
- 버튼을 놓고 일정 시간 지나면 `clean_btn`이 LOW
- `led2`는 버튼을 누를 때마다 상태가 반전됨

```text
clean_btn : 0 → 1 → 0 → 1
led0      : 0 → 1 → 0 → 1
led2      : 0 → 1 ─────→ 0
```

→ Debounce와 LED Toggle이 정상적으로 동작함.

<a id="notion-3fb1d46c18fc80e9912cfe282957cbd7"></a>

## `timescale`과 Waveform 시간

```verilog
`timescale 1ns / 1ps
```

- `#100` → 100 ns
- `#200` → 200 ns
- `#300` → 300 ns

Bounce 테스트:

```verilog
#100; btnU = 1;
#200; btnU = 0;
#300; btnU = 1;
#120; btnU = 0;
#500;
```

전체 Bounce 시간은 약 `1.22 µs`.

반면 Debounce 테스트는 약 `10~12 ms` 단위이므로 전체 Waveform에서는 Bounce 구간이 매우 짧아 거의 보이지 않음.

→ Bounce를 확인하려면 Waveform 시작 부분을 `ns ~ µs` 단위로 확대해서 확인해야 함.

<a id="notion-3fb1d46c18fc804e8cc1c48ed8773e70"></a>

## LED 배열을 개별 신호로 변경

기존:

```verilog
wire [1:0] led;
```

변경:

```verilog
wire led0;
wire led2;
```

각 LED의 역할을 개별 신호로 구분할 수 있어 Waveform 확인이 쉬워짐.

<a id="notion-3fb1d46c18fc80c1b377fa417dc4d02f"></a>

## LED 한 칸 이동

초기값:

```verilog
r_up_counter <= 16'h0001;
```

```text
0000_0000_0000_0001
```

LED 하나만 ON된 상태에서 한 칸씩 이동.

<a id="notion-3fb1d46c18fc8014ae98cfbb1febad15"></a>

### Concatenation을 이용한 이동

```verilog
r_up_counter <= {r_up_counter[14:0], 1'b0};
```

- `{ }` → 여러 Bit를 이어 붙이는 Concatenation
- `r_up_counter[14:0]` 뒤에 `1'b0`을 붙여 전체 값을 왼쪽으로 한 칸 이동

동작:

```text
0000_0000_0000_0001
→ 0000_0000_0000_0010
→ 0000_0000_0000_0100
→ 0000_0000_0000_1000
```

즉,

- 현재 LED는 OFF
- 다음 LED는 ON

으로 한 칸씩 이동함.

<a id="notion-3fb1d46c18fc8059b908d52f73b85ec5"></a>

### Shift 연산자로 표현

```verilog
r_up_counter <= r_up_counter << 1;
```

`<< 1` → 전체 Bit를 왼쪽으로 한 칸 이동.

따라서 아래 두 코드는 같은 방식의 LED 이동을 표현함.

```verilog
r_up_counter <= {r_up_counter[14:0], 1'b0};
```

```verilog
r_up_counter <= r_up_counter << 1;
```

<a id="notion-3fb1d46c18fc801b93e8e2c33b17e9f5"></a>

## 마지막 LED 처리

마지막 LED까지 이동하면:

```text
1000_0000_0000_0000
```

다음에는 다시 첫 번째 LED로 돌아가야 함.

```verilog
if (r_up_counter == 16'h8000) begin
  r_up_counter <= 16'h0001;
end else begin
  r_up_counter <= r_up_counter << 1;
end
```

동작:

```text
0001 → 0010 → 0100 → ... → 8000 → 0001
```

<a id="notion-3fb1d46c18fc80b0a87cfb9b9b64f5ba"></a>

## 핵심

- Debounce → 버튼의 Bounce 신호 제거
- `clean_btn` → 안정된 버튼 입력
- `led0` → Debounce된 버튼 상태 표시
- `led2` → 버튼 입력마다 ON/OFF Toggle
- `<< 1` → 켜진 LED 위치를 한 칸 이동
- `16'h8000`까지 이동하면 `16'h0001`로 돌아가 반복
