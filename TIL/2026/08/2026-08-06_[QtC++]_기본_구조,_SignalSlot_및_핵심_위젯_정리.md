# \[Qt/C++\] 기본 구조, Signal/Slot 및 핵심 위젯 정리

> 날짜: 2026-08-06
> 원본 노션: [링크](https://app.notion.com/p/Qt-C-Signal-Slot-3b31d46c18fc80b3b886f06dc05d3994)

<!-- notion-page-id: 3b31d46c18fc80b3b886f06dc05d3994 -->
<!-- notion-title: "[Qt/C++] 기본 구조, Signal/Slot 및 핵심 위젯 정리" -->

---

<a id="notion-3b41d46c18fc80298969e838beb22e28"></a>

## 1\. Qt 프로그램 기본 실행 흐름 (`main.cpp`)

- <strong>`QApplication a(argc, argv)`</strong>: GUI 애플리케이션의 제어 흐름과 기본 설정을 총괄 관리 (프로그램 당 1개 필수)
- <strong>`MainWindow w`</strong>: 메인 화면 객체 생성
- <strong>`w.show()`</strong>: 생성된 메인 윈도우를 화면에 표시
- <strong>`return a.exec()`</strong>: 메인 이벤트 루프(Event Loop) 실행 ➔ `exit()`가 호출될 때까지 대기 및 이벤트 처리

<a id="notion-3b41d46c18fc80769da4e25315518b41"></a>

## 2\. 메인 윈도우 구조 (`mainwindow.h` / `.cpp`)

<a id="notion-3b41d46c18fc80cbbddcc8df466ccb13"></a>

### 📄 `mainwindow.h` (설계도)

```cpp
#ifndef MAINWINDOW_H   // 헤더 중복 포함 방지 시작
#define MAINWINDOW_H

#include <QMainWindow> // Qt 기본 창 클래스 로드

namespace Ui {         // Qt Designer(.ui)가 생성한 클래스 네임스페이스
class MainWindow;
}

class MainWindow : public QMainWindow // QMainWindow 상속
{
    Q_OBJECT           // ★ 필수: Signal & Slot (이벤트 통신) 활성화 매크로

public:
    explicit MainWindow(QWidget *parent = nullptr); // 생성자 (explicit: 암시적 형변환 방지)
    ~MainWindow() override;                         // 소멸자

private:
    Ui::MainWindow *ui; // ★ 중요: GUI 위젯 접근 포인터 (안드로이드 ViewBinding 역할)
};
#endif // MAINWINDOW_H
```

<a id="notion-3b41d46c18fc807b8967c17c4d0a3cb6"></a>

### 📄 `mainwindow.cpp` (구현부)

```cpp
#include "mainwindow.h"
#include "ui_mainwindow.h" // Designer XML 변환 코드 포함

// 생성자 초기화 리스트 (부모 생성자 호출 + ui 동적 할당)
MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    // ★ 중요: .ui 파일의 위젯들을 화면에 실제 생성 및 배치
    // (안드로이드 setContentView 역할)
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui; // 메모리 해제
}
```

> 💡 **핵심 포인트 요약**
>
> - <strong>`Q_OBJECT`</strong>: Qt의 핵심 기능(Signal/Slot 등)을 C++ 컴파일러(MOC)가 해석하게 만드는 필수 매크로
> - <strong>`Ui::MainWindow *ui`</strong>: 화면 위젯 접근용 포인터 (`ui->btnHello`, `ui->lblMessage`)
> - **`MainWindow::`** <strong>(범위 지정 연산자)</strong>: 외부 접근이 아니라 "이 코드가 `MainWindow` 클래스 내부 구현부"임을 선언하는 문법 (따라서 `private` 멤버 접근 가능)

<a id="notion-3b41d46c18fc8063ba04d830c87bb3d9"></a>

## 3\. 이벤트 처리 (Signal &amp; Slot)

- <strong>시그널 (Signal)</strong>: 위젯에서 특정 이벤트(클릭, 값 변경 등)가 발생했을 때 외부에 알리는 신호
- <strong>슬롯 (Slot)</strong>: 시그널을 받아 실제 로직을 수행하는 반응 함수

<a id="notion-3b41d46c18fc80d98d2aceea99be2619"></a>

### 📌 시그널-슬롯 연결 방식 3가지 비교

|  |  |  |
| --- | --- | --- |
| **구분** | **작성 예시** | **장단점 및 평가** |
| **방식 1**<br><br>(Auto-Connect) | `void on_btnHello_clicked();` | Designer의 \[Go to slot\] 기능. 위젯 이름 변경 시 연결 끊김 ⚠️ |
| **방식 2**<br><br>(Legacy Macro) | `connect(ui->btn, SIGNAL(clicked()), ui->lbl, SLOT(clear()));` | Qt4 구식 방식. 문자열 기반이라 오타가 나도 컴파일 에러 안 남 ❌ |
| **방식 3**<br><br>(Function Pointer) | `connect(ui->btn, &QPushButton::clicked, ui->lbl, &QLabel::clear);` | **Qt5/6 권장 표준.** 컴파일 시점에 타입/오타 검수, 리팩토링 안전 ⭐⭐⭐ |

<a id="notion-3b41d46c18fc80458b25d454fd306180"></a>

### 🚀 현대적인 C++ 람다(Lambda) 활용법 (가장 추천)

슬롯 함수를 헤더 파일에 일일이 선언하지 않고, 인자 전달까지 깔끔하게 처리하는 스타일입니다.

```cpp
// 버튼 클릭 시 "Hello" 텍스트 설정
connect(ui->btnHello, &QPushButton::clicked, this, [this]() {
    ui->lblMessage->setText("Hello");
});
```

<a id="notion-3b41d46c18fc8014a6f0f9db7f352125"></a>

## 4\. Basic &amp; Display Widget 주요 속성

<a id="notion-3b41d46c18fc80e2b73ff601c9ceab41"></a>

### ⚙️ 공통 기본 속성 (Common Properties)

- <strong>`enabled`</strong>: 위젯 활성화/비활성화 여부 (`true`/`false`)
- <strong>`geometry`</strong>: 위젯의 위치 및 크기 (`x`, `y`, `width`, `height`)
- <strong>`minimumSize / maximumSize`</strong>: 위젯의 최소/최대 크기 제한
- <strong>`font`</strong>: 글꼴, 크기, 굵기 등 설정
- <strong>`styleSheet`</strong>: CSS 기반 스타일링 (예: `background-color: rgb(0, 0, 0); color: white;`)

<a id="notion-3b41d46c18fc80c9af53e39d3f40fcca"></a>

### 🏷️ QLabel 주요 속성

- <strong>`text`</strong>: 표시할 문자열 (코드에서 전달 시 `QString` 타입 사용)
- <strong>`alignment`</strong>: 정렬 방식 (가로/세로 중앙 정렬 등)
- <strong>`wordWrap`</strong>: 텍스트 자동 줄바꿈 여부
- <strong>`pixmap`</strong>: 라벨에 이미지 표시
- <strong>`openExternalLink`</strong>: 텍스트 내 하이퍼링크 클릭 시 브라우저 열기 여부
- <strong>`frameShape / frameShadow`</strong>: 테두리 모양 및 그림자 효과

<a id="notion-3b41d46c18fc806f89c9f5cfb9c3f74c"></a>

## 5\. Qt 리소스 파일 (`.qrc`) 관리

아이콘, 이미지 등 정적 자원을 실행 파일 내부에 포함시키는 방법입니다.

<a id="notion-3b41d46c18fc801483d2dff32deee810"></a>

### 🛠️ 리소스 파일 생성 순서

1. **\[File\] ➔ \[New File or Project...\] ➔ \[Qt\] ➔ \[Qt Resource File\]** 선택
2. 파일 이름 입력 (예: `MyResources`) ➔ **\[Next\] ➔ \[Finish\]**
3. 생성된 `.qrc` 우클릭 ➔ **\[Open in Editor\]**
4. **\[Add Prefix\]** 클릭 (예: `/icon`) ➔ **\[Add Files\]** 클릭하여 이미지 등록

<a id="notion-3b41d46c18fc8014a7d1f8e29f6096fa"></a>

### 💡 이미지 적용 Tip (`pixmap` vs `styleSheet`)

- **`pixmap`** <strong>사용 시</strong>: QLabel 전체에 이미지가 그려져 위에 얹힌 **글자(Text)가 숨겨지거나 덮어씌워질 수 있음**
- **`styleSheet`** <strong>사용 시</strong>: 배경 이미지(`background-image`)로 설정되므로 **이미지와 글자를 동시에 표시** 가능

<a id="notion-3b41d46c18fc80fa8717c9e318584933"></a>

## 6\. QPushButton (버튼 위젯)

**주요 속성 (Properties)**

- <strong>`checkable`</strong>: ON/OFF 토글(스위치) 버튼으로 변경
- <strong>`checked`</strong>: 토글 버튼의 현재 ON/OFF 상태
- <strong>`enabled`</strong>: 버튼 활성화/비활성화 (`false` 시 클릭 불가)
- <strong>`autoRepeat`</strong>: 길게 누르고 있을 때 연속 클릭 처리
- <strong>`flat`</strong>: 테두리 없는 평평한 배경
- <strong>`default`</strong>: 엔터(Enter) 키 입력 시 기본 실행될 버튼 설정
- <strong>`shortCut`</strong>: 단축키 설정 (예: `Ctrl+S`)

**주요 시그널 (Signals)**

- <strong>`clicked(bool)`</strong>: 버튼을 클릭했을 때 (가장 기본적)
- <strong>`toggled(bool)`</strong>: `checkable` 버튼의 ON/OFF 상태가 바뀔 때
- <strong>`pressed()`</strong>: 마우스를 누르는 순간
- <strong>`released()`</strong>: 마우스에서 손을 떼는 순간

> **발생 순서:** 누름(`pressed`) ➔ 뗌(`released`) ➔ 완료(`clicked` / `toggled`)
