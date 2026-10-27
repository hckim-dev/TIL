# \[FPGA\] Rotary Encoder

> 날짜: 2026-10-27
> 원본 노션: [링크](https://app.notion.com/p/FPGA-Rotary-Encoder-4061d46c18fc80dfaa86e30b16ddae39)

<!-- notion-page-id: 4061d46c18fc80dfaa86e30b16ddae39 -->
<!-- notion-title: "[FPGA] Rotary Encoder" -->

---

<a id="notion-4061d46c18fc80408090c6bfffaf7e38"></a>

## Rotary Encoder

- \*\*Encoder(엔코더)\*\*는 기계적인 위치, 방향, 각도 등의 변화를 감지하여 **전기적인 신호로 출력하는 센서**이다.

```text
기계적인 움직임
    ↓
위치 / 방향 / 각도 변화
    ↓
Pulse Signal
    ↓
Digital Signal로 처리
```

Encoder에는 대표적으로:

```text
Rotary Encoder
→ 회전 각도 / 방향 검출

Linear Encoder
→ 직선 위치 / 이동량 검출
```

이 있다.

Rotary Encoder는 가전제품의 메뉴 선택이나 시간 설정 등 다양한 입력장치에 사용된다.

---

<a id="notion-4061d46c18fc809db01bc6366b496e2e"></a>

## Rotary Encoder 동작 원리

Rotary Encoder를 돌리면 내부 접점이 회전하면서 정해진 패턴의 신호가 발생한다.

이 신호의 변화를 이용하여:

```text
회전 방향
회전량
각도 변화
회전 속도
```

등을 판단할 수 있다.

이번 실습에서 사용하는 **EC11 Rotary Encoder**는 A상과 B상의 두 출력 신호를 사용하며, 두 신호의 변화 순서를 이용하여 회전 방향과 회전량을 판단한다.

---

<a id="notion-4061d46c18fc80518a56d376a425e4e6"></a>

## A상 / B상

EC11의 A상과 B상은 서로 약 **90°의 위상차**를 가진다.

```text
A상이 먼저 변화
→ CW

B상이 먼저 변화
→ CCW
```

이 위상차를 이용하면 어느 방향으로 회전했는지 판단할 수 있다.

---

<a id="notion-4061d46c18fc8061992fe315377cfa82"></a>

## 회전 방향 판별

회전 방향은 **A, B의 이전 상태와 현재 상태 변화**를 이용하여 판단한다.

<a id="notion-4061d46c18fc809389ceedae819b14cd"></a>

### CW — 시계 방향

```text
00 → 10 → 11 → 01 → 00
```

<a id="notion-4061d46c18fc809ebf66debe6c272391"></a>

### CCW — 반시계 방향

```text
00 → 01 → 11 → 10 → 00
```

즉 단순히 현재 A, B 값만 보는 것이 아니라:

```text
이전 {A, B}
      ↓
현재 {A, B}
      ↓
상태 변화 순서 비교
      ↓
CW / CCW 판별
```

방식으로 처리한다.

---

<a id="notion-4061d46c18fc8017a829d7d7c461c230"></a>

## EC11 Rotary Encoder

강의에서 사용하는 **EC11**은 증분형(Incremental) Rotary Encoder의 한 종류이다.

특징:

```text
360° 계속 회전 가능
회전 방향 검출
회전량 검출
A / B 두 개의 Pulse 출력
```

증분형 Encoder는 절대적인 위치를 알려주는 방식이 아니라:

```text
얼마나 움직였는가?
어느 방향으로 움직였는가?
```

를 알려준다.

따라서 전원이 꺼지면 마지막 위치 정보는 유지되지 않는다.

---

<a id="notion-4061d46c18fc8022899ddd786fdc94bf"></a>

## Pulse와 회전량

EC11은 회전할 때 Pulse를 발생시킨다.

자료에서는 일반적으로:

```text
20 Pulse / 회전
또는
24 Pulse / 회전
```

형태가 사용된다고 설명한다.

발생한 Pulse의 수를 세면 **얼마나 회전했는지** 알 수 있다.

---

<a id="notion-4061d46c18fc80f78105de555ad7f90b"></a>

## Push Button

EC11 제품에는 축을 눌러 사용하는 **Push Button이 포함된 형태도 있다.**

이를 이용하여:

```text
회전
→ 값 증가 / 감소
→ 메뉴 이동

누름
→ 메뉴 선택
→ 기능 실행
```

과 같은 동작을 구현할 수 있다.

---

<a id="notion-4061d46c18fc803abbdbf31e3788ecf2"></a>

## Basys3 연결

강의자료에서는 Rotary Encoder를 Basys3의 **Pmod JC**에 연결한다.

```text
JC2 → S1
JC3 → S2
JC4 → KEY
```

역할:

```text
S1 / S2
→ Rotary Encoder의 회전 신호

KEY
→ Rotary Encoder Push Button
```

이다.

---

<a id="notion-4061d46c18fc80c9970efafe0dbdcadc"></a>

## FPGA에서의 처리 흐름

전체적인 처리 흐름은:

```text
Rotary Encoder 회전
        ↓
S1 / S2 입력
        ↓
입력 안정화
        ↓
이전 상태 저장
        ↓
현재 상태와 비교
        ↓
CW / CCW 판별
        ↓
Counter 증가 / 감소
        ↓
LED 등으로 결과 출력
```

형태로 이해하면 된다.

---

<a id="notion-4061d46c18fc8089b9d1e8721992c79a"></a>

## Chattering

Rotary Encoder는 기계식 접점을 사용하므로 회전하거나 버튼을 누를 때 **Chattering**이 발생할 수 있다.

```text
실제 입력
0 → 1

Chattering 발생
0 → 1 → 0 → 1 → 0 → 1
```

처럼 짧은 시간 동안 신호가 여러 번 흔들릴 수 있다.

따라서 실제 FPGA에서는 입력을 그대로 사용하기보다 **Debounce 처리 후 사용하는 것이 중요**하다.

---

<a id="notion-4061d46c18fc80acaa30f0cc355f65e1"></a>

## Simulation

강의자료의 Simulation에서는 S1, S2의 상태 변화를 이용하여 정방향과 역방향을 확인한다.

<a id="notion-4061d46c18fc8003b3ecdb9a45fb637a"></a>

### 정방향

```text
00 → 10 → 11 → 01 → 00
```

<a id="notion-4061d46c18fc80b8bd09f96e66d0db4a"></a>

### 역방향

```text
00 → 01 → 11 → 10 → 00
```

이 상태 변화에 따라 Counter 값이 증가하거나 감소하는 것을 확인한다.

Simulation에서는 Chattering 입력과 Debounce 후의 신호 변화도 함께 확인한다.

---

<a id="notion-4061d46c18fc80fba09ec19fe9b1a59a"></a>

## 핵심

```text
Encoder
→ 기계적인 움직임을 전기적 신호로 변환

Rotary Encoder
→ 회전 방향 / 회전량 / 회전 속도 검출

EC11
→ 증분형 Rotary Encoder

A상 / B상
→ 약 90° 위상차를 가진 두 신호

CW
→ 00 → 10 → 11 → 01 → 00

CCW
→ 00 → 01 → 11 → 10 → 00

이전 상태 + 현재 상태
→ 회전 방향 판별

Pulse 수
→ 회전량 확인

KEY
→ Rotary Encoder Push Button

Chattering
→ Debounce 필요

Basys3 Pmod
→ JC2: S1
→ JC3: S2
→ JC4: KEY
```

<br>
