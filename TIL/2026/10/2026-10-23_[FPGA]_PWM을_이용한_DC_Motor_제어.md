# \[FPGA\] PWM을 이용한 DC Motor 제어

> 날짜: 2026-10-23
> 원본 노션: [링크](https://app.notion.com/p/FPGA-PWM-DC-Motor-4021d46c18fc80f08ec1c1dd7bdf82c5)

<!-- notion-page-id: 4021d46c18fc80f08ec1c1dd7bdf82c5 -->
<!-- notion-title: "[FPGA] PWM을 이용한 DC Motor 제어" -->

---

<a id="notion-4021d46c18fc801eaa25e687ab71ff04"></a>

# PWM

- \*\*PWM(Pulse Width Modulation)\*\*은 한 주기에서 신호가 HIGH 상태로 유지되는 비율을 조절하는 방식이다.

```text
Duty Cycle = 한 주기에서 HIGH인 시간의 비율
```

예:

```text
Duty 0%   → 항상 LOW
Duty 25%  → 주기의 25%가 HIGH
Duty 50%  → 주기의 50%가 HIGH
Duty 75%  → 주기의 75%가 HIGH
Duty 100% → 항상 HIGH
```

PWM은 개별 bit 하나의 값보다 **한 주기 안에서 HIGH가 차지하는 비율**이 중요하다.

---

<a id="notion-4021d46c18fc80569c8cdfa7cf86b22a"></a>

## Duty Cycle

Duty Cycle을 조절하면 Digital Signal인 PWM을 이용해 아날로그와 유사한 효과를 낼 수 있다.

대표적인 활용:

```text
LED 밝기 제어
DC Motor 속도 제어
```

LED의 경우 Duty Cycle에 따라 ON 상태가 유지되는 비율이 달라지며, 빠르게 반복되는 PWM을 사람의 눈이 평균적인 밝기로 인식한다.

```text
Duty 낮음 → LED가 상대적으로 어둡게 보임
Duty 높음 → LED가 상대적으로 밝게 보임
```

---

<a id="notion-4021d46c18fc805488e6ee8fca8753f6"></a>

## DC Motor PWM 제어

DC Motor의 속도는 Motor Driver에 전달되는 PWM 신호를 이용하여 조절한다.

```text
PWM Duty Cycle 변경
        ↓
Motor 동작 속도 변경
```

전체 구조:

```text
Basys3 FPGA
    │
    ├─ PWM
    └─ 방향 제어
         ↓
   Motor Driver
         ↓
      DC Motor
```

PWM은 **모터 속도 제어**, 방향 제어 신호는 **모터 회전 방향 결정**에 사용된다.

---

<a id="notion-4021d46c18fc800abc8df93b6fc618e3"></a>

## Motor 방향 제어

Motor Driver의 `IN1`, `IN2` 신호를 이용하여 Motor의 회전 방향을 제어한다.

```text
IN1  IN2

 0    1  → 역방향 회전
 1    0  → 정방향 회전
 1    1  → Brake
```

역할을 구분하면:

```text
PWM       → Motor Speed
IN1 / IN2 → Motor Direction
```

이다.

---

<a id="notion-4021d46c18fc8045a88ae5cefefbc6b9"></a>

## Duty 조절 Button

PWM Duty Cycle은 Basys3 Button으로 조절한다.

```text
BTNU → Duty 증가
BTND → Duty 감소
```

XDC의 Top Port 이름:

```text
increase_duty_btn
decrease_duty_btn
```

동작 흐름:

```text
Button 입력
    ↓
Duty 값 증가 / 감소
    ↓
PWM HIGH 비율 변경
    ↓
Motor 속도 변경
```

---

<a id="notion-4021d46c18fc809880c6f0baa6ba2aa8"></a>

## 방향 선택 Switch

Basys3의 Switch를 Motor 방향 입력으로 사용한다.

```text
SW0 → motor_direction[0]
SW1 → motor_direction[1]
```

이 입력을 이용하여 Motor Driver에 전달할 `IN1 / IN2` 값을 결정한다.

```text
Switch
   ↓
motor_direction
   ↓
IN1 / IN2 결정
   ↓
Motor 회전 방향 결정
```

---

<a id="notion-4021d46c18fc805582d7f7cd2ce4e99a"></a>

## Pmod를 이용한 Motor Driver 연결

Basys3의 Pmod Header를 이용하여 PWM과 방향 제어 신호를 외부 Motor Driver로 전달한다.

XDC 기준:

```text
JA1 → PWM_OUT
JA2 → in1_in2[0]
JA3 → in1_in2[1]
```

즉:

```text
Basys3
 │
 ├─ JA1 : PWM
 ├─ JA2 : IN1
 └─ JA3 : IN2
        ↓
   Motor Driver
        ↓
     DC Motor
```

구조로 연결한다.

---

<a id="notion-4021d46c18fc805e9466e6c4231dfe9c"></a>

## PWM LED

PWM 신호를 Basys3의 `LED0`에도 연결하여 PWM 동작을 확인할 수 있다.

```text
LED0 → PWM_OUT_LED
```

Duty Cycle이 달라지면 LED의 밝기도 달라져 PWM 변화 여부를 시각적으로 확인할 수 있다.

---

<a id="notion-4021d46c18fc80aab82df6e079a48d08"></a>

## 7-Segment Display

7-Segment Display를 이용하여 Motor의 회전 방향과 PWM Speed를 표시할 수 있다.

자료의 표시 예:

```text
F → 정방향(Forward)
b → 역방향(Backward)

숫자 → PWM Speed
```

Basys3의 4자리 7-Segment Display는:

```text
seg[6:0]
dp
an[3:0]
```

신호를 사용한다.

Basys3의 7-Segment Display는 **Common Anode 방식**이다.

---

<a id="notion-4021d46c18fc8058beb1e640dc1cde40"></a>

## XDC 연결 정리

<a id="notion-4021d46c18fc80499fdcc25273c5f758"></a>

### Clock

```text
clk → Basys3 100 MHz Clock
```

Clock Constraint:

```text
Period = 10 ns
```

<a id="notion-4021d46c18fc8010aeeffa15d5433cd4"></a>

### Switch

```text
SW0 → motor_direction[0]
SW1 → motor_direction[1]
```

<a id="notion-4021d46c18fc8023a422d0929020e606"></a>

### Button

```text
BTNU → increase_duty_btn
BTND → decrease_duty_btn
```

<a id="notion-4021d46c18fc80d5a7d0f7f3563f9baa"></a>

### LED

```text
LED0 → PWM_OUT_LED
```

<a id="notion-4021d46c18fc809cb998fc00158d292f"></a>

### Pmod JA

```text
JA1 → PWM_OUT
JA2 → in1_in2[0]
JA3 → in1_in2[1]
```

<a id="notion-4021d46c18fc807a8de7d99e2dd0f49c"></a>

### 7-Segment

```text
seg[6:0]
dp
an[3:0]
```

---

<a id="notion-4021d46c18fc80ad93aac8cd63aea577"></a>

## 전체 동작 흐름

<a id="notion-4021d46c18fc80938237c830e9b43cb0"></a>

### 속도 제어

```text
BTNU / BTND
    ↓
Duty Cycle 증가 / 감소
    ↓
PWM 생성
    ↓
PWM_OUT
    ↓
Motor Driver
    ↓
DC Motor 속도 제어
```

<a id="notion-4021d46c18fc80b3afafd5b24ffe4286"></a>

### 방향 제어

```text
SW0 / SW1
    ↓
motor_direction
    ↓
IN1 / IN2
    ↓
Motor Driver
    ↓
정방향 / 역방향 / Brake
```

<a id="notion-4021d46c18fc80929183ed5c39d05c26"></a>

### 상태 확인

```text
PWM
 └→ PWM_OUT_LED

Direction + PWM Speed
 └→ 7-Segment Display
```

---

<a id="notion-4021d46c18fc801b82b6df71e9336697"></a>

## 핵심

```text
PWM
→ 한 주기에서 HIGH가 차지하는 시간 비율을 조절

Duty Cycle
→ HIGH 시간의 비율

Duty Cycle 변경
→ LED 밝기 / Motor 속도 제어

PWM
→ Motor 속도 제어

IN1 / IN2
→ Motor 방향 제어

Pmod
→ Basys3와 외부 Motor Driver 연결

7-Segment
→ 회전 방향과 PWM Speed 표시
```
