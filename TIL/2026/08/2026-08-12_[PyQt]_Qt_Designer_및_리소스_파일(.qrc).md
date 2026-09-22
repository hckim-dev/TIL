# \[PyQt\] Qt Designer 및 리소스 파일(.qrc)

> 날짜: 2026-08-12
> 원본 노션: [링크](https://app.notion.com/p/PyQt-Qt-Designer-qrc-3ba1d46c18fc80629516e01bbcb031b1)

<!-- notion-page-id: 3ba1d46c18fc80629516e01bbcb031b1 -->
<!-- notion-title: "[PyQt] Qt Designer 및 리소스 파일(.qrc)" -->

---

<a id="notion-3ba1d46c18fc80bd90bdcc1f2f4d8405"></a>

# 🚀 PyQt5 실무 표준 구조: Qt Designer (.ui) + OOP 연동

Qt Designer로 작성한 `.ui` 디자인 파일과 파이썬 로직 코드를 분리하여 개발할 때 사용하는 **실무 표준 객체지향(OOP) 구조**입니다.

<a id="notion-3ba1d46c18fc80ddaafcc3f55c2f11d1"></a>

## 1\. 전체 실행 코드

```python
import subprocess
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

# 1. Qt Designer로 생성한 .ui 파일명 지정
GUI_FILE_NAME = "gui"

# 2. .ui 파일을 최신 .py 파일로 자동 컴파일 (pyuic)
subprocess.run(
    [
        sys.executable,
        "-m",
        "PyQt5.uic.pyuic",
        "-x",
        f"{GUI_FILE_NAME}.ui",
        "-o",
        f"{GUI_FILE_NAME}.py",
    ],
    check=True,  # 변환 실패 시 즉시 예외를 발생시켜 이하 코드 실행 중단
)

# 3. 변환된 gui.py에서 UI 클래스(Ui_MainWindow) 임포트
from gui import Ui_MainWindow


# 4. 메인 폼 클래스 정의 (다중 상속)
class Form(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Qt Designer에서 만든 UI 요소들을 현재 클래스(self)에 생성


# 5. 프로그램 엔트리 포인트
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Form()
    w.show()
    sys.exit(app.exec_())
```

<a id="notion-3ba1d46c18fc806e9dd6e2d1105e47d2"></a>

## 2\. 핵심 구성 요소 상세 설명

<a id="notion-3ba1d46c18fc8082b40ac3878d944d4f"></a>

### 1\) 자동 컴파일 (`subprocess.run`)

- Qt Designer에서 `.ui` 파일의 버튼 위치나 레이아웃을 수정하고 저장할 때마다, 파이썬 코드가 실행될 때 <strong>자동으로</strong> **`.py`** <strong>코드로 다시 생성</strong>해 줍니다.
- `check=True`를 붙여서 `.ui` 파일 오타나 에러로 변환에 실패했을 때, 다음 줄의 `from gui import ...`에서 무의미한 모듈 오류가 발생하는 것을 막고 바로 예외를 던집니다.

<a id="notion-3ba1d46c18fc8008af65f017bd4ef011"></a>

### 2\) 다중 상속 (`QMainWindow`, `Ui_MainWindow`)

- <strong>`QMainWindow`</strong>: 창 닫기, 최소화, 위치 이동, 메뉴바 등 **Qt 윈도우 창으로서의 기능**을 담당합니다.
- <strong>`Ui_MainWindow`</strong>: Qt Designer가 자동으로 만들어 준 화면 디자인 요소(버튼, 라벨 등)를 담당합니다.
- 두 클래스를 함께 상속받아 하나의 `Form` 클래스로 만듦으로써, 기능과 디자인을 깔끔하게 통합합니다.

<a id="notion-3ba1d46c18fc80c9abb2e4af63f87c02"></a>

### 3\) `self.setupUi(self)`

- `Ui_MainWindow` 클래스 안에 정의된 핵심 메서드입니다.
- 인자로 넘겨받은 현재 메인 창(`self`)에 Qt Designer에서 작성한 라벨, 버튼 등의 위젯들을 실제 메모리에 올리고 화면에 그리도록 배치합니다.

<a id="notion-3ba1d46c18fc80758a3df219b726a795"></a>

### 4\) `app.exec_()`

- 프로그램이 켜진 상태를 유지하며 마우스 클릭, 키보드 입력 같은 사용자 이벤트를 상시 대기하는 이벤트 루프(Event Loop)를 가동합니다.

<a id="notion-3ba1d46c18fc805a9522c1e46816112e"></a>

## 3\. 시그널/슬롯 기본

```python
class Form(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btnHello.clicked.connect(lambda: self.change_message("Hello"))
        self.btnWorld.clicked.connect(lambda: self.change_message("World"))

    def change_message(self, message):
        self.lblMessage.setText(message)
```

<a id="notion-3ba1d46c18fc80ef8911d0ed2d5dda7c"></a>

## 4\. resource file 사용

qt designer 에서 리소스 탐색기 - 리소스 편집 - 리소스 파일명 (.qrc) - 접두사 추가 - 이미지 파일 추가 - .py 변환 (pyrcc5 xxx.qrc -o xxx\_rc.py)

<br>

```python
from PyQt5.QtGui import QPixmap

pixmap = QPixmap(":/icons/images/setting.png")
        self.lblPicture.setPixmap(pixmap)
        self.lblPicture.resize(pixmap.size())
```

<a id="notion-3ba1d46c18fc80639ef4d73c070b24f9"></a>

## 3\. 시그널 / 슬롯 (Signal &amp; Slot) 기본

<a id="notion-3ba1d46c18fc807483f4e6990357096e"></a>

### 📌 핵심 개념

- **Signal**: 버튼 클릭(`clicked`) 등 위젯에서 발생하는 이벤트
- **Slot**: 이벤트가 발생했을 때 실행시킬 함수(메서드)
- **인자(Parameter) 전달**: 연결할 함수에 인자를 넘겨줘야 할 때는 `lambda` 식을 활용합니다.

```python
from PyQt5.QtWidgets import QMainWindow


class Form(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 1) 인자가 없는 기본 슬롯 연결 (lambda 불필요)
        # self.btnHello.clicked.connect(self.some_function)

        # 2) 인자를 전달해야 하는 슬롯 연결 (lambda 사용)
        self.btnHello.clicked.connect(lambda: self.change_message("Hello"))
        self.btnWorld.clicked.connect(lambda: self.change_message("World"))

    def change_message(self, message):
        self.lblMessage.setText(message)
```

<a id="notion-3ba1d46c18fc80d0abadc1189753cb9c"></a>

## 4\. 리소스 파일 (.qrc) 활용

<a id="notion-3ba1d46c18fc801bb26fd72cde393a85"></a>

### 📌 워크플로우 (4단계)

1. **Qt Designer에서 등록**:

   `Resource Browser` ➔ `Edit Resources` ➔ `.qrc` 파일 생성 ➔ Prefix(접두사, 예: `/icons`) 추가 ➔ 이미지 파일 추가
2. <strong>파이썬 코드로 변환 (</strong><strong>`pyrcc5`</strong><strong>)</strong>:Bash

   터미널(CMD)에서 명령어로 `.qrc` 파일을 `.py` 파일로 컴파일합니다.

   ```text
   pyrcc5 resources.qrc -o resources_rc.py
   ```
3. <strong>⭐ \[중요\] 파이썬 코드에서 변환된 리소스 파일</strong> <strong>`import`</strong>:

   변환된 `resources_rc.py`를 파이썬 코드 상단에서 불러와야 Qt 엔진에 리소스 경로(`:/`)가 등록됩니다.
4. <strong>`QPixmap`</strong>**으로 불러오기**:

   리소스 경로 표기법인 `:/`를 붙여서 이미지를 로드합니다.

<a id="notion-3ba1d46c18fc80a99c36cdcb4ce8c79f"></a>

### 💻 적용 코드

```python
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow

# ⭐ 필수: 변환된 리소스 모듈을 import 해야 ':/' 경로를 인식합니다!
import resources_rc


class Form(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 리소스 파일에서 이미지 로드 (경로 시작은 ':/')
        pixmap = QPixmap(":/icons/images/setting.png")

        if not pixmap.isNull():
            self.lblPicture.setPixmap(pixmap)

            # Label 크기에 맞춰 이미지를 매끄럽게 조절하는 권장 방식
            self.lblPicture.setPixmap(
                pixmap.scaled(
                    self.lblPicture.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            print("이미지를 불러오지 못했습니다. 경로 및 import를 확인하세요.")
```

<a id="notion-3ba1d46c18fc80afa5c3d80113a73aaa"></a>

## 💡 추가 및 보완된 사항 요약

1. **`import resources_rc`** <strong>누락 보완 (필수 ⭐)</strong>

   - `pyrcc5`로 `.py` 파일만 만들고 파이썬 코드에서 `import`를 해주지 않으면 Qt가 `:/icons/...` 경로를 찾지 못해 이미지가 뜨지 않습니다.
2. **`resize()`** <strong>대신</strong> **`scaled()`** <strong>추천</strong>

   - 기존 `self.lblPicture.resize(pixmap.size())`는 **이미지 크기에 맞게 QLabel 위젯의 크기를 변경**합니다. 이미지가 엄청 크면 화면 레이아웃이 깨질 수 있습니다.
   - 대신 `pixmap.scaled()`를 사용하면 **QLabel 위젯 크기는 유지하면서 이미지 크기만 깔끔하게 맞출 수 있습니다.**
