# [PyQt] Dialog, Signal, Thread, Event

> 날짜: 2026-08-13
> 원본 노션: [링크](https://app.notion.com/p/PyQt-Dialog-Signal-Thread-Event-3bb1d46c18fc807da7ceda80211fef9d)

---

## 1. QFileDialog (파일 선택 / 저장 대화상자)

getOpenFileName(열기)과 getSaveFileName(저장)은 내부 파라미터 구조와 동작 방식이 동일합니다.

### 📌 파라미터 의미

- parent: 부모 위젯 (self)
- caption: 대화상자 상단 타이틀 (예: "파일 열기")
- directory: 시작 폴더 경로 (빈 값 "" 지정 시 현재 실행 경로)
- filter: 파일 확장자 필터 (구분자는 ;; 사용, 예: "Text (*.txt);;All (*)")
- initialFilter: (선택) 기본으로 선택해 둘 필터 지정
- options: (선택) 대화상자 옵션 (예: QFileDialog.DontUseNativeDialog)
### 📌 리턴값

- 성공 시: ('선택한 파일의 전체 경로', '선택된 필터 문자열') 튜플
- 취소(Cancel) 시: ('', '선택되어 있던 필터 문자열') 튜플
### 💻 핵심 사용 예시

```python
from PyQt5.QtWidgets import QFileDialog

# 1. 파일 열기
file_path, _ = QFileDialog.getOpenFileName(
    self, "파일 열기", "", "Text Files (*.txt);;All Files (*)"
)
if file_path:
    print(f"선택한 파일: {file_path}")

# 2. 파일 저장
save_path, _ = QFileDialog.getSaveFileName(
    self, "파일 저장", "untitled.txt", "Text Files (*.txt)"
)
if save_path:
    print(f"저장할 경로: {save_path}")
```

## 2. QMessageBox (메시지 / 경고 팝업창)

알림, 경고, 질의 응답 등을 띄울 때 사용합니다.

### 📌 팝업 종류별 파라미터 및 특징

| 메서드 | 아이콘 | 주요 목적 | 파라미터 구조 |
|---|---|---|---|
| about | (앱아이콘) | 단순 정보/버전 안내 | (parent, title, text) |
| information | ℹ️ | 일반 안내 메시지 | (parent, title, text, buttons, defaultButton) |
| warning | ⚠️ | 경고 메시지 | (parent, title, text, buttons, defaultButton) |
| critical | ❌ | 심각한 오류 알림 | (parent, title, text, buttons, defaultButton) |
| question | ❓ | 사용자의 선택(Yes/No) 확인 | (parent, title, text, buttons, defaultButton) |

### 📌 공통 파라미터 의미

- parent: 부모 위젯 (self)
- title: 팝업창 상단 제목
- text: 팝업창 본문 내용
- buttons: (선택) 배치할 버튼 조합 (예: QMessageBox.Yes | QMessageBox.No)
- defaultButton: (선택) 엔터 키 입력 시 기본 실행될 버튼 (예: QMessageBox.No)
### 💻 핵심 사용 예시

```python
from PyQt5.QtWidgets import QMessageBox

# 1. 단순 정보 / 오류 알림 (버튼 생략 시 [확인] 하나만 뜸)
QMessageBox.information(self, "알림", "처리가 완료되었습니다.")
QMessageBox.critical(self, "오류", "파일을 읽을 수 없습니다.")

# 2. 질문 팝업 (사용자가 클릭한 버튼 리턴)
reply = QMessageBox.question(
    self,
    "확인",
    "정말 삭제하시겠습니까?",
    QMessageBox.Yes | QMessageBox.No,
    QMessageBox.No,  # 기본 선택 버튼
)

if reply == QMessageBox.Yes:
    print("삭제 실행")
```

## 3. QDialog & 메인 UI 요소 (QMenuBar, QToolBar)

- 개념: 메인 창(QMainWindow) 외에 데이터 입력, 설정, 알림 등을 위해 띄우는 대화상자 창입니다.
- 주요 메서드:
- QMenuBar (메뉴바):
- QToolBar (툴바):
```python
# QMenuBar & QToolBar 액션 연결 예시
self.actionOpen.triggered.connect(self.open_file)
self.actionExit.triggered.connect(self.close)
```

## 4. 사용자 정의 시그널 (Custom Signal)

- 선언 규칙: pyqtSignal은 PyQt5.QtCore 모듈에 정의되어 있으며, 반드시 클래스 변수(Class Variable) 위치에 선언해야 합니다. (__init__ 함수 내부 선언 불가)
- 타입 지정: 시그널을 통해 전달할 데이터의 타입을 인자로 지정합니다. (int, str, dict, tuple 등)
- emit(*args): 정의된 타입의 데이터를 실어서 시그널을 방출합니다.
- connect(slot_function): 방출된 데이터를 인자로 받는 슬롯 함수를 연결합니다.
### 💻 3~4번 종합 실습 예시 코드

다이얼로그에서 선택한 옵션(튜플)을 사용자 정의 시그널로 메인 창에 전달하고, 메뉴바와 툴바를 활용하는 전체 예시입니다.

```python
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
)


# 1. 자식 다이얼로그 (QDialog + Custom Signal)
class OptionDialog(QDialog):
    # ⭐ 반드시 클래스 변수로 pyqtSignal 선언 (Tuple 전달)
    option_selected = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("옵션 선택")

        layout = QVBoxLayout()
        self.btn_send = QPushButton("설정 적용 (10, 20, 30)", self)
        self.btn_send.clicked.connect(self.apply_option)
        layout.addWidget(self.btn_send)
        self.setLayout(layout)

    def apply_option(self):
        # ⭐ 사용자 정의 시그널 방출 (tuple 전달)
        self.option_selected.emit((10, 20, 30))
        self.accept()  # Dialog 닫기


# 2. 메인 윈도우 (QMenuBar, QToolBar 연동)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 400, 300)

        # UI 요소 및 시그널/슬롯 연결
        self.lbl_status = QLabel("대기 중...", self)
        self.setCentralWidget(self.lbl_status)

        self.init_menu_and_toolbar()

    def init_menu_and_toolbar(self):
        # QMenuBar 생성 및 Action 추가
        menubar = self.menuBar()
        file_menu = menubar.addMenu("파일(&F)")

        open_action = QAction("옵션 창 열기", self)
        open_action.setShortcut("Ctrl+O")  # 단축키 지정
        open_action.triggered.connect(self.open_dialog)  # triggered 연결

        file_menu.addAction(open_action)

        # QToolBar 생성 및 동일 Action 공유
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.addAction(open_action)

    def open_dialog(self):
        dlg = OptionDialog(self)
        # ⭐ 자식 창의 시그널 ➔ 메인 창의 슬롯 연결
        dlg.option_selected.connect(self.receive_options)
        dlg.exec_()  # 모달 다이얼로그 실행

    def receive_options(self, values):
        # 전달받은 tuple(10, 20, 30) 처리
        self.lbl_status.setText(f"수신된 옵션 값: {values}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

```

## 5. Thread

```python
from PyQt5.QtCore import QThread, pyqtSignal


class MyThread(QThread):
    send_command = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        cnt = 0
        self.running = True
        while self.running:
            self.msleep(100)
            cnt += 1
            if cnt == 10:
                cnt = 0
                self.send_command.emit(1)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

    def is_running(self):
        return self.running
```

## 6. 이벤트 처리

```python
class Form(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pos_x = 40
        self.pos_y = 40
        self.move_block(0, 0)

    def keyPressEvent(self, event):
        STEP = 20

        if event.key() == Qt.Key_Left:
            self.move_block(-STEP, 0)
        elif event.key() == Qt.Key_Right:
            self.move_block(STEP, 0)
        elif event.key() == Qt.Key_Up:
            self.move_block(0, -STEP)
        elif event.key() == Qt.Key_Down:
            self.move_block(0, STEP)
        else:
            super().keyPressEvent(event)

    def move_block(self, inc_x, inc_y):
        max_x = self.width() - self.lblBlock.width()
        max_y = self.height() - self.lblBlock.height()

        new_x = self.pos_x + inc_x
        new_y = self.pos_y + inc_y

        self.pos_x = max(0, min(new_x, max_x))
        self.pos_y = max(0, min(new_y, max_y))

        self.lblBlock.move(self.pos_x, self.pos_y)
```



