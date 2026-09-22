# \[C++\] 다형성(Polymorphism)

> 날짜: 2026-08-05
> 원본 노션: [링크](https://app.notion.com/p/C-Polymorphism-3b21d46c18fc80d0b8bfd45ff041414e)

<!-- notion-page-id: 3b21d46c18fc80d0b8bfd45ff041414e -->
<!-- notion-title: "[C++] 다형성(Polymorphism)" -->

---

<a id="notion-3b31d46c18fc8079875cfcdc96293f28"></a>

# 📌 \[Part 1\] 가상 함수(Virtual Function)와 동적 바인딩

<a id="notion-3b31d46c18fc80fcb51ff85e23c98dbd"></a>

### 💡 핵심 개념

1. <strong>오버라이딩(Overriding)</strong>: 부모 클래스의 멤버 함수를 자식 클래스에서 재정의하는 것.
2. <strong>정적 바인딩 (Static Binding)</strong>:

   - 일반 멤버 함수 호출 시 **포인터/참조자의 타입**을 기준으로 컴파일 시점에 호출할 함수 결정 (속도가 빠름).
3. <strong>가상 함수 &amp; 동적 바인딩 (Dynamic Binding)</strong>:

   - `virtual` 키워드를 사용하면 **실제 가리키는 객체의 타입**을 기준으로 실행 시점(Run-time)에 호출할 함수를 결정.
   - `override` 키워드(C++11): 부모의 가상 함수를 올바르게 재정의했는지 컴파일러가 검사해 주는 키워드.

```cpp
#include <iostream>
using namespace std;

class A
{
public:
    // virtual: 동적 바인딩 활성화
    virtual void prt(){
        cout << "A" << endl;
    }
};

class B : public A
{
public:
    // override: 명시적 재정의 검사
    virtual void prt() override{
        cout << "B" << endl;
    }
};

void print_info(A *p){
    p->prt(); // p가 가리키는 실제 객체(A 또는 B)의 prt()가 호출됨!
}

int main(void){
    A x;
    B y;

    print_info(&x); // 출력: A
    print_info(&y); // 출력: B (A* 포인터지만 B의 함수 호출)

    return 0;
}
```

<a id="notion-3b31d46c18fc8058a66df31b71fa6da1"></a>

# 📌 \[Part 2\] 가상 소멸자 (Virtual Destructor)

<a id="notion-3b31d46c18fc80f196eef919ba751d95"></a>

### 💡 핵심 개념

- **문제 상황**: 부모 클래스 포인터로 자식 객체를 동적 할당(`new B`)한 뒤 `delete` 할 때, 부모 소멸자에 `virtual`이 없으면 **자식 클래스의 소멸자가 호출되지 않아 메모리 누수가 발생**합니다.
- **해결책**: 상속 관계에 있는 부모 클래스의 소멸자에는 <strong>반드시</strong> <strong>`virtual`</strong>**을 붙여야 합니다.** 부모 소멸자에 `virtual`이 붙으면 자식 소멸자도 자동으로 `virtual` 지정이 됩니다.

```cpp
#include <iostream>
using namespace std;

class A
{
public:
    A() { cout << "A 생성자" << endl; }
    // 부모 소멸자에 virtual 필수!
    virtual ~A() { cout << "~A 소멸자" << endl; }
};

class B : public A
{
public:
    B() { cout << "B 생성자" << endl; }
    ~B() override { cout << "~B 소멸자" << endl; } // 자동으로 virtual 적용됨
};

int main(void){
    A *p = new B; // 업캐스팅 포인터
    delete p;     // ~B() 호출 후 ~A() 순서로 정상 해제!

    return 0;
}
```

<a id="notion-3b31d46c18fc80479351f72ff35532fd"></a>

# 📌 \[Part 3\] 순수 가상 함수 &amp; 추상 클래스 (Abstract Class)

<a id="notion-3b31d46c18fc80e4a333dea3450ef351"></a>

### 💡 핵심 개념

1. <strong>순수 가상 함수 (Pure Virtual Function)</strong>:

   - `virtual void move_pos() = 0;` 처럼 구현부 없이 `= 0;`으로 선언한 함수.
2. <strong>추상 클래스 (Abstract Class)</strong>:

   - 순수 가상 함수를 하나라도 포함하고 있는 클래스.
   - **객체(인스턴스)를 직접 생성할 수 없음** (`items x;` ❌ 에러).
   - **인터페이스 역할**: 자식 클래스에게 특정 함수들을 반드시 오버라이딩하도록 강제할 때 사용.

```cpp
#include <iostream>
using namespace std;

// 추상 클래스 (인터페이스 역할)
class items
{
public:
    virtual void move_pos()= 0;   // 순수 가상 함수
    virtual void check_crash()= 0; // 순수 가상 함수
};

class ufo : public items
{
public:
    // 자식 클래스는 순수 가상 함수를 반드시 구현해야 인스턴스 생성 가능
    virtual void move_pos() override{
        cout << "ufo: move" << endl;
    }

    virtual void check_crash() override{
        cout << "ufo: check crash" << endl;
    }
};

int main(void){
    // items item; // ❌ 컴파일 에러! (추상 클래스는 객체 생성 불가)

    items *obj = new ufo(); // ⭕ 추상 클래스 포인터 사용 가능 (인터페이스 통일)
    obj->move_pos();

    delete obj;
    return 0;
}
```

<a id="notion-3b31d46c18fc80fa83cbdc4ae60bc503"></a>

# 📌 \[Part 4\] 연산자 오버로딩 (Operator Overloading)

<a id="notion-3b31d46c18fc80a08c3ce53b09de2765"></a>

### 💡 핵심 개념

1. **멤버 함수 방식의 연산자 오버로딩**:

   - 첫 번째 피연산자(좌항)는 무조건 자기 자신 객체(`this` 포인터)가 됩니다.
   - `x + y` 연산은 내부적으로 `x.operator+(y)` 형태로 해석됩니다.
2. <strong>연속 연산 (Cascading)</strong>:

   - `cout << a << b` 처럼 연산자를 연속으로 사용하려면 연산자 오버로딩 함수가 <strong>자기 자신의 참조자(</strong><strong>`this`</strong><strong>)나 객체</strong>를 반환해야 합니다.

```cpp
#include <iostream>
using namespace std;

class myout
{
public:
    int n;

    myout(int in = 0) : n(in) {}

    // + 연산자 오버로딩 (x + y -> x.operator+(y))
    int operator+(const myout &y)
    {
        return this->n + y.n;
    }

    // << 연산자 오버로딩 (연속 연산을 위해 자기 자신 객체 반환)
    myout operator<<(int m)
    {
        this->n += m;
        return *this; // 참조/객체 반환으로 Cascading 연산 가능
    }
};

int main(void){
    myout x(10), y(20);

    cout << "합: " << (x + y) << endl; // 30

    // (x << 10)의 실행 결과로 반환된 x에 다시 << 20, << 30 실행
    cout << (x << 10 << 20 << 30).n << endl; // 10 + 10 + 20 + 30 = 70

    return 0;
}
```

<a id="notion-3b31d46c18fc803fbae3da02232fd417"></a>

# 💡 \[참고 항목 \*\] RTTI &amp; 외부 함수 연산자 오버로딩

<a id="notion-3b31d46c18fc803b8410ca883b0612d5"></a>

### 1\. RTTI (Run Time Type Information)

- `typeid(*p)` 및 `typeid(*p).name()`을 사용하여 실행 시점에 포인터가 가리키는 실제 객체의 타입 정보를 확인하는 기능.
- 필요 시 정적 바인딩(`p->A::f()`)을 강제로 지정할 때 활용.

<a id="notion-3b31d46c18fc804290c1f022e356929d"></a>

### 2\. 외부 전역 함수에 의한 연산자 오버로딩

- 좌항 피연산자가 내 클래스의 객체가 아닐 때(예: `2 * obj` 또는 `cout << obj`) 클래스 외부에서 전역 함수로 작성하며, `friend` 키워드를 통해 클래스 내 `private` 멤버 접근 권한을 부여함.

```cpp
template <typename T>
void prt_info(T *p)
{
    // 코드 설계
    if (typeid(*p) == typeid(square))
    {
        cout << ((square *)p)->color_index << endl;
        cout << ((square *)p)->width << endl;
    }
    else if (typeid(*p) == typeid(rectagle))
    {
        cout << ((rectagle *)p)->color_index << endl;
        cout << ((rectagle *)p)->width << endl;
        cout << ((rectagle *)p)->height << endl;
    }
}

((C *)p)->C::f(); // 함수 이름이 다 같을 때

---

class B
{
public:
    int a;
    // 외부 함수 operator* 에 private/protected 접근 권한 부여
    friend B operator*(const B &x, int y);
};

B operator*(const B &x, int y)
{
    B r;
    r.a = x.a + (y * 2);
    return r;
}
```
