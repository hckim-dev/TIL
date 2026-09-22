# \[Qt/C++\] 핵심 위젯 &amp; 표준 Dialog

> 날짜: 2026-08-10
> 원본 노션: [링크](https://app.notion.com/p/Qt-C-Dialog-3b71d46c18fc80e6a959c6538275e7db)

<!-- notion-page-id: 3b71d46c18fc80e6a959c6538275e7db -->
<!-- notion-title: "[Qt/C++] 핵심 위젯 & 표준 Dialog" -->

---

<a id="notion-3b71d46c18fc8037a775fff66ff69e58"></a>

# 📑 connect &amp; 람다 활용 핵심 정리

<a id="notion-3b71d46c18fc80638287ec89b47720bb"></a>

## 1\. `QOverload` 사용 시점 및 작성법

<a id="notion-3b71d46c18fc8011a019cbb1cf661405"></a>

### 📌 언제 써야 하나요?

- 시그널(또는 슬롯)의 이름은 같지만 **파라미터 타입/개수가 다른 '오버로딩(Overloading)' 상태일 때** 사용합니다.
- 오버로딩 상태에서 함수 주소(`&Class::signal`)만 적으면 컴파일러가 어떤 버전을 연결해야 할지 몰라 모호성(Ambiguity) 컴파일 에러가 발생합니다.

<a id="notion-3b71d46c18fc806ba548dce6f684d8c3"></a>

### 📌 작성 문법 2가지

```cpp
// 1. QOverload<타입>::of() (기본 방식)
connect(ui->comboBox, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &MainWindow::onIndexChanged);

// 2. qOverload<타입>() (Qt 5.14+ / C++14 이상 권장 ⭐)
connect(ui->comboBox, qOverload<int>(&QComboBox::currentIndexChanged), this, &MainWindow::onIndexChanged);
```

> 💡 **Qt 6 참고**: Qt 6에서는 `QComboBox`, `QSpinBox` 등의 오버로딩 시그널이 대거 단일화되어 `QOverload`를 쓸 일이 이전보다 훨씬 줄어들었습니다.

<a id="notion-3b71d46c18fc8084a85eef4463422daa"></a>

## 2\. `connect` 시그널-슬롯 파라미터 매칭 규칙

<a id="notion-3b71d46c18fc809d8b73c3420650f239"></a>

### 📌 파라미터 타입 명시 여부

시그널과 슬롯의 타입이 호환되고 오버로딩이 없다면, C++ 멤버 함수 포인터 기반으로 컴파일러가 타입을 자동 추론하므로 **파라미터 타입을 별도로 적을 필요가 없습니다.**

```cpp
connect(ui->btnOK, &QPushButton::clicked, this, &MainWindow::onOkClicked);
```

<a id="notion-3b71d46c18fc80e1a544de4eac2ebb60"></a>

### 📌 개수 차이에 따른 동작 규칙

1. **시그널 인자 == 슬롯 인자**: 정상 연결
2. **시그널 인자 &gt; 슬롯 인자**: **허용 ⭕** (슬롯이 필요한 앞쪽 인자만 쓰고 뒷부분은 자동 무시되므로 **람다 없이 바로 연결 가능**)

   - 예: `toggled(bool)` 시그널 ➔ `void onToggled()` 슬롯
3. **시그널 인자 &lt; 슬롯 인자**: **불가 ❌** (컴파일 에러)

<a id="notion-3b71d46c18fc808aa23efbee90b9dac2"></a>

## 3\. 파라미터 형태가 다를 때 (추가 인자 전달) 처리 방식

시그널이 넘겨주지 않는 추가 데이터(예: 버튼 ID 값)를 슬롯에 전달해야 할 때 **무조건 람다만 써야 하는 것은 아닙니다.**

<a id="notion-3b71d46c18fc8034a9d9d4dbee08e24e"></a>

### 📌 처리 대안 3가지

- **방법 A. 람다(Lambda) 활용 (가장 권장 ⭐)**

  - 헤더 파일에 함수를 늘리지 않고 가장 간결하게 작성 가능

  ```cpp
  connect(ui->btn1, &QPushButton::clicked, this, [this]() { processButton(1); });
  ```
- **방법 B. 중계(Helper) 슬롯 함수 작성**

  - 중간 다리역할을 하는 슬롯 함수를 만들고 그 안에서 목적 함수 호출
- <strong>방법 C.</strong> **`std::bind`** <strong>활용</strong>

  - C++ 표준 `std::bind`로 인자를 고정 바인딩하여 연결

  ```cpp
  connect(ui->btn1, &QPushButton::clicked, this, std::bind(&MainWindow::processButton, this, 1));
  ```

<a id="notion-3b71d46c18fc808cb64af895890b532a"></a>

## 4\. 람다의 `[this]` 캡처와 UI 컴포넌트 접근

<a id="notion-3b71d46c18fc803589b7e0ffb33a3604"></a>

### 📌 `[this]`만 캡처해도 UI 컴포넌트 전체를 쓸 수 있는 이유

- `btnOk` 등은 독립된 지역 변수가 아니라 `MainWindow` 클래스의 멤버 변수 포인터인 `ui`가 가리키는 객체(`ui->btnOk`)입니다.
- `[this]`를 캡처하면 `MainWindow` 클래스 전체의 멤버 접근 권한을 얻으므로 내부에서 `ui->btnOk->setText(...)` 형태로 **모든 UI 컴포넌트와 클래스 멤버 변수를 자유롭게 사용**할 수 있습니다.

<a id="notion-3b71d46c18fc80dd92bddc74c5a996d3"></a>

### 📌 작성 주의사항

```cpp
// ⭕ 올바른 방식 (this 캡처로 ui 하위 모든 컴포넌트 접근 가능)
connect(ui->btnOk, &QPushButton::clicked, this, [this]() {
    ui->lblMsg->setText("완료");
});

// ❌ 문법 에러 (캡처 리스트 안에 'ui->btnOk' 같은 멤버 접근식 직접 작성 불가)
connect(ui->btnOk, &QPushButton::clicked, this, [ui->btnOk]() { ... });
```

<a id="notion-3b81d46c18fc80c6be1be399c80f37f9"></a>

# 📑 Input Widgets 정리

<a id="notion-3b81d46c18fc80729a43ec0afb4fa9a9"></a>

## 1\. `QLineEdit` (한 줄 텍스트 입력창)

한 줄 형태의 텍스트를 입력받는 기본 위젯입니다. (비밀번호 입력, 검색창, 숫자 입력창 등에 활용)

<a id="notion-3b81d46c18fc8089a4d1d2807dd4da81"></a>

### 📌 주요 속성 (Properties)

- <strong>`placeholderText`</strong>: 입력 전 옅게 보이는 은색 안내문구 (예: <em>"아이디를 입력하세요"</em>)
- <strong>`echoMode`</strong>: 텍스트 표시 방식 지정

  - `Normal`: 입력한 글자 그대로 표시 (기본값)
  - `Password`: 입력한 글자를 점(.)으로 가림 (비밀번호 입력용)
  - `NoEcho`: 입력한 글자를 전혀 출력하지 않음
- <strong>`readOnly`</strong>: `true` 설정 시 수정 불가능한 읽기 전용 상태로 변경 (계산기 디스플레이용)
- <strong>`clearButtonEnabled`</strong>: `true` 설정 시 우측 끝에 텍스트 일괄 삭제(`X`) 버튼 표시
- <strong>`maxLength`</strong>: 입력할 수 있는 최대 글자 수 제한

<a id="notion-3b81d46c18fc807282daff0f96053766"></a>

### 📌 주요 시그널 (Signals)

- <strong>`textChanged(QString)`</strong>: 코드로 변경되든 사용자가 직접 치든 **텍스트가 바뀔 때마다** 매번 발생
- <strong>`textEdited(QString)`</strong>: 코드로 바뀐 것은 무시하고, **사용자가 키보드로 직접 편집할 때만** 발생
- <strong>`returnPressed()`</strong>: 입력창에서 **Enter(Return) 키를 눌렀을 때** 발생 (검색/로그인 실행용)
- <strong>`editingFinished()`</strong>: **Enter 키를 누르거나, 입력창에서 포커스(Focus)가 벗어났을 때** 발생
- <strong>`inputRejected()`</strong>: `validator`나 `inputMask` 조건에 맞지 않는 잘못된 값이 입력되어 거부되었을 때 발생

<a id="notion-3b81d46c18fc80658815e7d820d71414"></a>

### 📌 주요 메서드 (Methods)

- <strong>`setText(QString)`</strong>: 입력창의 텍스트를 코드로 설정
- <strong>`text()`</strong>: 입력창에 실제로 저장되어 있는 **원본 텍스트** 반환
- <strong>`displayText()`</strong>: 화면에 **눈으로 보이는 텍스트** 반환 (`Password` 모드일 때 가려진 문자열 형태 확인용)

<a id="notion-3b81d46c18fc80ecb80dc701a92b9425"></a>

## 2\. `QComboBox` (드롭다운 선택 상자)

최소한의 공간을 차지하면서 여러 항목 중 하나를 선택할 수 있는 옵션 목록 위젯입니다.

<a id="notion-3b81d46c18fc80e6aa01f368b4c8fc2f"></a>

### 📌 주요 속성 (Properties)

- <strong>`editable`</strong>: `true` 설정 시 선택 목록 외에 **사용자가 직접 텍스트를 입력**할 수 있게 변경
- <strong>`duplicatesEnabled`</strong>: `editable` 상태일 때 이미 목록에 있는 중복 항목을 또 추가할 수 있게 허용할지 여부 (`true`/`false`)

<a id="notion-3b81d46c18fc80709ddbe0ace08e553c"></a>

### 📌 주요 시그널 (Signals)

- <strong>`currentIndexChanged(int / QString)`</strong>: 선택된 항목의 인덱스(순서)나 텍스트가 바뀔 때 발생 (Qt 6부터는 오버로딩 대신 `currentIndexChanged(int)` 위주 사용)
- <strong>`currentTextChanged(QString)`</strong>: 현재 선택된 항목의 **텍스트 문자열이 바뀔 때** 발생 (가장 자주 사용 ⭐)
- <strong>`activated(int / QString)`</strong>: 사용자가 **마우스나 키보드로 항목을 직접 선택/확정했을 때만** 발생 (코드로 바뀐 것은 발생 안 함)
- <strong>`highlighted(int / QString)`</strong>: 사용자가 드롭다운 목록 위에서 마우스 커서를 올리거나 키보드로 **항목을 가리키고만 있을 때** 발생 (아직 선택 확정 X)
- <strong>`editTextChanged(QString)`</strong>: `editable = true`일 때 사용자가 직접 텍스트를 수정하면 발생

<a id="notion-3b81d46c18fc806eacfbc7519a6abf79"></a>

### 💡 실무 한 줄 요약 &amp; 팁

- <strong>`QLineEdit`</strong>**에서 사용자 직접 입력만 반응하고 싶다면**: `textChanged` 대신 **`textEdited`** 사용
- **`QLineEdit`** <strong>비번/결과창</strong>: 비밀번호는 `echoMode = Password`, 결과 창은 `readOnly = true`
- **`QComboBox`** <strong>텍스트 기반 처리</strong>: 선택된 글자를 바로 슬롯으로 받고 싶다면 **`currentTextChanged(QString)`** 시그널이 가장 직관적

<a id="notion-3b81d46c18fc80a4bc59ec73505c5df9"></a>

# 📑 QTimer (타이머) 정리

<a id="notion-3b81d46c18fc80faa8f4e9fe8bb2a341"></a>

## 1\. `QTimer` 개요

- Qt에서 일정 시간 간격으로 특정 로직을 반복 실행하거나, 일정 시간이 지난 후 한 번만 이벤트를 발생시킬 때 사용하는 **상위 레벨 타이머 인터페이스**입니다.
- 비동기 방식(이벤트 루프 기반)으로 동작하여 타이머가 작동하는 동안에도 **UI가 멈추지 않고(Non-blocking)** 계속 응답할 수 있습니다.

<a id="notion-3b81d46c18fc8096bb12d6aaa3904113"></a>

## 2\. 타이머 기본 사용 순서 (3단계)

1. **타이머 객체 생성**: `new QTimer(this)` (부모 객체를 지정하여 메모리 자동 관리)
2. **시그널-슬롯 연결**: `timeout()` 시그널에 시간 도달 시 실행할 함수(슬롯) 연결
3. **타이머 시작**: `start(msec)` 호출 ➔ 지정한 밀리초(ms)마다 `timeout()` 시그널 발생

<a id="notion-3b81d46c18fc8063bb3cd09e5cc76f08"></a>

## 3\. 주요 메서드 (Methods)

|  |  |
| --- | --- |
| **메서드** | **설명** |
| **`start(int msec)`** | 지정한 밀리초(`msec`) 간격으로 타이머를 시작합니다. (인자 없이 `start()` 호출 시 기존 `interval` 값 사용) |
| **`stop()`** | 동작 중인 타이머를 즉시 정지합니다. |
| **`setInterval(int msec)`** | 타이머의 주기(간격)를 밀리초 단위로 설정합니다. (1000ms = 1초) |
| **`setSingleShot(bool)`** | `true` 설정 시 타이머가 주기적으로 반복하지 않고 **딱 1번만 실행**된 후 자동 정지합니다. (기본값: `false`) |
| **`isActive()`** | 현재 타이머가 가동(동작) 중인지 여부를 반환합니다. (`bool`) |
| **`remainingTime()`** | 다음 `timeout()` 시그널이 방출되기까지 \*\*남은 시간(ms)\*\*을 반환합니다. (타이머가 멈춰있으면 `-1`) |

<a id="notion-3b81d46c18fc80f6bc7dcc3ce4916590"></a>

## 4\. 실무 기본 코드 예시

```cpp
#include <QTimer>
#include <QDebug>

// 1. 반복 타이머 (1초마다 실행)
QTimer *timer = new QTimer(this);

// 시그널-슬롯 연결
connect(timer, &QTimer::timeout, this, [this]() {
    qDebug() << "1초마다 실행되는 로직";
});

// 1000ms(1초) 간격으로 타이머 시작
timer->start(1000);

// 필요 시 타이머 정지
// timer->stop();
```

<a id="notion-3b81d46c18fc8065b722fb8230818fd5"></a>

## 💡 실무 팁

1. <strong>1회성 지연 실행 (</strong><strong>`QTimer::singleShot`</strong><strong>)</strong>:

   객체를 생성하고 관리할 필요 없이 "N초 뒤에 딱 한 번만 무언가 실행"하고 싶다면 정적(Static) 함수를 활용하는 것이 훨씬 간결합니다.

   ```cpp
   // 3초(3000ms) 후에 람다 함수 딱 1번 실행
   QTimer::singleShot(3000, this, [this]() {
       ui->lblStatus->setText("3초가 지났습니다!");
   });
   ```
2. **메모리 관리**:

   `new QTimer(this);`처럼 `this` 포인터를 부모(Parent)로 전달하면, 해당 클래스(`MainWindow` 등)가 파괴될 때 타이머도 자동으로 메모리에서 해제됩니다.

<a id="notion-3b81d46c18fc802a94dec7febeac3bf3"></a>

# 📑 표준 대화상자 (Standard Dialog) 정리

<a id="notion-3b81d46c18fc8066893edac0df209e0f"></a>

## 1\. `QDialog` 개요

- 모든 대화상자(Dialog) 클래스의 **최상위 부모 클래스**입니다.
- 메인 윈도우(`QMainWindow`) 위에 **팝업(Pop-up)** 형태로 떠서 사용자에게 정보를 전달하거나 입력을 받습니다.

<a id="notion-3b81d46c18fc800d8111f2081249aa03"></a>

## 2\. 모달 (Modal) vs 모달리스 (Modeless)

대화상자를 화면에 띄우는 방식과 사용자 입력 제어에 따라 구분됩니다.

|  |  |  |
| --- | --- | --- |
| **구분** | **모달 (Modal)** | **모달리스 (Modeless)** |
| **특징** | 대화상자를 **닫기 전까지 다른 창을 조작할 수 없음** | 대화상자가 켜진 상태에서도 **다른 창을 자유롭게 조작 가능** |
| **사용 목적** | 필수 입력, 경고/확인 메시지, 파일 선택 등 | 작업 도구 상자(Toolbox), 찾기/바꾸기 창 등 |
| **실행 메서드** | **`exec()`** | **`show()`** |
| **코드 흐름** | 창이 닫힐 때까지 **코드가 대기(Blocking)** | 창을 띄우고 **즉시 다음 코드가 실행됨(Non-blocking)** |
| **메모리 관리** | 스택(Stack) 생성 가능 (`QDialog dlg; dlg.exec();`) | 힙(Heap) 생성 필요 (`new QDialog(this);`) |

<a id="notion-3b81d46c18fc80edab63d7b1ee0cd658"></a>

## 3\. 대표적인 표준 대화상자 (Standard Dialogs)

Qt에서 기본으로 제공하는 유용한 빌트인 대화상자들입니다.

<a id="notion-3b81d46c18fc80a5b9d6c91cb9c9cf64"></a>

### ① `QFileDialog` (파일 / 디렉토리 선택)

- 파일 열기, 저장, 폴더 선택 시 사용합니다.
- 정적(Static) 메서드로 한 줄 만에 경로를 얻어올 수 있습니다.

```cpp
QString fileName = QFileDialog::getOpenFileName(this, "파일 열기", "", "Text Files (*.txt);;All Files (*)");
```

<a id="notion-3b81d46c18fc807b9ff4f148672e9a5c"></a>

### ② `QMessageBox` *(※ 유저 노치의 QMessageDialog 정식 명칭)*

- 사용자에게 알림, 경고, 질문, 에러 메시지를 표시할 때 사용합니다.
- `QMessageBox::information`, `QMessageBox::warning`, `QMessageBox::question` 등 활용.

```cpp
QMessageBox::StandardButton reply;
reply = QMessageBox::question(this, "확인", "정말 삭제하시겠습니까?", QMessageBox::Yes | QMessageBox::No);
```

<a id="notion-3b81d46c18fc803490bacfdf1d51a5cb"></a>

### ③ `QColorDialog` (색상 선택)

- 팔레트에서 색상을 선택받고 `QColor` 객체를 반환받습니다.

```cpp
QColor color = QColorDialog::getColor(Qt::white, this, "색상 선택");
if (color.isValid()) {
    // 선택한 색상 적용
}
```

<a id="notion-3b81d46c18fc80f9ac9eedbaec57e9a3"></a>

### ④ `QFontDialog` (글꼴 선택)

- 폰트 종류, 크기, 스타일(굵게/기울임)을 선택받고 `QFont` 객체를 반환받습니다.

```cpp
bool ok;
QFont font = QFontDialog::getFont(&ok, this);
if (ok) {
    ui->label->setFont(font);
}
```

<a id="notion-3b81d46c18fc80e7b486c0696221ad08"></a>

### ⑤ `QInputDialog` (단일 값 입력받기)

- 별도의 Dialog를 새로 만들지 않고 간단한 텍스트, 정수, 실수, 리스트 중 하나를 받아올 때 유용합니다.

```cpp
bool ok;
QString text = QInputDialog::getText(this, "이름 입력", "이름을 입력하세요:", QLineEdit::Normal, "", &ok);
```

<a id="notion-3b81d46c18fc80d6927bd8b61f2b8e96"></a>

### ⑥ `QProgressDialog` (진행률 표시)

- 시간이 오래 걸리는 작업(파일 복사, 다운로드 등)의 진행률을 바(Bar) 형태로 보여주며, 취소 버튼을 제공합니다.

<a id="notion-3b81d46c18fc803fb9d9cfa7d469678e"></a>

## 4\. `QDialog` 결과 반환값 (Modal 사용 시)

`exec()` 메서드로 모달 대화상자를 띄우면, 창이 닫힐 때 정수형 결과값(`int`)을 반환합니다.

- **`QDialog::Accepted`** <strong>(</strong><strong>`1`</strong><strong>)</strong>: \[확인/OK\] 버튼을 눌러 닫힘 (`accept()` 호출)
- **`QDialog::Rejected`** <strong>(</strong><strong>`0`</strong><strong>)</strong>: \[취소/Cancel\] 버튼이나 `X` 버튼을 눌러 닫힘 (`reject()` 호출)

```cpp
MyCustomDialog dlg(this);
if (dlg.exec() == QDialog::Accepted) {
    // 확인 버튼을 눌렀을 때만 데이터 처리
}
```

<a id="notion-3b81d46c18fc8097a7e3e3a6ea5692e4"></a>

### 💡 실무 한 줄 팁

- `QFileDialog`, `QMessageBox`, `QInputDialog` 같은 단순 표준 대화상자들은 `new`로 객체를 생성할 필요 없이 정적(Static) 함수(`getOpenFileName`, `warning` 등)를 사용하는 것이 코드가 훨씬 깔끔하고 빠릅니다.

<br>
