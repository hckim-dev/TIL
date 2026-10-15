# \[FPGA\] Verilog 연산자와 주요 문법 정리

> 날짜: 2026-10-14
> 원본 노션: [링크](https://app.notion.com/p/FPGA-Verilog-3f91d46c18fc80b3ad44ef452945935c)

<!-- notion-page-id: 3f91d46c18fc80b3ad44ef452945935c -->
<!-- notion-title: "[FPGA] Verilog 연산자와 주요 문법 정리" -->

---

<a id="notion-3f91d46c18fc802bb9e5c022a9f92e8f"></a>

# \[FPGA\] Verilog 추가 문법 정리

<a id="notion-3f91d46c18fc80f8a56bdeeecb171e00"></a>

## 연산자 구분

Verilog에서는 비슷하게 생긴 연산자의 의미를 구분해야 한다.

| 문법 | 의미 | 예 |
| --- | --- | --- |
| `&` | Bitwise AND | `a & b` |
| `&&` | Logical AND | `a && b` |
| `\|` | Bitwise OR | `a \| b` |
| `\|\|` | Logical OR | `a \|\| b` |
| `~` | Bit 단위 NOT | `~a` |
| `!` | 논리 NOT | `!a` |
| `^` | Bitwise XOR | `a ^ b` |

예:

```text
a = 4'b1010;
b = 4'b0000;

a | b     // 4'b1010
a || b    // 1'b1
```

`|`은 **각 bit를 계산**, `||`은 값 전체를 **참/거짓으로 판단**한다.

---

<a id="notion-3f91d46c18fc80c592d2f37d328b61e9"></a>

## Reduction 연산자

연산자 하나를 Vector 앞에 붙이면 **모든 bit를 하나로 축약**한다.

```text
wire [3:0] a = 4'b1010;

&a      // 1 & 0 & 1 & 0 = 0
|a      // 1 | 0 | 1 | 0 = 1
^a      // 1 ^ 0 ^ 1 ^ 0 = 0
```

즉:

```text
|a
```

는 `a`의 bit 중 **하나라도 1인지** 확인하는 식으로 사용할 수 있다.

---

<a id="notion-3f91d46c18fc80c0838ed134c2c174ce"></a>

## Concatenation `{ }`

여러 신호를 이어 붙여 **하나의 Vector처럼 만드는 문법**이다. 왼쪽이 상위 bit(MSB), 오른쪽이 하위 bit(LSB)이다.

```text
{a, b}
```

예:

```text
a = 1'b1
b = 2'b10

{a, b} = 3'b110
```

<a id="notion-3f91d46c18fc8096955de1c3f1e83f86"></a>

### Full Adder 간단 표현

기존에는:

```text
assign sum  = a ^ b ^ cin;
assign cout = (a & b) | (b & cin) | (a & cin);
```

처럼 만들었다.

덧셈 결과 전체를 받으면 다음처럼 간단하게 표현할 수도 있다.

```text
assign {cout, sum} = a + b + cin;
```

```text
{ cout, sum }
    ↑     ↑
   MSB   LSB
```

예:

```text
1 + 1 + 0 = 2'b10

cout = 1
sum  = 0
```

같은 방법으로 여러 bit Adder도 표현할 수 있다.

```text
assign {cout, sum[3:0]} = a[3:0] + b[3:0];
```

자료에서도 4bit 덧셈 결과를 Carry와 Sum을 결합한 5bit 출력으로 받는 형태를 사용한다.

---

<a id="notion-3f91d46c18fc802e98dff4a2d83a3463"></a>

## Replication `{N{ }}`

같은 값을 여러 번 반복해서 붙인다.

```text
{4{1'b1}}
```

결과:

```text
4'b1111
```

예:

```text
{3{a}}
```

`a`가 `1`이면:

```text
111
```

이 된다.

---

<a id="notion-3f91d46c18fc80dfa72fd651d7301f68"></a>

## 조건 연산자 `? :`

C의 삼항연산자와 동일한 형태이며, **MUX를 표현할 때 자주 사용**한다.

```text
assign out = sel ? a : b;
```

의미:

```text
sel = 1 → a 출력
sel = 0 → b 출력
```

즉 실제 회로 관점에서는:

```text
       a ──┐
           ├─ MUX ─→ out
       b ──┘
           ↑
          sel
```

복잡한 경우에도 연속해서 사용할 수 있다.

---

<a id="notion-3f91d46c18fc80788b42d5a1fcf29604"></a>

## `parameter`

Module 내부에서 반복해서 사용할 **설정값이나 상수**를 정의할 때 사용한다.

```text
parameter WIDTH = 8;
```

그러면:

```text
input wire [WIDTH-1:0] data;
```

처럼 사용할 수 있다.

즉 `8` 같은 값을 코드 곳곳에 직접 쓰는 대신 이름을 붙여 관리하는 방식이다.

```text
WIDTH = 8
→ [WIDTH-1:0]
→ [7:0]
```

자료에서는 bit 수, 지연값, 상태값 등을 지정하는 용도로 설명한다.

---

<a id="notion-3f91d46c18fc80df9789e4ae9bea280c"></a>

## `always @(*)`에서 의 의미

```text
always @(*) begin
    y = a & b;
end
```

- 는 **Module의 모든 input**이라는 뜻이 아니라, 해당 블록에서 **읽고 있는 신호들을 Sensitivity List에 자동으로 포함**한다는 의미이다.

위 코드는 사실상:

```text
always @(a or b)
```

와 같은 의미다.

따라서 Module에 `c`라는 input이 있어도 블록에서 `c`를 사용하지 않는다면 `c`의 변화 때문에 이 블록을 다시 평가하지 않는다.

---

<a id="notion-3f91d46c18fc80619c69fdec9079f60b"></a>

## 지금 단계에서 기억할 문법

```text
& / | / ^       → bit 단위 연산
&& / || / !     → 논리 참·거짓 연산

&a / |a / ^a    → Vector 전체를 1bit로 축약

{a, b}          → 신호 결합
{4{a}}          → 신호 반복

조건 ? A : B    → 조건에 따라 선택(MUX)

parameter       → Module 설정값/상수

{cout, sum}
= a + b + cin   → Full Adder를 간단하게 표현 가능
```

<br>
