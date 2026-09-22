# \[STM32\] GPIO 제어, 필수 키워드(volatile/const) 및 매크로 정리

> 날짜: 2026-07-15
> 원본 노션: [링크](https://app.notion.com/p/STM32-GPIO-volatile-const-39d1d46c18fc805a9df0d6f9334839dc)

<!-- notion-page-id: 39d1d46c18fc805a9df0d6f9334839dc -->
<!-- notion-title: "[STM32] GPIO 제어, 필수 키워드(volatile/const) 및 매크로 정리" -->

---

<a id="notion-39e1d46c18fc80778748d9ec2c2a4efc"></a>

# ⚡ Push-Pull vs Open-Drain

<a id="notion-39e1d46c18fc80718ddcfa39b756b226"></a>

## 🌗 1. Push-Pull: "끌 때(Off/Low)도 칩이 직접 일을 해야 하는 구조"

- **동작 특징:** 핀을 'Off(Low, 0V)'로 만들 때, 칩 내부의 아래쪽 N-MOS 스위치가 켜지면서 외부 선에 남아있던 전하를 칩 내부의 그라운드(\$V\_\{SS\}\$)로 싹 잡아당겨서 태워버립니다.
- **전류 소모 관점:**

  - 신호를 끌 때(Off) 외부 회로나 선로에 뭉쳐있던 전류(기생 커패시턴스 등)가 **칩 내부로 쏟아져 들어오기 때문에**, 칩 내부 드라이버가 이 전류를 그라운드로 빼내기 위해 전력을 능동적으로 소비하게 됩니다.
  - 즉, 켤 때(High)뿐만 아니라 **끌 때(Low)도 칩이 직접 힘을 써야 하므로** 내부 드라이버의 전력 부담이 상시 존재합니다.

<a id="notion-39e1d46c18fc80bb808ed8e391c450a8"></a>

## 🏢 2. Open-Drain: "칩은 손 떼고, 외부 저항이 전원을 끌어다 쓰는 구조"

- **동작 특징:** 핀을 'Off(High, 1)'로 만들 때, 칩 내부의 스위치는 그냥 완전히 열려(Open) 아무 일도 하지 않는 상태(Hi-Z)가 됩니다. 대신 외부에 매달린 풀업 저항이 전원(\$V\_\{DD\}\$)을 부하(Load) 쪽으로 자연스럽게 끌어다(Pull-up) 줍니다.
- **전류 소모 관점:**

  - 신호가 꺼져서 High가 될 때, **MCU 내부에서는 전류를 한 방울도 쓰지 않습니다.** 오직 외부 저항과 외부 전원 라인 사이에서만 미세한 전류가 흐를 뿐입니다.
  - 즉, 칩 내부 드라이버가 능동적으로 밀고 당기는 힘을 쓸 필요가 전혀 없기 때문에, **MCU 칩 자체의 발열과 내부 전력 소비를 극적으로 줄일 수 있습니다.**
  - 특히 전력 소모가 극도로 적어야 하는 센서 버스(I2C 등)나 배터리 기반의 디바이스에서, 여러 장치가 동시에 물려있을 때 칩들의 내부 전류 부담을 최소화하는 최적의 아키텍처가 됩니다.

<a id="notion-39e1d46c18fc806896fdd5c73451e9db"></a>

## 📊 3줄 요약

- **Push-Pull:** High든 Low(Off)든 **칩 내부 스위치들이 상시 일을 하며 전류를 밀고 당겨야 하므로** 칩 내부 드라이버의 상시 전력 소모와 부담이 큼.
- **Open-Drain:** Off(High) 상태가 되면 칩 내부는 완전히 연결을 끊고 휴식을 취하며, **외부 저항이 대신 전원을 끌어다 신호를 채워주기 때문에** 칩 자체의 전류 소모와 드라이버 부담이 대폭 감소함.
- **결론:** 칩 내부의 전력 스트레스와 대기 소모 전류를 줄이고 안전하게 신호를 띄우려면 외부 전원과 저항의 힘을 빌리는 **오픈드레인 + 풀업 방식**이 하드웨어 아키텍처 관점에서 훨씬 유리함.

<a id="notion-39e1d46c18fc80d98269ecd244970e76"></a>

# 👁️ `volatile` 키워드 한 줄 정의

> **"컴파일러야, 내 코드가 안 바뀐 것 같아도 하드웨어나 외부 요인에 의해 언제든지 값이 변할 수 있으니까, 꼼수(최적화) 부리지 말고 실행할 때마다 무조건 실제 메모리 주소에 가서 값을 새로 읽어와\!"** 라고 강제하는 키워드입니다.

<a id="notion-39e1d46c18fc80279705c394b922b957"></a>

## 🛠️ 1. `volatile`이 없을 때 발생하는 대참사 (예시 코드)

데이터시트를 보면 STM32의 `USART2->SR` 레지스터의 5번 비트는 데이터가 수신되면 하드웨어적으로 자동으로 1이 됩니다.

```c
// ❌ volatile이 없는 잘못된 코드 예시
unsigned int *USART2_SR = (unsigned int *)0x40004400; // 가상의 레지스터 주소

void Wait_For_Data(void){
    // 컴파일러의 꼼수(최적화) 발동:
    // "어? 루프 안에서 USART2_SR 값을 바꾸는 코드가 없네? 매번 무겁게 주소창 찾아가지 말고,
    // 그냥 처음에 한 번 읽어온 값(0)을 CPU 임시 상자(레지스터)에 넣어두고 우려먹어야지!"
    while ((*USART2_SR & (1U << 5U)) == 0U)
    {
        // 하드웨어가 밖에서 아무리 레지스터 값을 1로 바꿔도,
        // CPU는 임시 상자(0)만 보고 있으므로 이 루프를 영원히 빠져나오지 못함 (무한 루프 버그)
    }
}
```

<a id="notion-39e1d46c18fc803d9c54c1ccaaae2bf8"></a>

## 🟢 2. `volatile`을 붙인 정석 해결 코드

```c
// 🟢 MISRA C 및 실무 표준 코드
// volatile을 붙여서 컴파일러의 최적화를 완전히 차단합니다.
volatile unsigned int *USART2_SR = (volatile unsigned int *)0x40004400;[cite: 1]

void Wait_For_Data(void){
    // 이제 CPU는 루프를 돌 때마다 꼼수를 부리지 못하고,
    // 무조건 0x40004400 번지 하드웨어 방으로 직접 찾아가서 값을 새로 읽어옵니다.
    while ((*USART2_SR & (1U << 5U)) == 0U)
    {
        // 외부에서 데이터가 들어와 하드웨어가 값을 1로 바꾸는 순간,
        // 실시간으로 감지하여 루프를 안전하게 탈출합니다!
    }
}
```

<a id="notion-39e1d46c18fc809b8761f1580d96eafc"></a>

## 📌 3. 임베디드 실무에서 `volatile`을 무조건 써야 하는 3대 상황

1. **하드웨어 주변장치 레지스터를 제어할 때:** (예: GPIO, UART, 타이머 등 매뉴얼에 나오는 모든 주소)
2. **인터럽트 서비스 루틴(ISR)과 메인 루프가 공유하는 전역 변수:** 인터럽트는 언제 튈지 모르기 때문에 메인 루프가 변수의 변화를 실시간으로 알아채야 합니다.
3. **멀티태스킹(RTOS) 환경에서 여러 태스크가 공유하는 전역 변수**

임베디드 면접 단골 질문이기도 하니, "컴파일러 최적화 방지 ➡️ 실시간 메모리 직접 접근"이라는 핵심 메커니즘으로 기억해 두시면 완벽합니다\!

<a id="notion-39e1d46c18fc80969c1dc8c4f1656c6d"></a>

# 🔒 `const` 키워드 한 줄 정의

> "컴파일러야, 이 변수에 저장된 값은 절대로 중간에 바뀌면 안 되는 데이터(Read-Only)니까, 누가 실수로 값을 바꾸려고 하면 빌드할 때 에러를 터트려줘\! 그리고 이 데이터는 RAM이 아니라 롬(Flash Memory)에 박아서 보관해줘."

<a id="notion-39e1d46c18fc8004a2b9c82d20c2997a"></a>

## 🛠️ 1. 임베디드에서 `const`가 왜 그렇게 중요할까? (메모리 관점)

일반 PC 개발에서는 `const`를 단순히 "실수 방지용"으로 쓰지만, 우리 STM32 보드 같은 임베디드 시스템에서는 **저장되는 메모리 영토**가 완전히 바뀝니다.

- <strong>일반 변수 (</strong><strong>`uint32_t data = 10;`</strong><strong>):</strong> 언제든 값을 바꿔야 하므로 용량이 작고 비싼 SRAM(System SRAM)에 위치합니다.
- <strong>const 변수 (</strong><strong>`const uint32_t data = 10;`</strong><strong>):</strong> 읽기만 하면 되므로, 프로그램 코드와 함께 용량이 크고 전력이 들지 않는 **내장 플래시 메모리(Flash Memory, ROM)** 영역에 영구 박제됩니다.
- **결론:** 폰트 데이터, 센서 보정 테이블 값, 불변의 환경 설정값 등을 `const`로 선언하면 **귀한 RAM(SRAM) 용량을 아끼고 시스템 안정성을 극대화**할 수 있습니다.

<a id="notion-39e1d46c18fc80db8f9cfaad4439fed3"></a>

## 💻 2. 실무 예시 코드 (정석과 응용)

<a id="notion-39e1d46c18fc80c78e3ef7a53ba67203"></a>

### ① 기본적인 데이터 박제 (RAM 절약)

```c
// 🟢 플래시 메모리(ROM) 영역에 저장되어 RAM을 한 바이트도 먹지 않는 효자 코드
const uint8_t Sensor_Calibration_Table[4] = {0x12U, 0x34U, 0x56U, 0x78U};

void Process_Data(void){
    // Sensor_Calibration_Table[0] = 0x00U;
    // ❌ 만약 위 주석처럼 값을 바꾸려고 하면 컴파일러가 빌드 시점에 "Read-Only입니다" 하고 에러를 터트려줍니다.
}
```

<a id="notion-39e1d46c18fc80499176f71f00cc416e"></a>

### ② 포인터와 조합할 때의 2가지 변종 (★면접/실무 단골)

아래의 **"오른쪽 법칙"** 딱 하나만 기억하세요.

<a id="notion-39e1d46c18fc80268b74d8afbd8c9705"></a>

### 1\. `const` **데이터타입** (예: `const uint32_t *p`)

> 💡 `const` 오른쪽에 **데이터타입**이 있으면 ➡️ **알맹이**가 고정\!

- **비유:** "상자 안의 내용물은 절대 못 바꿔\!"
- **상태:**

  - `*p = 5U;` ❌ **안됨** (알맹이 수정 불가)
  - `p = &other_address;` 🟢 **됨** (가리키는 주소 변경 가능)

<a id="notion-39e1d46c18fc803f8314c27fcadd3002"></a>

### 2\. `const` **변수명** (예: `uint32_t * const p`)

> 💡 `const` 오른쪽에 \*\*변수명(포인터 자체)\*\*이 있으면 ➡️ \*\*주소(손가락)\*\*가 고정\!

- **비유:** "가리키고 있는 방향(주소)은 평생 절대 못 바꿔\!"
- **상태:**

  - `*p = 5U;` 🟢 **됨** (가리키고 있는 방 안의 알맹이 수정 가능)
  - `p = &other_address;` ❌ **안됨** (가리키는 주소 변경 불가)

<a id="notion-39e1d46c18fc80e7a6acdb3a038033aa"></a>

### 3\. 둘 다 고정 (예: `const uint32_t * const p`)

- **상태:** `*p = 5U;` ❌ **안됨** / `p = &other_address;` ❌ **안됨** (방향도 내용물도 철통 보안\!)

<a id="notion-39e1d46c18fc80319d61f436d89cf385"></a>

### 💡 딱 3초 요약

> `const` 바로 **오른쪽에 있는 대상**이 잠깁니다.
>
> - `const uint32_t` ➡️ \*\*타입(값)\*\*이 잠김
> - `const p` ➡️ \*\*포인터(주소)\*\*가 잠김
>
> ```c
> /* =============================================================================
>  * [ 단일 비트 제어 매크로 ]
>  * 특정 1개 비트만 콕 집어서 상태를 변경할 때 사용합니다.
>  * ============================================================================= */
>
> /* dest 변수의 pos 번째 비트만 1로 만듭니다. (Set) */
> #define Macro_Set_Bit(dest, pos) ((dest) |= ((unsigned)0x1 << (pos)))
>
> /* dest 변수의 pos 번째 비트만 0으로 만듭니다. (Clear) */
> #define Macro_Clear_Bit(dest, pos) ((dest) &= ~((unsigned)0x1 << (pos)))
>
> /* dest 변수의 pos 번째 비트 상태를 뒤집습니다. (0은 1로, 1은 0으로 반전 / Toggle) */
> #define Macro_Invert_Bit(dest, pos) ((dest) ^= ((unsigned)0x1 << (pos)))
>
> /* =============================================================================
>  * [ 다중 비트 영역(Area) 제어 매크로 ]
>  * 여러 개의 비트(예: 3비트, 4비트 등) 영역을 동시에 제어할 때 사용합니다.
>  * ============================================================================= */
>
> /* dest 변수의 pos 위치부터 시작하는 bits 크기의 영역을 모두 0으로 밉니다. */
> #define Macro_Clear_Area(dest, bits, pos) ((dest) &= ~(((unsigned)bits) << (pos)))
>
> /* dest 변수의 pos 위치부터 시작하는 bits 크기의 영역을 모두 1로 만듭니다. */
> #define Macro_Set_Area(dest, bits, pos) ((dest) |= (((unsigned)bits) << (pos)))
>
> /* dest 변수의 pos 위치부터 시작하는 bits 크기 영역의 상태를 전부 반전시킵니다. */
> #define Macro_Invert_Area(dest, bits, pos) ((dest) ^= (((unsigned)bits) << (pos)))
>
> /* =============================================================================
>  * [ 데이터 쓰기 및 추출 매크로 ]
>  * 특정 영역에 정확히 원하는 숫자(값)를 쓰거나 읽어올 때 사용하는 고난도 매크로입니다.
>  * ============================================================================= */
>
> /*
>  * [영역 덮어쓰기]
>  * dest의 pos 위치에 있는 bits 크기의 방을 먼저 깨끗이 비운(Clear) 다음,
>  * 그 자리에 정확히 원하는 data 값을 대입(Write)합니다.
>  */
> #define Macro_Write_Block(dest, bits, data, pos) ((dest) = (((unsigned)dest) & ~(((unsigned)bits) << (pos))) | (((unsigned)data) << (pos)))
>
> /*
>  * [영역 읽어오기]
>  * dest의 pos 위치에 있는 데이터를 오른쪽 끝으로 당겨온 뒤, bits 크기만큼 필터링(Mask)하여
>  * 순수한 데이터만 쏙 뽑아냅니다. (예: GPIO 설정 상태 읽기)
>  */
> #define Macro_Extract_Area(dest, bits, pos) ((((unsigned)dest) >> (pos)) & (bits))
>
> /* =============================================================================
>  * [ 비트 상태 검사 매크로 ]
>  * 조건문(if, while 등)에서 특정 비트의 현재 상태를 체크할 때 참(1)/거짓(0)을 반환합니다.
>  * ============================================================================= */
>
> /* dest 변수의 pos 번째 비트가 현재 1(Set)인지 확인합니다. (맞으면 1, 틀리면 0 반환) */
> #define Macro_Check_Bit_Set(dest, pos) ((((unsigned)dest) >> (pos)) & 0x1)
>
> /* dest 변수의 pos 번째 비트가 현재 0(Clear)인지 확인합니다. (맞으면 1, 틀리면 0 반환) */
> #define Macro_Check_Bit_Clear(dest, pos) (!((((unsigned)dest) >> (pos)) & 0x1))
> ```

<a id="notion-39e1d46c18fc80ebadc5e292493d59af"></a>

## 🛡️ 3. MISRA C 규칙과의 연결고리 (Rule 8.13 등)

MISRA C에서는 "함수의 매개변수로 포인터를 넘길 때, 함수 내부에서 그 알맹이 값을 바꿀 일이 없다면 무조건 `const`를 붙여라"라고 강제합니다.

```c
// ❌ MISRA C 위반: 함수 내부에서 데이터를 바꾸지 않음에도 const가 없음
void Send_Data(uint8_t *p_buffer, uint16_t size);

// 🟢 MISRA C 준수: 읽기 전용 버퍼임을 명확히 하여 하드웨어 오염을 방지함
void Send_Data(const uint8_t *p_buffer, uint16_t size);
```

<a id="notion-39e1d46c18fc8011861bf877e6444cef"></a>

## 💡 `volatile`과 `const`가 동시에 붙을 수도 있나요?

**네\! 임베디드에서는 매우 자주 쓰입니다.** 대표적인 예가 "입력전용 GPIO 레지스터"나 "읽기전용 하드웨어 ID 레지스터"입니다.

```c
// 🟢 읽기 전용 하드웨어 레지스터의 정석 (Figure 18의 Input Data Register 같은 경우)[cite: 1]
#define GPIOA_IDR  (*(volatile const uint32_t *)0x40020010)[cite: 1]
```

- **volatile:** 내가 안 건드려도 외부에서 버튼을 누르면 값이 실시간으로 변하니까 꼼수 부리지 말고 매번 메모리 주소에 직접 가서 읽어라
- **const:** 하지만 내 소스코드 내부에서 대입 연산자(`=`)로 이 레지스터 값을 강제로 바꾸는 코드(버그)는 컴파일러 네가 빌드할 때 절대 못 하게 막아라\!

<a id="notion-39e1d46c18fc802785f3dc245c08d110"></a>

# 📦 CMSIS 표준의 레지스터 구조체 매핑 기법

우리가 앞서 제어했던 GPIOA의 레지스터들을 CMSIS 규격에 맞춰 구조체로 묶는 실제 헤더 파일 내부 구조입니다.

<a id="notion-39e1d46c18fc80d3a855dfbb9104d039"></a>

## 📑 1. 헤더 파일 (`stm32f4xx_gpio.h` 예시)

```c
#include <stdint.h> // uint32_t 같은 표준 크기 타입 사용을 위해 선언

// [CMSIS 매크로 규정] 읽기/쓰기 권한을 명확히 정의함
#define     __I     volatile const       /*!< Read-Only 권한 */
#define     __O     volatile             /*!< Write-Only 권한 */
#define     __IO    volatile             /*!< Read/Write 권한 */

/*
 * 🟢 CMSIS 규정 1: 주변 장치 레지스터들을 구조체(typedef struct)로 정의한다.
 * 메모리 맵 상에서 레지스터들이 '연속적으로 배치'되어 있는 특징을 100% 활용합니다.
 */
typedef struct
{
  __IO uint32_t MODER;    /*!< GPIO port mode register,        Address offset: 0x00 */
  __IO uint32_t OTYPER;   /*!< GPIO port output type register, Address offset: 0x04 */
  __IO uint32_t OSPEEDR;  /*!< GPIO port output speed register,Address offset: 0x08 */
  __IO uint32_t PUPDR;    /*!< GPIO port pull-up/pull-down,    Address offset: 0x0C */
  __I  uint32_t IDR;      /*!< GPIO port input data register,  Address offset: 0x10 */
  __IO uint32_t ODR;      /*!< GPIO port output data register, Address offset: 0x14 */
  __IO uint32_t BSRR;     /*!< GPIO port bit set/reset,        Address offset: 0x18 */
  __IO uint32_t LCKR;     /*!< GPIO port configuration lock,   Address offset: 0x1C */
  __IO uint32_t AFR[2];   /*!< GPIO alternate function regs,   Address offset: 0x20-0x24 */
} GPIO_TypeDef;           // <--- 이제 이 구조체 크기는 정확히 40바이트(4바이트 * 10개)가 됩니다.


/*
 * 🟢 CMSIS 규정 2: 실제 하드웨어 주소(Base Address)를 정의한다.
 */
#define PERIPH_BASE           (0x40000000UL) /*!< 주변장치 시작 주소 */
#define AHB1PERIPH_BASE       (PERIPH_BASE + 0x00020000UL) /*!< AHB1 버스 시작 주소 */
#define GPIOA_BASE            (AHB1PERIPH_BASE + 0x0000UL) /*!< GPIOA 시작 주소 = 0x40020000 */


/*
 * 🟢 CMSIS 규정 3: 하드웨어 시작 주소를 앞서 만든 구조체 포인터로 강제 캐스팅한다.
 * (우리가 배운 volatile, 포인터, 캐스팅 개념이 모두 쓰인 정점입니다!)
 */
#define GPIOA               ((GPIO_TypeDef *) GPIOA_BASE)
```

<a id="notion-39e1d46c18fc80319371c8447ba16e42"></a>

## 💻 2. 메인 소스코드에서의 사용 방식 (`main.c`)

위와 같이 헤더 파일이 CMSIS 규격대로 정의되어 있다면, 우리는 복잡한 주소나 비트 연산 없이 C언어의 구조체 포인터 멤버 연산자(`->`)를 사용해 레지스터를 아주 우아하게 제어할 수 있게 됩니다.

```c
void Main(void){
    // 1. GPA[5]를 출력 모드로 설정 (MODER 레지스터 제어)
    // GPIOA(0x40020000 번지)에 있는 MODER 멤버(Offset +0x00)를 직접 수정합니다.
    GPIOA->MODER &= ~(0x3U << 10U);
    GPIOA->MODER |= (0x1U << 10U);

    // 2. GPA[5]를 Push-Pull 모드로 설정 (OTYPER 레지스터 제어, Offset +0x04)
    GPIOA->OTYPER &= ~(0x1U << 5U);

    // 3. GPA[5] LED를 ON 시키도록 설정 (ODR 레지스터 제어, Offset +0x14)
    GPIOA->ODR |= (0x1U << 5U);
}
```

<a id="notion-39e1d46c18fc80b98395e972ebf8d876"></a>

## 💡 이 코드의 기가 막힌 장점

1. **레지스터 주소 자동 계산:** 컴파일러가 구조체 멤버의 순서를 보고 `MODER`는 주소값 그대로(Offset +0), `OTYPER`는 +4바이트 뒤의 주소, `ODR`은 +20바이트(0x14) 뒤의 주소인 것을 알아서 계산해 줍니다.
2. **실수 방지:** 입력 전용 레지스터인 `IDR`은 헤더 파일에 `__I` (volatile const)로 막혀 있기 때문에, 개발자가 실수로 `GPIOA->IDR = 0x01;` 이라고 코딩하면 컴파일러가 빌드 과정에서 즉시 버그로 잡아내 줍니다.
