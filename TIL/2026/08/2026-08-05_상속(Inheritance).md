# 상속(Inheritance)

> 날짜: 2026-08-05
> 원본 노션: [링크](https://app.notion.com/p/Inheritance-3b21d46c18fc8040a80cf5482c159a0f)

---

# 📌 C++ 클래스 상속(Inheritance) 기초

### 💡 핵심 개념 한눈에 보기

1. 상속(Inheritance): 기존 클래스(부모 / 상위 / Base Class)의 멤버 변수와 멤버 함수를 그대로 물려받아 새로운 클래스(자식 / 하위 / Derived Class)를 만드는 기능.
1. 상속의 주요 장점:
1. 접근 지정자 protected:
### 💻 상속 기본 예시 코드

```c++
#include <iostream>
using namespace std;

// ============================================================
// 1. 부모 클래스 (Base / Parent Class)
// ============================================================
class person
{
protected: // 자식 클래스에게는 접근을 허용하는 접근 지정자
    char name[20];
    int age;

public:
    person(const char *n = "None", int a = 0)
    {
        int i = 0;
        while (n[i] != '\0' && i < 19)
        {
            this->name[i] = n[i];
            i++;
        }
        this->name[i] = '\0';
        this->age = a;
    }

    void print_person_info(void) const{
        cout << "이름: " << name << ", 나이: " << age << endl;
    }
};

// ============================================================
// 2. 자식 클래스 (Derived / Child Class)
// public 상속: 부모의 public, protected 멤버를 그대로 유지하며 물려받음
// ============================================================
class student : public person
{
private:
    int student_id; // 자식 클래스에서 새로 추가된 멤버 변수

public:
    // 자식 생성자: 부모 생성자(person)를 초기화 리스트에서 먼저 호출해 줌!
    student(const char *n, int a, int id) : person(n, a), student_id(id) {}

    // 자식 클래스에서 새로 추가한 멤버 함수
    void print_student_info(void) const{
        // 부모의 protected 멤버(name, age)에 직접 접근 가능!
        cout << "학번: " << student_id << ", 이름: " << name << ", 나이: " << age << endl;
    }
};

// ============================================================
// main 함수
// ============================================================
int main(void){
    // 1. 부모 객체 생성
    person p("KIM", 40);
    p.print_person_info(); // 부모의 함수 호출

    cout << "----------------------------------------" << endl;

    // 2. 자식 객체 생성
    student s("LEE", 20, 20260001);

    // 자식 객체는 부모로부터 물려받은 멤버 함수를 그대로 사용할 수 있음 (재사용성)
    s.print_person_info();

    // 자식 객체 고유의 멤버 함수 호출
    s.print_student_info();

    return 0;
}
```

### 💡 시험 및 공부용 핵심 체크 포인트!

1. 자식 생성자에서의 부모 생성자 호출 (초기화 리스트)
1. 객체 생성/소멸 순서 (단골 시험 문제 ⭐)
# 📌 [Part 1] 상속과 접근 지정자 (Access Modifiers & Inheritance)

### 💡 핵심 개념

1. 부모 클래스 멤버 접근 권한:
1. 상속 방식(public, protected, private 상속):
| 상속 방식 | 부모 public ➔ 자식에서의 자격 | 부모 protected ➔ 자식에서의 자격 | main() 접근 가능 여부 |
|---|---|---|---|
| public 상속 | public 유지 | protected 유지 | public 멤버만 가능 |
| protected 상속 | protected로 강등 | protected 유지 | 모두 접근 불가 |
| private 상속 | private으로 강등 | private으로 강등 | 모두 접근 불가 |

```c++
#include <iostream>
using namespace std;

class A
{
public:
    int a = 10;
protected:
    int b = 20;
private:
    int c = 30; // 자식 클래스도 직접 접근 불가
};

// [1] public 상속
class B : public A
{
public:
    void f(){
        cout << a << endl; // ⭕ 가능 (public)
        cout << b << endl; // ⭕ 가능 (protected)
        // cout << c << endl; // ❌ 컴파일 에러! (부모 private은 접근 불가)
    }
};

// [2] protected 상속 (외부에서 a, b 접근 불가)
class C : protected A
{
public:
    void f(){
        cout << a << endl; // ⭕ 내부 접근 가능
        cout << b << endl; // ⭕ 내부 접근 가능
    }
};

// [3] private 상속 (내부 접근 가능, 손자 클래스부터는 접근 불가)
class D : private A
{
public:
    void f(){
        cout << a << endl; // ⭕ 내부 접근 가능
        cout << b << endl; // ⭕ 내부 접근 가능
    }
};

int main(void){
    B x;
    cout << x.a << endl; // ⭕ 가능 (public 상속으로 a가 public 유지)
    // cout << x.b << endl; // ❌ 컴파일 에러! (protected는 main에서 접근 불가)
    // cout << x.c << endl; // ❌ 컴파일 에러! (private)
    x.f();

    C y;
    // cout << y.a << endl; // ❌ 컴파일 에러! (protected 상속으로 a가 protected가 됨)
    y.f();

    D z;
    // cout << z.a << endl; // ❌ 컴파일 에러! (private 상속으로 a가 private이 됨)
    z.f();

    return 0;
}
```

# 📌 [Part 2] 캡슐화 예외 — friend 선언

### 💡 핵심 개념

- friend 키워드는 특정 외부 함수나 다른 클래스에게 자신의 private / protected 멤버에 직접 접근할 수 있는 특권을 부여합니다.
- 캡슐화를 깨뜨릴 수 있으므로 꼭 필요한 경우(연산자 오버로딩 등)에만 제한적으로 사용합니다.
```c++
#include <iostream>
using namespace std;

class A
{
private:
    int a = 10;

protected:
    void f(){
        cout << "A::a = " << a << endl;
    }

    // friend 선언: B 클래스와 h() 함수에게 모든 멤버 접근 권한 허용
    friend class B;
    friend void h();
};

class B
{
public:
    void g(){
        A x;
        x.a = 40; // ⭕ friend이므로 private 변수 변경 가능
        x.f();    // ⭕ friend이므로 protected 함수 호출 가능
    }
};

void h(){
    A x;
    x.a = 50; // ⭕ friend 함수이므로 private 변수 변경 가능
    x.f();
}

int main(void){
    B y;
    y.g();
    h();

    return 0;
}
```

# 📌 [Part 3] 생성자 / 소멸자 실행 순서 및 매개변수 전달

### 💡 핵심 개념

1. 호출 순서:
1. 부모 생성자 매개변수 전달:
```c++
#include <iostream>
using namespace std;

class A
{
public:
    A(int n)
    {
        cout << "부모 생성자 A: " << n << endl;
    }
    ~A()
    {
        cout << "부모 소멸자 ~A" << endl;
    }
};

class B : public A
{
public:
    // 초기화 리스트를 통해 부모 생성자 A(x + 1) 호출
    B(int x) : A(x + 1)
    {
        cout << "자식 생성자 B: " << x << endl;
    }
    ~B()
    {
        cout << "자식 소멸자 ~B" << endl;
    }
};

int main(void){
    {
        B x(3); // A(4) 실행 -> B(3) 실행
    } // 블록을 벗어나며 x 소멸 -> ~B() 실행 -> ~A() 실행

    return 0;
}
```

# 📌 [Part 4] 캐스팅 (Upcasting & Downcasting)

### 💡 핵심 개념

1. 업캐스팅 (Upcasting):
1. 다운캐스팅 (Downcasting):
```c++
#include <iostream>
using namespace std;

class car
{
public:
    int price;
};

class truck : public car
{
public:
    double load;
};

class van : public car
{
public:
    int passenger;
};

// 업캐스팅 활용: car를 상속받은 모든 자식 객체를 인자로 받을 수 있음
void prt_price(car *p){
    cout << "가격: " << p->price << endl;
}

int main(void){
    truck x;
    van y;

    x.price = 1200;
    x.load = 2.5;
    y.price = 2400;

    // 1. Upcasting (자동 형변환)
    car *p1 = &x; // truck* -> car*
    prt_price(&x);
    prt_price(&y);

    // 2. Downcasting (명시적 형변환)
    // cout << p1->load; // ❌ 컴파일 에러! (car 포인터는 load 멤버를 모름)
    cout << "트럭 적재량: " << ((truck *)p1)->load << endl; // ⭕ 명시적 다운캐스팅

    return 0;
}
```

# 📌 [Part 5] 다중 상속과 가상 상속 (Virtual Inheritance)

### 💡 핵심 개념

1. 다중 상속 생성자 순서: class C : public A, public B ➔ 선언된 순서대로 A 생성자 ➔ B 생성자 ➔ C 생성자 호출.
1. 이름 충돌 (Ambiguity): 여러 부모가 동일한 함수/변수 이름을 가질 경우 범위 지정 연산자(x.A::func())로 명시해야 합니다.
1. 다이아몬드 상속과 가상 상속 (virtual public):
```c++
#include <iostream>
using namespace std;

// [1] 할아버지 클래스
class A
{
public:
    int a;
    A() { cout << "A 생성자" << endl; }
};

// [2] Virtual Inheritance (가상 상속) 적용
class B1 : virtual public A
{
public:
    int b1;
};

class B2 : virtual public A
{
public:
    int b2;
};

// [3] 다중 상속
class C : public B1, public B2
{
public:
    int c;
};

int main(void){
    C x;
    // 가상 상속을 하지 않으면 A가 2번 생성되어 x.a 접근 시 컴파일 에러 발생!
    x.a = 100; // ⭕ virtual 상속 덕분에 A::a에 모호성 없이 직접 접근 가능

    cout << "x.a = " << x.a << endl;
    cout << "x.B1::a = " << x.B1::a << endl; // x.a와 동일한 메모리 공유

    return 0;
}
```



