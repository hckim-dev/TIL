# \[FPGA\] PWM을 이용한 Piezo Buzzer 제어

> 날짜: 2026-10-26
> 원본 노션: [링크](https://app.notion.com/p/FPGA-PWM-Piezo-Buzzer-4041d46c18fc807abb8def9ffb943a50)

<!-- notion-page-id: 4041d46c18fc807abb8def9ffb943a50 -->
<!-- notion-title: "[FPGA] PWM을 이용한 Piezo Buzzer 제어" -->

---

<a id="notion-4051d46c18fc804c9843c2360be9c4cc"></a>

## Piezo Buzzer

- \*\*Piezo Buzzer(피에조 부저)\*\*는 압전 효과를 이용하여 소리를 발생시키는 소자이다.

압전 효과는 수정이나 세라믹 같은 물질에:

```text
기계적인 압력 / 변형
→ 전기적 신호 발생
```

또는 반대로:

```text
전기적 신호 인가
→ 물질 변형
```

이 발생하는 현상이다.

Piezo Buzzer에 전기 신호를 인가하면 내부 물질이 변형되고, 이로 인해 공기 입자에 압력 차이가 발생하면서 **음파**가 만들어진다.

---

<a id="notion-4051d46c18fc800a9ac8d015c4a1aeeb"></a>

## 음계와 주파수

소리의 음계는 주파수에 따라 달라진다.

자료의 음계 주파수 예:

| 음계 | 주파수 예 |
| --- | --- |
| C(도) | 261.6256 Hz |
| D(레) | 293.6648 Hz |
| E(미) | 329.6276 Hz |
| F(파) | 349.2282 Hz |
| G(솔) | 391.9954 Hz |
| A(라) | 440.0000 Hz |
| B(시) | 493.8833 Hz |

같은 음이라도 옥타브가 올라가면 주파수도 증가한다.

예:

```text
A(라)

110 Hz
220 Hz
440 Hz
880 Hz
1760 Hz
```

---

<a id="notion-4051d46c18fc803eb3a0e0f0a0014043"></a>

## FPGA에서 음계 만들기

Basys3의 기준 Clock을 분주하여 각 음계에 해당하는 주파수의 신호를 만든다.

자료에서 사용하는 음계와 분주값:

| 음 | 분주값 | 주파수(Hz) | Button |
| --- | --- | --- | --- |
| 도 | 76,444 | 1308.147 | BTND |
| 레 | 68,104 | 1468.343 | BTNL |
| 미 | 60,674 | 1648.152 | BTNC |
| 솔 | 51,020 | 1960.016 | BTNR |
| 라 | 45,454 | 2200.026 | BTNU |

Button에 따라 서로 다른 분주값을 선택한다.

```text
BTND → 도
BTNL → 레
BTNC → 미
BTNR → 솔
BTNU → 라
```

분주값이 달라지면 Buzzer에 전달되는 신호의 주파수도 달라지고, 결과적으로 서로 다른 음이 발생한다.

---

<a id="notion-4051d46c18fc803dbcdfd474f287abdc"></a>

## 동작 원리

전체 동작은 다음과 같다.

```text
Button 입력
    ↓
해당 음계 선택
    ↓
음계별 분주값 선택
    ↓
Clock 분주
    ↓
해당 주파수 신호 생성
    ↓
Piezo Buzzer 출력
```

즉 **FPGA의 기준 Clock을 분주하여 원하는 음계에 해당하는 주파수의 신호를 생성하고 Piezo Buzzer를 구동한다.**

---

<a id="notion-4051d46c18fc80d4a07dca4a28ab62db"></a>

## Piezo Buzzer와 주파수 제어

Piezo Buzzer에는 HIGH와 LOW가 반복되는 디지털 신호를 전달한다.

```text
HIGH ────┐    ┌────
         │    │
LOW      └────┘
```

이 신호가 반복되는 **주파수**에 따라 발생하는 음의 높이가 달라진다.

```text
낮은 주파수 → 낮은 음
높은 주파수 → 높은 음
```

이번 실습에서는 각 Button에 서로 다른 분주값을 적용하여 출력 주파수를 변경하고 음계를 만든다.

---

<a id="notion-4051d46c18fc80558d91e824f16e309a"></a>

## DC Motor PWM과 차이

DC Motor와 Piezo Buzzer 모두 HIGH / LOW가 반복되는 디지털 신호를 사용하지만 **주로 제어하는 요소가 다르다.**

| 구분 | DC Motor | Piezo Buzzer |
| --- | --- | --- |
| 주요 제어값 | Duty Cycle | 주파수 |
| 제어 목적 | 속도 제어 | 음계 제어 |
| 출력 | Motor 회전 | 소리 |

```text
DC Motor
→ Duty Cycle 변경
→ 속도 변경

Piezo Buzzer
→ 출력 주파수 변경
→ 음계 변경
```

---

<a id="notion-4051d46c18fc8055838cf7deeb6f17c1"></a>

## Basys3 Button

Basys3의 5개 Push Button을 각 음계 입력으로 사용한다.

```text
BTNU
BTND
BTNL
BTNR
BTNC
```

자료의 Basys3 I/O 기준:

```text
BTNL → W19
BTNR → T17
BTNU → T18
BTND → U17
BTNC → U18
```

각 Button을 누르면 해당 음계에 대응하는 분주값을 선택한다.

---

<a id="notion-4051d46c18fc800fb264f9c96abe5e92"></a>

## Pmod를 이용한 Piezo Buzzer 연결

Piezo Buzzer는 Basys3의 **Pmod Port**를 이용하여 연결한다.

Pmod Header는:

```text
VCC
GND
8개의 Signal Pin
```

으로 구성된다.

이번 실습에서는 Pmod를 통해 FPGA에서 생성한 Buzzer 제어 신호를 외부 Piezo Buzzer로 전달한다.

```text
Basys3 FPGA
    ↓
Pmod
    ↓
Piezo Buzzer
```

---

<a id="notion-4051d46c18fc80dc8f41d82e066054ce"></a>

## 시뮬레이션

Testbench에서는 각 Button 입력을 순서대로 발생시키고 `buzzer` 출력 동작을 확인한다.

자료의 Simulation에서는:

```text
btnU
btnL
btnC
btnR
btnD
```

신호를 순차적으로 입력한다.

검증 흐름:

```text
Button 변경
→ 선택 음계 변경
→ 분주값 변경
→ Buzzer 출력 동작 확인
```

---

<a id="notion-4051d46c18fc80abb5b5c14dab15ee1c"></a>

## 핵심

```text
Piezo Buzzer
→ 압전 효과를 이용하여 소리 발생

음계
→ 주파수에 따라 결정

FPGA
→ 기준 Clock을 분주하여 원하는 주파수 생성

Button
→ 음계별 분주값 선택

주파수 낮음
→ 낮은 음

주파수 높음
→ 높은 음

DC Motor PWM
→ Duty Cycle로 속도 제어

Piezo Buzzer
→ 주파수로 음계 제어
```
