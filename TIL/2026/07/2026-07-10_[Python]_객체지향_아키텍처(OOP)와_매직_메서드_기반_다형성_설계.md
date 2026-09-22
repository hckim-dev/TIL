# \[Python\] 객체지향 아키텍처(OOP)와 매직 메서드 기반 다형성 설계

> 날짜: 2026-07-10
> 원본 노션: [링크](https://app.notion.com/p/Python-OOP-3991d46c18fc8014885fcfa8c2ea3449)

<!-- notion-page-id: 3991d46c18fc8014885fcfa8c2ea3449 -->
<!-- notion-title: "[Python] 객체지향 아키텍처(OOP)와 매직 메서드 기반 다형성 설계" -->

---

<a id="notion-3991d46c18fc8073994def06c0540a1b"></a>

# 🛠️ \[Chapter 12\]

<a id="notion-3991d46c18fc80d3be08dfb0f2d2344b"></a>

### 1\. 객체지향 프로그래밍(OOP)과 변수의 스코프(Scope) 격리

- <strong>함수 기반의 전역 한계 (</strong><strong>`[12-1]`</strong><strong>) :</strong> `global` 키워드로 전역 장부를 강제 조작하거나 사용자별 인덱스 바구니(`s[n]`)를 파내는 방식은 프로젝트가 커질수록 상태 오염 위험이 심해집니다.
- <strong>클래스와 인스턴스의 본질 (</strong><strong>`[12-2]`</strong><strong>,</strong> <strong>`[12-3]`</strong><strong>) :</strong> `class`는 새로운 하나의 데이터 타입을 정의하는 행위이며, 이를 통해 생성된 개별 인스턴스(`usr1`, `usr2`)들은 서로의 메모리 공간을 절대 침범하지 않는 완전한 독립성을 보장받습니다.
- <strong>공용 변수 vs 독립 변수 (</strong><strong>`[12-4]`</strong><strong>,</strong> <strong>`[12-5]`</strong><strong>) :</strong>

  - `CLS.a`는 모든 객체가 단 하나의 주소를 공유하며 같이 누적 연산하는 클래스 변수입니다.
  - `self.b`는 인스턴스 전용 독립 변수입니다. `self.a += x`와 같이 대입 연산을 가하는 순간, 공용 변수와의 연결을 완전히 끊고 자기 지갑 속에 전용 변수를 새로 파내어 결별합니다.

<a id="notion-3991d46c18fc808394b2cbf2c1ff16ec"></a>

### 2\. 라이프 사이클 특수 메서드와 매직 연산자 오버로딩

- <strong>생성 초기화자</strong> **`__init__`** <strong>(</strong><strong>`[12-6]`</strong><strong>,</strong> <strong>`[12-7]`</strong><strong>,</strong> <strong>`[12-8]`</strong><strong>) :</strong> 인스턴스가 메모리에 생성되는 순간 자동으로 강제 호출되는 스페셜 메서드입니다. `self.s = x`와 같이 객체가 살아 숨 쉬는 동안 사용할 기본 데이터를 안전하게 세팅(초기화)합니다. `__doc__`은 클래스 내부에 적어둔 주석 설명문을 바깥으로 반환해 줍니다.
- <strong>소멸 자원 반납</strong> **`__del__`** <strong>(</strong><strong>`[12-9]`</strong><strong>,</strong> <strong>`[12-10]`</strong><strong>) :</strong> `del 인스턴스` 명령이나 가비지 컬렉션에 의해 객체가 메모리에서 완전히 파괴될 때 자동으로 트리거됩니다. 임대 수량 감소(`cnt -= 1`) 등 사후 정리를 완수합니다.
- <strong>연산자 오버로딩</strong> <strong>`__add__`</strong><strong>,</strong> <strong>`__gt__`</strong><strong>,</strong> **`__abs__`** <strong>(</strong><strong>`[12-11]`</strong><strong>,</strong> <strong>`[12-12]`</strong><strong>) :</strong> 파이썬의 모든 빌트인 연산자와 내장 함수(더하기 `+`, 크기 비교 `>`, 절대값 `abs()`)는 내부적으로 쌍밑줄 매직 메서드로 링크되어 있습니다. 클래스 내부에 이를 재정의하면 내가 만든 객체끼리도 사칙연산과 크기 비교가 가능해집니다.

```python
# [12-12] 매직 메서드 오버로딩 기반 커스텀 연산 구조
class CLS:
    def __init__(self, x): self.s = x
    def __add__(self, x): return self.s + x   # 객체 + 숫자 연산 가능하도록 뚫어줌
    def __gt__(self, x): return self.s > x.s  # 객체 > 객체 크기 비교 가능하도록 뚫어줌

usr1 = CLS(10)
print(usr1 + 30)  # 출력: 40 (usr1.__add__(30)이 백엔드에서 자동 호출됨)
```

<a id="notion-3991d46c18fc805fbba7ec81f8e03421"></a>

### 3\. 상속(Inheritance) 아키텍처와 메서드 탐색 순서(MRO)

- <strong>상속과</strong> **`super().__init__()`** <strong>(</strong><strong>`[12-13]`</strong><strong>,</strong> <strong>`[12-14]`</strong><strong>) :</strong> `class 자식(부모):` 형태로 선언하면 부모의 변수와 메서드를 그대로 물려받습니다. 자식 쪽에서 생성자를 재정의할 때는 반드시 `super().__init__(x)`를 수동으로 쳐서 올려보내 주어야 부모가 가진 기초 초기화 방들이 정상적으로 개설됩니다.
- <strong>메서드 오버라이딩과 다중 상속 (</strong><strong>`[12-15]`</strong><strong>,</strong> <strong>`[12-16]`</strong><strong>) :</strong> 부모가 물려준 메서드가 마음에 안 들면 자식 클래스에서 똑같은 이름으로 메서드를 재정의하여 덮어쓸(Overriding) 수 있습니다. 여러 부모에게 한 번에 상속받는 다중 상속도 가능합니다.
- <strong>MRO(Method Resolution Order) 탐색 경로 (</strong><strong>`[12-15]`</strong><strong>,</strong> <strong>`[12-16]`</strong><strong>) :</strong> 동명의 메서드가 겹칠 때 누구 것을 먼저 실행할지는 **`클래스명.mro()`** 결과 순서(좌측 부모 우선)에 따라 파이썬 인터프리터가 엄격하게 줄을 세워 찾아갑니다.

<a id="notion-3991d46c18fc806686e4c9d5346a4e99"></a>

### 4\. 장부 제어 데코레이터: 클래스 메서드와 스태틱 메서드

- **`@classmethod`** <strong>(</strong><strong>`[12-17]`</strong><strong>) :</strong> 매개변수로 인스턴스(`self`) 대신 클래스 자체(<strong>`cls`</strong>)를 넘겨받습니다. 클래스 변수(`cls.s`)에 다이렉트로 접근하여 제어할 때 사용합니다.
- **`@staticmethod`** <strong>(</strong><strong>`[12-17]`</strong><strong>) :</strong> `self`도 `cls`도 아예 인자로 받지 않는 완전히 독립적인 방입니다. 클래스 내부에 묶여는 있지만, 인스턴스나 클래스 상태를 건드리지 않고 유틸리티 성격의 독립 함수를 돌릴 때 주입합니다.

```python
# [12-17] 데코레이터 메서드 2종 세트 호출 비교
class My_CLS:
    s = 0
    @classmethod
    def c_method(cls): print("클래스 직접 제어:", cls.s)
    @staticmethod
    def s_method(): print("인자 없는 독립 함수:", My_CLS.s)

My_CLS.c_method()  # 객체를 찍지 않고 클래스 이름으로 바로 호출 가능
My_CLS.s_method()  # 객체를 찍지 않고 클래스 이름으로 바로 호출 가능
```

<br>
