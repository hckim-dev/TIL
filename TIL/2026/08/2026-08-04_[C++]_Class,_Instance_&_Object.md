# \[C++\] Class, Instance &amp; Object

> 날짜: 2026-08-04
> 원본 노션: [링크](https://app.notion.com/p/C-Class-Instance-Object-3b11d46c18fc808aab32e093aca21d93)

<!-- notion-page-id: 3b11d46c18fc808aab32e093aca21d93 -->
<!-- notion-title: "[C++] Class, Instance & Object" -->

---

<a id="notion-3b21d46c18fc8074bcedd3470c6cf38b"></a>

# 📌 C++ 객체지향 프로그래밍(OOP) 및 클래스 기초

<a id="notion-3b21d46c18fc8062888feec77781bf8e"></a>

## 1\. 절차지향(Procedural) vs 객체지향(OOP)

|  |  |  |
| --- | --- | --- |
| **구분** | **절차지향 프로그래밍 (Procedural)** | **객체지향 프로그래밍 (OOP)** |
| **핵심 개념** | 순차적인 **순서(Procedure)와 함수** 중심 설계 | 데이터와 동작을 하나로 묶은 **객체(Object)** 중심 설계 |
| **데이터 처리** | 데이터와 함수가 분리됨 (전역 변수 활용 많음) | 객체 내부의 데이터는 스스로 관리 (캡슐화) |
| **장점** | 처리 속도가 빠르고 구조가 단순함 | 코드 재사용성, 확장성, 유지보수성이 뛰어남 |
| **단점** | 대형 프로젝트 시 데이터 추적이 어려움 | 설계가 복잡하며 객체 간 통신 오버헤드가 발생할 수 있음 |

<a id="notion-3b21d46c18fc80beadcde07820816f0b"></a>

## 2\. 객체지향의 핵심 핵심 용어 정리

- <strong>Object (객체)</strong>: 현실 세계에 존재하는 사물, 현상, 개념 등 **속성(상태)과 동작(기능)을 가진 모든 것**.
- <strong>Abstraction (추상화)</strong>: 객체들의 공통적인 특징(속성, 기능)을 뽑아내어 코드로 정의하는 과정.
- <strong>Class (클래스)</strong>: 추상화를 통해 만들어진 <strong>설계도(틀)</strong>. (C++에서는 `struct`도 클래스와 동일한 역할을 수행)
- <strong>Instance (인스턴스)</strong>: 클래스(설계도)를 바탕으로 메모리에 실제로 생성된 <strong>실체(객체)</strong>.

<a id="notion-3b21d46c18fc80febf52dcbbac866006"></a>

## 3\. C++에서의 `struct`와 `class`

C++은 C의 `struct`를 확장하여 **내부에 함수(메서드)를 포함하고 접근 지정자를 사용할 수 있도록** 만들었습니다.

- C++에서 `struct`와 `class`는 기능적으로 **99% 동일**합니다.
- **유일한 차이점**: 기본 접근 지정자 (Default Access Specifier)

  - `struct`: 명시하지 않으면 기본값이 **`public`**
  - `class`: 명시하지 않으면 기본값이 **`private`**

<a id="notion-3b21d46c18fc803ebb89d6ee878ad4d8"></a>

## 4\. 접근 지정자 (Access Specifiers) 및 정보 은닉

클래스 내부 멤버 변수/함수에 대한 외부 접근 권한을 제어하여 데이터의 왜곡 방지 및 보안성(정보 은닉)을 확보합니다.

- <strong>`private`</strong>: 클래스(구조체) 내부 멤버 함수에서만 접근 가능 (**데이터 보호**).
- <strong>`public`</strong>: 클래스 외부(예: `main()` 함수 등) 어디서나 접근 가능 (**인터페이스 제공**).
- <strong>`protected`</strong>: 상속 관계의 자식 클래스까지 접근 허용 (상속 다뤄질 때 사용).

<a id="notion-3b21d46c18fc807283b2f583ba61626a"></a>

## 5\. 실습 예제 코드 및 개선 (이율 계산 클래스)

```cpp
#include <iostream>
using namespace std;

// C++ 구조체 (기본 접근 지정자는 public)
struct Account
{
private:
    // 정보 은닉: 외부에서 직접 수정할 수 없는 데이터
    double interest_rate = 0.02; // 이율 (2%)
    double total_balance = 0.0;  // 총 잔액

    // 내부 전용 출력 메서드
    void disp_total() const{
        cout << "현재 총 잔액: " << total_balance << '\n';
    }

public:
    // 외부 공개 인터페이스: 입금 및 이자 계산 메서드
    double deposit(int amount){
        total_balance += amount * (1.0 + interest_rate);
        disp_total();
        return total_balance;
    }

    // 읽기 전용 잔액 조회 메서드 (Getter)
    double getTotalBalance() const{
        return total_balance;
    }
};

int main(){
    Account my_account; // 인스턴스 생성

    // my_account.total_balance = 10000; // ❌ private 멤버이므로 외부 접근 불가 (컴파일 에러)

    my_account.deposit(50);  // 50 * 1.02 = 51 출력
    my_account.deposit(100); // 51 + 102 = 153 출력

    return 0;
}
```

<a id="notion-3b21d46c18fc80439c03cb942f8e81ed"></a>

### 💡 요약 한 줄

> **C++ 객체지향의 핵심**: 변수와 함수를 하나로 묶고(`캡슐화`), `private` 변수를 통해 데이터를 안전하게 보호하며, 외부에는 `public` 함수(인터페이스)만 열어두는 것\!

<a id="notion-3b21d46c18fc803e922ce20007574b2c"></a>

# 📌 C++ 클래스 기초

```cpp
#include <iostream>
using namespace std;

class mart_calc
{
private:
    int *price_history;
    int history_count;
    int max_size;
    double tax;

public:
		// Default Parameter 형식의 Constructor
    mart_calc(int size = 5, double tax = 0.01);

		// 소멸자(destructor)
    ~mart_calc(void);

		// Member Function의 Overloading
    void buy(int price);
    void buy(int price, double custom_tax);

    void set_tax(double tax);

    void print_history(void);
}; // 함수가 아니므로 반드시 ; 사용

// 생성자 외부 정의 (new를 통한 동적 메모리 할당)
mart_calc::mart_calc(int size, double tax)
{
    this->max_size = size;
    this->tax = tax;
    this->history_count = 0;
    this->price_history = new int[max_size]; // 동적 메모리 할당
}

mart_calc::~mart_calc(void)
{
    delete[] price_history; // delete는 new로 만든 포인터에만 쓸 수 있음
}

// this 포인터 활용: 멤버 변수 tax와 매개변수 tax 이름 충돌 해결
void mart_calc::set_tax(double tax){
    this->tax = tax; // this->tax는 private 멤버 변수, 우변 tax는 매개변수
}

// Overloading 1
void mart_calc::buy(int price){
    if (history_count < max_size)
    {
        price_history[history_count] = price * (1 + tax);
        history_count++;
    }
}

// Overloading 2
void mart_calc::buy(int price, double custom_tax){
    if (history_count < max_size)
    {
        price_history[history_count] = price * (1 + custom_tax);
        history_count++;
    }
}

void mart_calc::print_history(void){
    cout << "=== 구매 내역 (기본 세율: " << tax * 100 << "%) ===" << endl;
    for (int i = 0; i < history_count; i++)
    {
        cout << i + 1 << "번째 결제 금액: " << price_history[i] << endl;
    }
}

int main(void){
    mart_calc calc1; // default 생성자는 괄호 붙이면 안됨 { calc1() [X], calc [O] }
    mart_calc calc2(10, 0.05);

    calc1.buy(100);        // buy(int) 호출
    calc1.buy(200, 0.1);   // buy(int, double) 호출

    calc2.set_tax(0.02);
    calc2.buy(500);        // 변경된 세율 0.02 적용

    // 결과 출력
    calc1.print_history();
    cout << endl;
    calc2.print_history();

    return 0;
}
```

<a id="notion-3b21d46c18fc80749bfeee35e6bcda0c"></a>

# 📌 Static 멤버 및 클래스 속성 (초기화 리스트 / `const` 함수)

<a id="notion-3b21d46c18fc800f8e23dc61600c524b"></a>

### 💡 핵심 개념 한눈에 보기

1. **`static`** <strong>멤버 변수</strong>: 인스턴스 생성 여부와 상관없이 **프로그램 전체에서 단 1개만 존재**하는 클래스 변수 (클래스 외부에 `int A::s = 0;` 형태로 반드시 정의 필요).
2. **`static`** <strong>멤버 함수</strong>: 인스턴스 없이 `A::fc()`로 호출 가능하며, <strong>`static`</strong>**이 아닌 일반 멤버 변수/함수에는 접근 불가능**.
3. **멤버 초기화 리스트**: `const` 멤버 변수나 참조자는 생성자 괄호 `{}` 안에서 대입할 수 없으므로 <strong>반드시 초기화 리스트(</strong><strong>`: age(a)`</strong><strong>)를 사용</strong>.
4. **`const`** <strong>멤버 함수</strong>: `int func() const` 형태로 작성하며, 함수 내부에서 **클래스 멤버 변수의 값을 변경하는 것을 금지**함.

```cpp
#include <iostream>
using namespace std;

int g_var = 10; // 전역 변수 (Global Variable)

class student
{
public:
    // [1] 변수 종류별 정의
    static int student_count; // Class 변수 (모든 인스턴스가 공유)
    int student_id;           // Instance 변수
    const int age;            // const 멤버 변수 (초기화 리스트 필수)

    // [2] 생성자 및 멤버 초기화 리스트
    student(int id, int a) : student_id(id), age(a)
    {
        student_count++; // static 변수 증가
    }

    // [3] 일반 멤버 함수 (모든 변수에 접근 가능)
    void print_info(int extra_code) // extra_code: 매개변수(지역변수){
    {
        int local_val = 100;        // local_val: 지역변수
        cout << "ID: " << student_id << ", Age: " << age << ", Total: " << student_count << endl;
        cout << "Sum: " << g_var + student_id + extra_code + local_val << endl;
    }

    // [4] const 멤버 함수 (멤버 변수 수정 불가, 읽기만 가능)
    int get_age_plus(int inc) const{
        // age += inc; // ❌ 에러! const 함수 내에서는 멤버 변수 수정 불가
        int result = age + inc; // 매개변수나 지역 변수는 변경 가능
        return result;
    }

    // [5] static 멤버 함수 (인스턴스 없이 호출 가능)
    static void print_count(void){
        // cout << student_id; // ❌ 에러! static 함수는 일반 instance 변수 접근 불가
        cout << "현재 등록된 학생 수: " << student_count << endl;
    }
};

// [필수] static 멤버 변수 클래스 외부 정의 및 초기화
int student::student_count = 0;

int main(void){
    // static 함수는 객체 생성 없이 바로 호출 가능
    student::print_count(); // 0

    // 인스턴스 생성 (초기화 리스트 작동)
    student s1(101, 20);
    student s2(102, 22);

    s1.print_info(5);

    // const 멤버 함수 호출
    cout << "Age + 5 = " << s1.get_age_plus(5) << endl;

    // static 변수 접근 방식 (클래스명::변수명 권장)
    cout << "s1을 통한 접근: " << s1.student_count << endl;     // 2
    cout << "클래스를 통한 접근: " << student::student_count << endl; // 2

    return 0;
}
```

<a id="notion-3b21d46c18fc80d4adf1d1d3fcacd264"></a>

# 📌 C++ 클래스 응용 (Template 클래스 &amp; Member Pointer)

<a id="notion-3b21d46c18fc8014b132d86c50ca1205"></a>

### 💡 핵심 개념 한눈에 보기

1. <strong>클래스 템플릿 (</strong><strong>`template <typename T>`</strong><strong>)</strong>: 다양한 데이터 타입을 하나의 클래스 구조로 다룰 수 있게 해주는 기능 (인스턴스 생성 시 `mart_calc<int> a;` 처럼 타입 명시 필요).
2. <strong>클래스 멤버 포인터 (</strong><strong>`int A::*pp = &A::p;`</strong><strong>)</strong>: 특정 객체의 주소가 아닌, 클래스 내부에서 해당 변수가 위치한 상대적 오프셋(Offset)을 저장하는 포인터.
3. **`.*`** <strong>연산자</strong>: 객체와 멤버 포인터를 조합하여 실제 메모리 값에 접근할 때 사용 (`a.*pp`).

```cpp
#include <iostream>
using namespace std;

// ============================================================
// 1. Template 클래스 예제
// ============================================================
template <typename T>
class mart_calc
{
public:
    T total = 0;

    mart_calc(T price)
    {
        total += price;
    }

    void buy(T price){
        total += price;
    }
};

// ============================================================
// 2. Class Member Pointer 예제
// ============================================================
class product
{
public:
    int price = 1000;
    int amount = 50;
};

// 인스턴스 참조(p)와 클래스 멤버 오프셋(dst)을 전달받는 함수
void print_member(product &p, int product::*dst){
    // .* 연산자로 객체의 해당 오프셋 위치 값 읽기
    cout << "멤버 변수 값: " << p.*dst << endl;
}

// ============================================================
// main 함수
// ============================================================
int main(void){
    // ----- 1. Template 클래스 사용 -----
    mart_calc<int> calc_int(10);
    calc_int.buy(20.5); // int 타입이므로 20만 더해짐 (20.5 -> 20)

    mart_calc<double> calc_double(3.5);
    calc_double.buy(10.0);

    cout << "int total: " << calc_int.total << endl;       // 30
    cout << "double total: " << calc_double.total << endl; // 13.5
    cout << "----------------------------------------" << endl;

    // ----- 2. Member Pointer 사용 -----
    product item;

    // 멤버 포인터 변수 선언 및 오프셋 대입
    int product::*ptr = &product::price;

    cout << "직접 접근: " << item.*ptr << endl; // 1000

    item.price = 2000;
    cout << "값 변경 후: " << item.*ptr << endl; // 2000

    // 함수에 객체와 멤버 오프셋을 전달하여 출력
    print_member(item, &product::price);  // price 오프셋 전달 (2000)
    print_member(item, &product::amount); // amount 오프셋 전달 (50)

    return 0;
}
```

<br>
