# [Qt/C++] 사용자 Dialog와 Thread

> 날짜: 2026-08-11
> 원본 노션: [링크](https://app.notion.com/p/Qt-C-Dialog-Thread-3b81d46c18fc80fdbf05dbd47392c1b8)

---

# 📑 사용자 정의 대화상자 (Custom QDialog) 정리

## 1. QDialog 개요

- 팝업 창이나 커스텀 대화상자(설정창, 입력 창 등)를 만들 때 상속받아 사용하는 기본(Base) 클래스입니다.
- 일반 QWidget과 달리 결과 코드(Result Code: Accepted / Rejected)를 반환하고 창의 모달(Modal) 상태를 관리하는 전용 메서드를 제공합니다.
## 2. 대화상자 열기 (Public Slots)

대화상자를 출력하는 방식에 따라 3가지 메서드로 나뉩니다.

| 메서드 | 모달 여부 | 동작 방식 (Blocking) | 반환값 | 주요 용도 |
|---|---|---|---|---|
| exec() | 모달 (Modal) | 동기 (Blocking)<br><br>(창이 닫힐 때까지 코드 대기) | int<br><br>(Accepted / Rejected) | 가장 일반적으로 사용하는 대화상자 열기 방식 ⭐ |
| open() | 모달 (Modal) | 비동기 (Non-blocking)<br><br>(코드 대기 없음) | void | 창은 모달로 띄우되, 이벤트 루프를 막지 않고 시그널 기반 처리 시 사용 |
| show() | 모달리스 (Modeless) | 비동기 (Non-blocking)<br><br>(코드 대기 없음) | void | 대화상자가 켜진 상태에서 메인 창도 조작해야 할 때 사용 |

## 3. 대화상자 닫기 & 결과 전달 (Public Slots)

대화상자를 닫으면서 메인 창으로 어떤 결과(Result)를 전달할지 결정합니다.

- accept(): [확인 / OK] 버튼을 눌렀을 때 호출
- reject(): [취소 / Cancel / ESC / X] 버튼을 눌렀을 때 호출
- done(int r): 사용자가 정한 임의의 정수 값(r)으로 결과 코드를 설정하고 창을 닫습니다.
## 4. 주요 속성 및 설정 함수 (Public Functions)

- setModal(bool modal): true 설정 시 WindowModal 모달리티가 적용됩니다.
- setResult(int i): 대화상자를 닫지 않은 채로 결과 코드만 미리 설정해 둡니다.
- setWindowModality(Qt::WindowModality): 모달 차단 범위를 정밀하게 제어합니다.
## 5. 주요 시그널 (Signals)

창이 닫힐 때 호출한 메인 창으로 이벤트 전달 시 활용합니다.

- accepted(): accept() 호출로 창이 정상 승인되어 닫힐 때 방출
- rejected(): reject() 호출로 창이 취소되어 닫힐 때 방출
- finished(int result): 어떤 이유로든 창이 닫힐 때 최종 결과 코드(result)를 담아 방출
## 6. 커스텀 QDialog 기본 구현 코드 예시

### ① 커스텀 다이얼로그 클래스 내부 (MyDialog.cpp)

```c++
// [확인] 버튼 클릭 시
void MyDialog::onBtnOkClicked(){
    // 입력값 검증 로직...
    accept(); // 대화상자를 Accepted(1) 상태로 닫음
}

// [취소] 버튼 클릭 시
void MyDialog::onBtnCancelClicked(){
    reject(); // 대화상자를 Rejected(0) 상태로 닫음
}
```

### ② 메인 윈도우에서 호출 시 (MainWindow.cpp)

```c++
void MainWindow::openCustomDialog(){
    MyDialog dlg(this);

    // exec() 호출로 모달 창 띄움 -> 사용자 응답 대기
    if (dlg.exec() == QDialog::Accepted) {
        // 확인 버튼을 누르고 닫혔을 때 수행할 로직
        QString inputData = dlg.getInputText();
        ui->labelResult->setText(inputData);
    } else {
        // 취소 버튼이나 X를 눌러 닫혔을 때
        qDebug() << "사용자가 취소함";
    }
}
```

## 6. Custom QDialog 생성

1. Qt Creator 좌측 상단 메뉴에서 [File] ➔ [New File or Project...] 클릭합니다.
1. 왼쪽 카테고리에서 [Qt] 선택 ➔ 가운데 목록에서 [Qt Designer Form Class] 선택 후 [Choose...] 버튼을 누릅니다.
1. Designer Template 선택 창에서 Dialog with Buttons Bottom (또는 Dialog without Buttons) 선택 후 [Next]를 클릭합니다.
1. 클래스 이름(Class name)을 입력합니다. (예: MyDialog)
1. 프로젝트 파일(.pro 또는 CMakeLists.txt) 추가 확인 후 **[Finish]**를 누르면 mydialog.h, mydialog.cpp, mydialog.ui 3개 파일이 프로젝트에 추가됩니다.
## 7. Dialog와 데이터 주고받기

### 1. 메인 창 ➔ 다이얼로그로 데이터 보내기 (Setter)

다이얼로그를 띄우기 전에 기존에 저장되어 있던 설정값이나 데이터를 미리 채워두고 싶을 때 사용합니다. 다이얼로그 클래스에 public 함수(Setter)를 만듭니다.

filterdialog.h (다이얼로그 헤더)

```c++
// 외부에서 값을 받아와 위젯에 세팅해주는 함수 추가
void setInitialData(const QString &tag, const QString &level);
```

filterdialog.cpp (다이얼로그 소스)

```c++
void FilterDialog::setInitialData(const QString &tag, const QString &level){
    ui->leTagFilter->setText(tag); // 기존 태그 입력창에 채우기

    int index = ui->comboLogLevel->findText(level);
    if (index != -1) {
        ui->comboLogLevel->setCurrentIndex(index); // 기존 레벨 선택하기
    }
}
```

mainwindow.cpp (메인 창에서 다이얼로그를 띄울 때)

```c++
FilterDialog dlgFilter(this);

// 1. 다이얼로그를 띄우기 전에 데이터 먼저 전달!
dlgFilter.setInitialData("MyAppTag", "Debug");

// 2. 다이얼로그 실행
if (dlgFilter.exec() == QDialog::Accepted) {
    // ...
}
```

### 2. 다이얼로그 ➔ 메인 창으로 데이터 가져오기 (Getter)

사용자가 다이얼로그에서 입력하거나 선택한 값을 메인 창으로 들고 올 때 사용합니다.

filterdialog.h

```c++
// 입력된 값을 리턴해주는 Getter 함수
QString getTagFilter() const;
QString getLogLevel() const;
```

filterdialog.cpp

```c++
QString FilterDialog::getTagFilter() const{
    return ui->leTagFilter->text();
}

QString FilterDialog::getLogLevel() const{
    return ui->comboLogLevel->currentText();
}
```

### 💡 데이터 교환 전체 흐름 요약 (MainWindow 기준)

```c++
void MainWindow::on_btnOpenFilter_clicked(){
    FilterDialog dlgFilter(this);

    // [Step 1] 메인 창 ➔ 다이얼로그로 기존 값 전달 (보내기)
    dlgFilter.setInitialData(currentTag, currentLevel);

    // [Step 2] 다이얼로그 오픈 (모달)
    if (dlgFilter.exec() == QDialog::Accepted) {

        // [Step 3] 다이얼로그 ➔ 메인 창으로 최종 입력값 가져오기 (가져오기)
        currentTag = dlgFilter.getTagFilter();
        currentLevel = dlgFilter.getLogLevel();
    }
}
```

- exec(): GETTER, SETTER
```c++
/* mydialog.h */
signals:
    void send_hobby(QString);

/* mydialog.cpp */
connect(this, SIGNAL(send_hobby(QString)), parent, SLOT(receive_hobby(QString)));

emit send_hobby(str); // signal 호출

/* mainwindow.h */
private slots:
    void receive_name(QString);

/* mainwindow.cpp */
void MainWindow::receive_hobby(QString str)
{
    qDebug() << "receive_hobby" << str;
    ui->lblHobby->setText(str);
}
```

- open(), show(): SIGNAL, SLOT
# 🧵 QThread Worker-Object 표준 패턴 정리 (Notion용)

> 한 줄 요약

## 🔄 스레드 동작 전체 흐름

```plain text
[1. 객체 생성]   Worker는 parent 없이 생성 (new Worker())
      │
[2. 소유권 이동] worker->moveToThread(thread)
      │
[3. 시그널 연결] ├─ thread::started   ──> worker::doWork (일 시작)
                 ├─ worker::sendData  ──> main::handleData (결과 전달)
                 ├─ worker::finished  ──> thread::quit (스레드 루프 종료)
                 ├─ worker::finished  ──> worker::deleteLater (일꾼 메모리 해제)
                 ├─ thread::finished  ──> thread::deleteLater (스레드 메모리 해제)
                 └─ thread::finished  ──> nullptr 초기화 (Dangling Pointer 방지 ⭐)
      │
[4. 스레드 가동] thread->start()
```

## 💻 표준 소스코드 템플릿

### 1. worker.h (일꾼 클래스 선언)

```c++
#ifndef WORKER_H
#define WORKER_H

#include <QObject>
#include <atomic>

class Worker : public QObject {
    Q_OBJECT

public:
    // ⚠️ parent는 기본값 nullptr 필수 (부모가 있으면 moveToThread 불가능)
    explicit Worker(QObject* parent = nullptr);
    bool isRunning() const;

public slots:
    void doWork(); // 백그라운드 반복/연산 작업
    void stop();   // 중단 요청

signals:
    void send_data(int data); // 메인 UI로 보낼 결과값
    void finished();          // 작업 완료 알림

private:
    std::atomic<bool> m_running{false}; // 스레드 안전 플래그
};

#endif // WORKER_H
```

### 2. worker.cpp (일꾼 클래스 구현)

```c++
#include "worker.h"
#include <QThread>

Worker::Worker(QObject* parent)
    : QObject(parent)
{
}

bool Worker::isRunning() const{
    return m_running;
}

void Worker::doWork(){
    m_running = true;
    int count = 0;

    // 백그라운드 작업 루프
    while (m_running) {
        QThread::msleep(100); // 작업 간격

        if (!m_running) break;

        // 주기적으로 결과 전달
        if (++count == 10) {
            count = 0;
            emit send_data(1);
        }
    }

    emit finished(); // 루프 종료 알림
}

void Worker::stop(){
    m_running = false;
}
```

### 3. mainwindow.h (메인 창 선언)

```c++
#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QThread>
#include "worker.h"

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget* parent = nullptr);
    ~MainWindow();

private slots:
    void on_btnStart_clicked();
    void on_btnStop_clicked();
    void handle_data(int data); // 수신 슬롯

private:
    void stopThread();

    Ui::MainWindow* ui;
    QThread* m_thread = nullptr;
    Worker* m_worker = nullptr;
};

#endif // MAINWINDOW_H
```

### 4. mainwindow.cpp (메인 창 구현 및 스레드 제어)

```c++
#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QDebug>

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    stopThread();
    delete ui;
}

void MainWindow::on_btnStart_clicked(){
    // 이미 실행 중이면 중복 실행 방지
    if (m_thread && m_thread->isRunning()) {
        qDebug() << "Already running";
        return;
    }

    // 1. 객체 생성 (Worker는 부모 없이 생성!)
    m_thread = new QThread(this);
    m_worker = new Worker();

    // 2. 소유권 이동
    m_worker->moveToThread(m_thread);

    // 3. 시그널/슬롯 체이닝 연결
    connect(m_thread, &QThread::started, m_worker, &Worker::doWork);
    connect(m_worker, &Worker::send_data, this, &MainWindow::handle_data);

    // 작업 완료 시 종료 및 메모리 해제 수순
    connect(m_worker, &Worker::finished, m_thread, &QThread::quit);
    connect(m_worker, &Worker::finished, m_worker, &QObject::deleteLater);
    connect(m_thread, &QThread::finished, m_thread, &QObject::deleteLater);

    // ⭐ [핵심] 스레드 파괴 시 포인터 변수 초기화 (재시작 시 크래시 방지)
    connect(m_thread, &QThread::finished, this, [this]() {
        m_thread = nullptr;
        m_worker = nullptr;
    });

    // 4. 스레드 시작
    m_thread->start();
}

void MainWindow::on_btnStop_clicked(){
    stopThread();
}

void MainWindow::stopThread(){
    if (m_worker && m_worker->isRunning()) {
        m_worker->stop(); // 루프 탈출 신호
    }

    if (m_thread && m_thread->isRunning()) {
        m_thread->quit(); // 이벤트 루프 종료
        m_thread->wait(); // 완전 정지까지 블로킹 대기
    }
}

void MainWindow::handle_data(int data){
    qDebug() << "Data received:" << data;
    // UI 업데이트 로직 처리
}
```

## 📌 필수 암기 4대 규칙 (Cheatsheet)

1. Worker 생성 시 Parent 금지
1. 소유권 이전 필수
1. deleteLater로 메모리 자진 해제
1. nullptr 초기화 람다 등록


