# [PyQt] Qt Designer 및 리소스 파일(.qrc)

> 날짜: 2026-08-12
> 원본 노션: [링크](https://app.notion.com/p/PyQt-Qt-Designer-qrc-3ba1d46c18fc80629516e01bbcb031b1)

---

# 🚀 PyQt5 실무 표준 구조: Qt Designer (.ui) + OOP 연동

Qt Designer로 작성한 .ui 디자인 파일과 파이썬 로직 코드를 분리하여 개발할 때 사용하는 실무 표준 객체지향(OOP) 구조입니다.

## 1. 전체 실행 코드

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

## 2. 핵심 구성 요소 상세 설명

### 1) 자동 컴파일 (subprocess.run)

- Qt Designer에서 .ui 파일의 버튼 위치나 레이아웃을 수정하고 저장할 때마다, 파이썬 코드가 실행될 때 자동으로 .py 코드로 다시 생성해 줍니다.
- check=True를 붙여서 .ui 파일 오타나 에러로 변환에 실패했을 때, 다음 줄의 from gui import ...에서 무의미한 모듈 오류가 발생하는 것을 막고 바로 예외를 던집니다.
### 2) 다중 상속 (QMainWindow, Ui_MainWindow)

- QMainWindow: 창 닫기, 최소화, 위치 이동, 메뉴바 등 Qt 윈도우 창으로서의 기능을 담당합니다.
- Ui_MainWindow: Qt Designer가 자동으로 만들어 준 화면 디자인 요소(버튼, 라벨 등)를 담당합니다.
- 두 클래스를 함께 상속받아 하나의 Form 클래스로 만듦으로써, 기능과 디자인을 깔끔하게 통합합니다.
### 3) self.setupUi(self)

- Ui_MainWindow 클래스 안에 정의된 핵심 메서드입니다.
- 인자로 넘겨받은 현재 메인 창(self)에 Qt Designer에서 작성한 라벨, 버튼 등의 위젯들을 실제 메모리에 올리고 화면에 그리도록 배치합니다.
### 4) app.exec_()

- 프로그램이 켜진 상태를 유지하며 마우스 클릭, 키보드 입력 같은 사용자 이벤트를 상시 대기하는 이벤트 루프(Event Loop)를 가동합니다.
## 3. 시그널/슬롯 기본

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

## 4. resource file 사용

qt designer 에서 리소스 탐색기 - 리소스 편집 - 리소스 파일명 (.qrc) - 접두사 추가 - 이미지 파일 추가 - .py 변환 (pyrcc5 xxx.qrc -o xxx_rc.py)



```python
from PyQt5.QtGui import QPixmap

pixmap = QPixmap(":/icons/images/setting.png")
        self.lblPicture.setPixmap(pixmap)
        self.lblPicture.resize(pixmap.size())
```

## 3. 시그널 / 슬롯 (Signal & Slot) 기본

### 📌 핵심 개념

- Signal: 버튼 클릭(clicked) 등 위젯에서 발생하는 이벤트
- Slot: 이벤트가 발생했을 때 실행시킬 함수(메서드)
- 인자(Parameter) 전달: 연결할 함수에 인자를 넘겨줘야 할 때는 lambda 식을 활용합니다.
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

## 4. 리소스 파일 (.qrc) 활용

### 📌 워크플로우 (4단계)

1. Qt Designer에서 등록:
1. 파이썬 코드로 변환 (pyrcc5):Bash
1. ⭐ [중요] 파이썬 코드에서 변환된 리소스 파일 import:
1. QPixmap으로 불러오기:
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

## 💡 추가 및 보완된 사항 요약

1. import resources_rc 누락 보완 (필수 ⭐)
1. resize() 대신 scaled() 추천
