# \[Linux\] POSIX 세마포어, 태스크 관리와 커널 메모리

> 날짜: 2026-09-28
> 원본 노션: [링크](https://app.notion.com/p/Linux-POSIX-3e91d46c18fc80408a86d64590faa491)

<!-- notion-page-id: 3e91d46c18fc80408a86d64590faa491 -->
<!-- notion-title: "[Linux] POSIX 세마포어, 태스크 관리와 커널 메모리" -->

---

<a id="notion-3e91d46c18fc808eb869e8c108cd4c4a"></a>

## POSIX 세마포어

POSIX 세마포어는 **카운터 값을 이용해 프로세스 또는 스레드의 실행 순서와 동기화를 제어**한다.

<a id="notion-3e91d46c18fc80599e74e2e4a3cc9d18"></a>

### 이름 있는 세마포어(Named Semaphore)

이름을 가진 세마포어 객체를 이용하며, 주로 **프로세스 간 동기화**에 사용한다.

주요 함수:

```text
sem_open()   → 이름 있는 세마포어 생성/열기
sem_wait()   → 세마포어 획득
sem_post()   → 세마포어 반환
sem_close()  → 세마포어 닫기
sem_unlink() → 이름 있는 세마포어 제거
```

---

<a id="notion-3e91d46c18fc8068a65dcffc0f77c35f"></a>

### 이름 없는 세마포어(Unnamed Semaphore)

`sem_t` 타입의 세마포어 변수를 이용하며, 주로 **스레드 간 동기화**에 사용한다.

주요 함수:

```text
sem_init()    → 세마포어 초기화
sem_wait()    → 세마포어 획득
sem_post()    → 세마포어 반환
sem_destroy() → 세마포어 제거
```

---

<a id="notion-3e91d46c18fc80feaf19f539ce1f673d"></a>

## 이름 없는 POSIX 세마포어 구현

두 개의 스레드가 `g_count`를 증가시키되, <strong>Thread 1이</strong> <strong>`g_count == 100`</strong>**에 도달한 뒤 Thread 2가 동작을 시작하도록 제어**하는 예제이다.

```text
sem_t g_sem;
```

<a id="notion-3e91d46c18fc80abaf0cc2a4900c33f4"></a>

### 세마포어 초기화

```text
sem_init(&g_sem, 0, 0);
```

- 첫 번째 인자: 세마포어 주소
- 두 번째 인자 `0`: 현재 프로세스 내부 스레드 간 공유
- 세 번째 인자 `0`: 세마포어 초기값

초기값이 `0`이므로 Thread 2가 먼저:

```text
sem_wait(&g_sem);
```

를 호출하면 대기 상태가 된다.

---

<a id="notion-3e91d46c18fc8051aa1be06e8ddb80ea"></a>

### `sem_wait()`

```text
sem_wait(&g_sem);
```

세마포어를 획득한다.

```text
세마포어 값 > 0
→ 값을 1 감소
→ 다음 코드 실행

세마포어 값 == 0
→ 대기(block)
```

---

<a id="notion-3e91d46c18fc806c96b6e2c701999ba0"></a>

### `sem_post()`

Thread 1에서:

```text
if (g_count == 100)
{
    sem_post(&g_sem);
}
```

을 수행한다.

```text
g_count == 100
        ↓
sem_post()
        ↓
세마포어 값 0 → 1
        ↓
대기 중이던 Thread 2가 깨어남
        ↓
sem_wait()가 값 1 → 0으로 감소
        ↓
Thread 2 실행 시작
```

즉 세마포어를 이용해 **스레드의 실행 순서를 제어**한다.

---

<a id="notion-3e91d46c18fc8023b261ec183e66e08d"></a>

### Mutex와 Semaphore 역할

이 예제에서는 두 동기화 도구의 목적이 다르다.

```text
Mutex
→ g_count 공유 데이터 보호
→ Race Condition 방지

Semaphore
→ Thread 2가 언제 시작할지 제어
→ 실행 순서 동기화
```

`g_count`를 읽고 수정하는 부분은:

```text
pthread_mutex_lock(&g_mutex);

/* g_count 접근 */

pthread_mutex_unlock(&g_mutex);
```

으로 보호한다.

---

<a id="notion-3e91d46c18fc80f6b3b7d516467518d9"></a>

## Reentrant 함수와 MT-Safe 함수

📝 **시험 중요**

둘 이상의 스레드가 동시에 같은 함수를 호출할 수 있으므로, 멀티스레드 환경에서는 함수의 **MT-Safety 여부**를 확인해야 한다.

---

<a id="notion-3e91d46c18fc801c83f0ed68821fb53d"></a>

### Reentrant 함수

**여러 실행 흐름에서 동시에 호출되어도 서로 영향을 주지 않고 안전하게 실행될 수 있는 함수**이다.

수업 기준 핵심 특징:

- 둘 이상의 스레드가 동시에 호출해도 안전하게 병렬 실행 가능
- 전역 변수, `static` 지역 변수 등 **공유되는 변경 가능한 상태에 의존하지 않도록 구현**
- 함수 내부의 상태가 다른 호출에 의해 변경되지 않음
- 스레드, 재귀 호출 등에서 안전하게 사용할 수 있음

```text
Reentrant
→ 호출마다 독립적으로 동작
→ 공유 상태에 의한 간섭 X
```

⚠️ **핵심**

Reentrant 함수는 **MT-Safe 함수이기도 하다.**

---

<a id="notion-3e91d46c18fc8076995cf67efb229e99"></a>

### MT-Safe 함수

**여러 스레드가 동시에 호출해도 문제가 발생하지 않는 함수**이다.

- 동시에 호출되어도 안전함
- 반드시 병렬로 실행된다는 의미는 아님
- 전역 변수나 `static` 데이터 등 공유 자원을 사용할 수도 있음
- 공유 자원을 Mutex 등으로 보호하면 MT-Safe하게 만들 수 있음
- Mutex로 보호된 구간은 여러 스레드가 동시에 실행하지 못하므로 일부 작업이 **직렬화**될 수 있음

예:

```text
Thread 1 ─┐
          ├─ Mutex → 공유 데이터 접근
Thread 2 ─┘
```

---

<a id="notion-3e91d46c18fc802399eaeace70482021"></a>

## ⭐ Reentrant와 MT-Safe의 관계

시험에서 가장 중요한 부분.

```text
Reentrant → MT-Safe
```

즉,

> **Reentrant 함수는 MT-Safe 함수이다.**

하지만 역은 항상 성립하지 않는다.

```text
MT-Safe ↛ Reentrant
```

왜냐하면 MT-Safe 함수는 공유 데이터를 사용하더라도 **Mutex 같은 동기화 기법으로 보호하여 안전성을 확보**할 수 있기 때문이다.

<a id="notion-3e91d46c18fc80d0acc0f3ba8ff391f2"></a>

### 비교

| 구분 | Reentrant | MT-Safe |
| --- | --- | --- |
| 여러 스레드에서 안전 | O | O |
| 공유 상태 사용 | 사용하지 않도록 설계 | 사용할 수 있음 |
| Mutex 사용 가능성 | 일반적으로 불필요 | 사용할 수 있음 |
| 병렬 실행 | 가능 | 내부 동기화 때문에 직렬화될 수도 있음 |
| 관계 | MT-Safe에 포함 | 반드시 Reentrant는 아님 |

⭐ **시험 암기**

```text
Reentrant ⊂ MT-Safe
```

---

<a id="notion-3e91d46c18fc806abbb6e2ed35eae5e5"></a>

## `strtok()`과 `strtok_r()`

📝 **시험 가능성 높음**

```text
strtok()
```

은 문자열 분리 과정에서 내부 상태를 사용하므로 여러 스레드가 동시에 사용하면 문제가 발생할 수 있다.

반면:

```text
strtok_r()
```

은 상태 정보를 호출자가 별도로 관리하도록 만든 **Reentrant 버전**이다.

```text
strtok()
→ MT-Safety에 주의

strtok_r()
→ Reentrant
→ MT-Safe
```

`_r`은 보통 **reentrant 버전**임을 나타낸다.

---

<a id="notion-3e91d46c18fc8037af39f40df2c21313"></a>

## `errno`와 멀티스레드

📝 **시험 예상 질문**

> 여러 스레드가 동시에 `errno`를 사용하면 서로의 에러값을 덮어쓰지 않는가?

단순한 전역 변수 하나를 모든 스레드가 공유한다면 문제가 발생할 수 있다.

하지만 POSIX 스레드 환경에서 `errno`는 **스레드별로 독립적으로 관리**된다.

```text
Thread 1 → 자기 errno
Thread 2 → 자기 errno
Thread 3 → 자기 errno
```

따라서 한 스레드에서 발생한 오류가 다른 스레드의 `errno` 값을 직접 덮어쓰지 않는다.

---

<a id="notion-3e91d46c18fc80b5bb33cf0fe6f1090f"></a>

## 📝 시험 핵심

```text
Reentrant
→ 여러 실행 흐름에서 동시에 호출해도 서로 간섭 없이 안전
→ 공유되는 변경 가능 상태에 의존하지 않도록 구현
→ MT-Safe

MT-Safe
→ 여러 스레드가 동시에 호출해도 안전
→ 공유 자원을 사용할 수도 있음
→ Mutex 등으로 보호 가능
→ 반드시 Reentrant인 것은 아님

관계
→ Reentrant ⊂ MT-Safe

strtok()
→ 멀티스레드 사용 시 주의

strtok_r()
→ Reentrant 버전

errno
→ POSIX 스레드 환경에서는 스레드별로 관리
```

⭐ **한 줄 암기**

> **Reentrant는 공유 상태에 의존하지 않고 재진입해도 안전한 함수이고, MT-Safe는 여러 스레드가 동시에 호출해도 안전한 함수이다. Reentrant는 MT-Safe이지만 MT-Safe가 반드시 Reentrant인 것은 아니다.**

---

<a id="notion-3e91d46c18fc80df966ec7ede8729a58"></a>

## 실습 — 빵 포장하기

3개의 스레드로 빵 생산과 포장을 구현하는 예제이다.

```text
Thread 1 → 빵 생산
Thread 2 → 빵 생산
Thread 3 → 빵 포장
```

설정:

```text
#define NUM_OF_THREAD 3
#define NUM_OF_BREAD 100
#define NUM_OF_BOX 10
```

```text
총 빵       → 100개
한 박스     → 10개
총 박스     → 10개
```

---

<a id="notion-3e91d46c18fc803d9e94c3139646aebf"></a>

### 빵 생산 스레드

Thread 1과 Thread 2는 동일한:

```text
thread_maker()
```

를 실행한다.

공유 변수:

```text
int bread_count;
pthread_mutex_t bread_mutex;
```

두 생산 스레드가 `bread_count`를 동시에 수정할 수 있으므로 Mutex로 보호한다.

```text
pthread_mutex_lock(&bread_mutex);

bread_count++;

pthread_mutex_unlock(&bread_mutex);
```

---

<a id="notion-3e91d46c18fc80bf8d09f59671b2d73d"></a>

### 생산 시간

```text
usec = 500000 + (random() % 500000);
usleep(usec);
```

따라서 각 빵은:

```text
500000 ~ 999999 us
= 0.5초 이상 1.0초 미만
```

의 임의 시간 후 생산된다.

난수 초기화:

```text
srandom(time(NULL));
```

---

<a id="notion-3e91d46c18fc803f841de7610a836d78"></a>

### 10개 생산될 때마다 포장 신호

```text
if (bread_count % NUM_OF_BOX == 0)
{
    sem_post(&box_sem);
}
```

빵이:

```text
10
20
30
...
100
```

개에 도달할 때마다 세마포어를 하나 증가시킨다.

즉:

```text
빵 10개 완성
    ↓
sem_post()
    ↓
포장 가능한 박스 +1
```

---

<a id="notion-3e91d46c18fc80018829ddbd4487df4a"></a>

### 포장 스레드

Thread 3은:

```text
thread_boxer()
```

를 실행한다.

먼저:

```text
sem_wait(&box_sem);
```

을 수행한다.

초기값이:

```text
sem_init(&box_sem, 0, 0);
```

이므로 처음에는 대기한다.

생산 스레드가 빵 10개를 만들고:

```text
sem_post(&box_sem);
```

를 호출하면 포장 스레드가 깨어난다.

그 후:

```text
sleep(5);
box_count++;
```

로 포장 작업을 수행한다.

---

<a id="notion-3e91d46c18fc80d9b079d364096fc4f3"></a>

### 전체 동작

```text
Thread 1 / Thread 2
        ↓
빵 생산
        ↓
bread_count 증가
        ↓
10개 단위 완성
        ↓
sem_post()
        ↓
────────────────────
        ↓
Thread 3
sem_wait()에서 깨어남
        ↓
박스 포장
        ↓
box_count 증가
```

100개의 빵 생산이 끝나면:

```text
빵 100개
÷
박스당 10개
=
박스 10개
```

가 되고, `box_count == NUM_OF_BOX`가 되면 포장 스레드도 종료한다.

<a id="notion-3e91d46c18fc8008b4efe8fb8e905905"></a>

### 동기화 역할

```text
bread_mutex
→ 두 생산 스레드의 bread_count 접근 보호
→ 상호 배제 / Race Condition 방지

box_sem
→ 빵 10개가 완성될 때마다 포장 스레드에게 알림
→ 생산자와 포장자의 실행 순서 동기화
```

<a id="notion-3e91d46c18fc804ead87cdcd7668c363"></a>

# 리눅스 커널

<a id="notion-3e91d46c18fc80c4a63fe17401a2e485"></a>

## 프로세스 관리

<a id="notion-3e91d46c18fc8034a3c2fe6130ec9e9d"></a>

### 프로세스

프로세스는 **실행 중인 프로그램**이다.

Linux Kernel은 프로세스를 포함한 실행 단위를 **태스크(Task)** 형태로 관리하고 스케줄링한다.

---

<a id="notion-3e91d46c18fc8085bd5ae8c308a97778"></a>

## 프로세스, 스레드, 커널 스레드

⚠️ **중요**

Linux에서 주요 실행 단위는 다음과 같다.

```text
프로세스(Process)
스레드(Thread)
커널 스레드(Kernel Thread)
```

<a id="notion-3e91d46c18fc804997eff79ee58d62cb"></a>

### 프로세스

- 독립적인 가상 주소 공간을 가지는 실행 단위
- User Space와 Kernel Space를 사용

<a id="notion-3e91d46c18fc801289f9ce879cdbe6fc"></a>

### 스레드

- 하나의 프로세스 내부에서 실행되는 실행 흐름
- 같은 프로세스의 다른 스레드와 주소 공간 및 여러 자원을 공유
- 커널에서는 각각 하나의 **Task**로 관리

<a id="notion-3e91d46c18fc8023b0cdea3faa58d296"></a>

### 커널 스레드

- 커널에서 수행되는 실행 단위
- **User Space가 없고 Kernel Space에서만 동작**
- 커널 내부 작업을 수행하기 위해 사용

⚠️ **핵심**

커널은 프로세스, 스레드, 커널 스레드를 모두 **Task 단위로 관리하고 스케줄링**한다.

```text
Process       ─┐
Thread         ├─→ Task → Scheduler
Kernel Thread ─┘
```

---

<a id="notion-3e91d46c18fc80c89c8ced1a3d8c9f22"></a>

## 태스크의 생성

커널에 새로운 Task가 생성되는 대표적인 경우:

1. 커널 초기화 과정에서 초기 태스크들이 생성되는 경우

   - PID 0 : idle/swapper 계열
   - PID 1 : init
   - PID 2 : 일반적으로 `kthreadd`
2. `fork()` 등에 의해 새로운 프로세스가 생성되는 경우
3. 새로운 스레드가 생성되는 경우
4. 커널 스레드가 생성되는 경우

---

<a id="notion-3e91d46c18fc802e91a1cbfbd56f8f89"></a>

## `task_struct`

Linux Kernel은 각각의 Task를:

```text
struct task_struct
```

객체로 표현한다.

`task_struct`에는 Task를 관리하기 위한 다양한 정보가 들어 있다.

대표적으로:

```text
PID / 프로세스 식별 정보
Task 상태
주소 공간 관련 정보
열린 파일 관련 정보
스케줄링 정보
부모/자식 관계
시그널 관련 정보
...
```

커널은 `task_struct` 안의 연결 정보를 이용하여 Task 간 관계를 관리한다.

대표적으로 Task 목록에는 Linux Kernel의 `list_head`를 이용한 **이중 연결 리스트 구조**가 사용된다.

```text
task_struct ↔ task_struct ↔ task_struct ↔ ...
```

---

<a id="notion-3e91d46c18fc802597b4daef6a1f157e"></a>

## 태스크 상태

<a id="notion-3e91d46c18fc800dac6dde4f0ce47e7f"></a>

### `R` — Running / Runnable

```text
TASK_RUNNING
```

- 현재 CPU에서 실행 중
- 또는 CPU를 할당받기 위해 실행 대기 중

즉:

```text
실행 중 + 실행 가능 상태
```

를 포함한다.

---

<a id="notion-3e91d46c18fc8091b1b9f4e1829ab72e"></a>

### `S` — Interruptible Sleep

```text
TASK_INTERRUPTIBLE
```

특정 이벤트가 발생하기를 기다리는 상태이다.

```text
이벤트 발생
또는
시그널 발생
    ↓
TASK_RUNNING
```

으로 전환될 수 있다.

---

<a id="notion-3e91d46c18fc80b9b215da46a481d76f"></a>

### `D` — Uninterruptible Sleep

```text
TASK_UNINTERRUPTIBLE
```

특정 이벤트를 기다리는 상태라는 점은 `TASK_INTERRUPTIBLE`과 비슷하지만, 일반적인 시그널에 의해 쉽게 깨어나지 않는다.

주로 커널 내부에서 특정 I/O 등의 완료를 기다릴 때 볼 수 있다.

---

<a id="notion-3e91d46c18fc80368e0fd4dc0dafaede"></a>

### `T` — Stopped

실행이 정지된 상태.

특정 시그널이나 디버깅 등에 의해 정지될 수 있다.

---

<a id="notion-3e91d46c18fc8054a5a5d0160779044f"></a>

### `Z` — Zombie

프로세스 실행은 종료되었지만 **종료 정보를 부모가 아직 회수하지 않은 상태**이다.

```text
실행 종료
    ↓
Zombie
    ↓
부모의 wait() 계열 처리
    ↓
최종 정리
```

---

<a id="notion-3e91d46c18fc807eb920f89d3cbbda6f"></a>

# 프로세스 복제 시 커널의 동작

프로세스를 생성할 때 커널 내부에서는 공통적인 Task 생성 과정이 사용된다.

수업에서 보는 핵심 흐름:

```text
fork()
   ↓
kernel_clone()
   ↓
copy_process()
   ↓
새 Task 생성
   ↓
새 Task 실행 가능 상태
```

---

<a id="notion-3e91d46c18fc80378591ea9d0239f2ec"></a>

## `kernel_clone()`

Task를 생성하기 위한 커널 내부의 핵심 함수 중 하나이다.

큰 흐름:

```text
Task 복제
    ↓
새로운 Task를 실행 가능한 상태로 만듦
```

내부적으로 `copy_process()`를 사용해 새로운 Task를 준비한다.

---

<a id="notion-3e91d46c18fc8040aa28e8569a9febe5"></a>

## `copy_process()`

새로운 Task를 생성하기 위한 핵심 작업을 수행한다.

대표적인 작업:

```text
task_struct 생성 및 초기화
각종 자원 복제 또는 공유 설정
새로운 PID 할당
부모/자식 관계 설정
스케줄링 관련 정보 준비
...
```

⚠️ **중요**

프로세스와 스레드는 완전히 별개의 커널 객체로 관리되는 것이 아니라 **둘 다 Task를 생성하는 공통 메커니즘을 사용**한다.

---

<a id="notion-3e91d46c18fc80b3a147ef1de79d7eb3"></a>

# 스레드 생성

Linux Kernel은 **스레드도 하나의 Task로 관리**한다.

커널 입장에서 스레드는:

> 다른 Task와 주소 공간 및 여러 자원을 공유하도록 생성된 Task

라고 이해할 수 있다.

User Space에서는:

```text
pthread_create()
```

를 통해 스레드를 생성한다.

결국 커널에서는 새로운 실행 단위가 만들어지고 스케줄링 대상이 된다.

```text
Process
 ├─ Main Thread → Task
 ├─ Thread 1    → Task
 └─ Thread 2    → Task
```

---

<a id="notion-3e91d46c18fc805ea725eee1078260fd"></a>

# 커널 스레드 생성

커널 스레드는 **User Space 없이 Kernel Space에서만 동작하는 Task**이다.

커널 내부에서는 커널 스레드 생성과 관련하여:

```text
kernel_thread()
kthread 관련 인터페이스
kthreadd
```

등이 사용된다.

`kthreadd`는 일반적으로 **PID 2**이며, 커널의 여러 `kthread` 생성 요청을 처리하는 역할을 한다.

---

<a id="notion-3e91d46c18fc80f6a6c9f5878f69f832"></a>

## 커널 스레드 생성 시 커널 동작

프로세스, 스레드, 커널 스레드는 형태는 다르지만 **Task를 만든다는 공통점**이 있다.

수업에서 핵심 흐름은:

```text
Process 생성 ──────┐
Thread 생성 ───────┼─→ kernel_clone()
Kernel Thread 생성 ┘         ↓
                         copy_process()
                              ↓
                           Task 생성
```

차이점은 생성 시 어떤 자원을:

```text
복제할 것인지
공유할 것인지
User Space를 가질 것인지
```

등의 설정이 다르다는 것이다.

---

<a id="notion-3e91d46c18fc80fab302c1aa91489d04"></a>

# 태스크 종료

프로세스, 스레드, 커널 스레드가 종료된다는 것은 커널 관점에서 해당 **Task가 종료되는 것**을 의미한다.

Task 종료의 핵심 커널 함수:

```text
do_exit()
```

---

<a id="notion-3e91d46c18fc8033aedbea4f2c016d41"></a>

## `do_exit()`

Task 종료에 필요한 여러 정리 작업을 수행한다.

큰 흐름:

```text
Task 종료 시작
    ↓
사용하던 각종 자원 정리
    ↓
종료 상태 처리
    ↓
필요한 경우 부모에게 종료 사실 전달(SIGCHILD)
    ↓
다른 Task로 스케줄링
```

일반적인 프로세스의 경우 종료 정보가 아직 부모에게 회수되지 않았다면 **Zombie 상태**로 남을 수 있다.

⚠️ `do_exit()`이 실행됐다고 해서 `task_struct`가 항상 그 즉시 완전히 사라지는 것은 아니다.

---

<a id="notion-3e91d46c18fc80eb918ac97be1c94433"></a>

## `release_task()`

종료된 Task가 더 이상 필요하지 않게 되면:

```text
release_task()
```

등을 통해 남아 있는 Task 관리 정보가 최종적으로 정리된다.

일반적인 부모-자식 프로세스 관계에서는:

```text
Child 종료
    ↓
do_exit()
    ↓
Zombie 상태
    ↓
Parent가 wait()/waitpid()
    ↓
release_task()
    ↓
task_struct 등 최종 정리
```

의 흐름으로 이해하면 된다.

---

<a id="notion-3e91d46c18fc804aa59cfa6ce0052f10"></a>

## ⚠️ 중요 흐름

```text
프로세스 / 스레드 / 커널 스레드
            ↓
          Task
            ↓
       task_struct
            ↓
         Scheduler
```

생성:

```text
kernel_clone()
      ↓
copy_process()
      ↓
새 task_struct / Task 생성
```

종료:

```text
do_exit()
    ↓
Task 실행 종료
    ↓
필요한 종료 정보 유지
    ↓
release_task()
    ↓
최종 정리
```

⭐ **핵심 개념**

> Linux Kernel은 프로세스와 스레드를 완전히 별개의 실행 개념으로 스케줄링하는 것이 아니라, 모두 `task_struct`로 표현되는 **Task 단위로 관리하고 스케줄링한다.**

<a id="notion-3e91d46c18fc808a9ab7d46be7735c4f"></a>

## 📝 프로세스 관리 시험 포인트

<a id="notion-3e91d46c18fc80009de6c84f69bb6f1a"></a>

### 커널 스레드 생성

📝 **시험**

> 커널 스레드를 생성하는 함수는 `kthread_create()`이다.

**→ X**

수업 기준 정답:

```text
kernel_thread()
```

<a id="notion-3e91d46c18fc803eb216e551a850b662"></a>

### `task_struct` 해제

📝 **시험**

> `do_exit()` 함수를 호출하면 `task_struct` 객체가 해제된다.

**→ X**

```text
do_exit()
→ 태스크 종료 처리

release_task()
→ task_struct 등 남은 태스크 정보 최종 해제
```

---

<a id="notion-3e91d46c18fc80e79b14d5e28d5be30d"></a>

# 시스템 콜

<a id="notion-3e91d46c18fc800aa896f08f294dec5a"></a>

## 소프트웨어 인터럽트와 시스템 콜

응용 프로그램은 시스템 콜을 이용하여 **User Mode에서 직접 수행할 수 없는 Kernel 기능을 요청**한다.

수업에서의 전체 흐름:

```text
User Mode
   ↓
read()
   ↓
시스템 콜 Wrapper API
   ↓
시스템 콜 진입
   ↓
Kernel Mode 전환
   ↓
커널의 예외 처리 코드
   ↓
시스템 콜 처리
   ↓
개별 Service 함수 실행
   ↓
Kernel Mode → User Mode
   ↓
read() 호출 이후로 복귀
```

즉 시스템 콜이 발생하면:

1. CPU가 **User Mode → Kernel Mode**로 전환
2. 커널의 예외 처리 코드 실행
3. 시스템 콜 번호에 해당하는 서비스 처리
4. 결과 반환
5. **Kernel Mode → User Mode**로 복귀
6. 시스템 콜을 호출했던 프로그램의 실행을 계속함

> 참고: 실제 시스템 콜 진입 방식과 커널 함수 이름은 CPU 아키텍처와 Kernel 버전에 따라 다를 수 있다. 수업에서는 `sys_read()` 형태로 개념을 이해하면 된다.

---

<a id="notion-3e91d46c18fc80de82d5eaf3a23bb6f3"></a>

## 시스템 콜 Wrapper API

⭐ **시험 ★★★**

응용 프로그램에서 사용하는:

```text
read()
write()
open()
```

등은 시스템 콜을 사용하기 위한 **Wrapper API**이다.

예:

```text
Application
    ↓
read()
    ↓
시스템 콜 진입
    ↓
Kernel의 read 관련 서비스
```

<a id="notion-3e91d46c18fc80e48efec2a40818d253"></a>

### 시스템 콜 번호

각 시스템 콜에는 **고유한 시스템 콜 번호**가 할당되어 있다.

```text
시스템 콜 번호
→ 어떤 커널 서비스를 실행할지 구분
```

수업 예:

```text
System Call Number 63
→ read
```

시스템 콜 번호와 매개변수는 주로 **CPU Register**를 통해 Kernel로 전달된다.

```text
Register
├─ System Call Number
├─ Argument 1
├─ Argument 2
├─ Argument 3
└─ ...
```

실행 결과 역시 일반적으로 Register를 통해 User Space로 전달된다.

⚠️ **중요**

```text
시스템 콜 번호
→ Kernel ABI에 정의되어 있음
→ 응용 프로그램이 임의로 변경하는 값이 아님
```

---

<a id="notion-3e91d46c18fc80de9e0fc2afa9b8aea3"></a>

# 메모리 관리

<a id="notion-3e91d46c18fc80b484fad6f35673c0e1"></a>

## 가상 메모리와 물리 메모리

CPU가 프로그램을 실행하면서 사용하는 주소는 기본적으로 \*\*가상 주소(Virtual Address)\*\*이다.

```text
CPU
 ↓
Virtual Address
 ↓
MMU
 ↓
Physical Address
 ↓
Physical Memory
```

MMU는 페이지 테이블 등의 정보를 이용하여:

```text
Virtual Address → Physical Address
```

변환을 수행한다.

---

<a id="notion-3e91d46c18fc80f89404eadbe14ebeea"></a>

## 페이지(Page)

Linux Kernel은 물리 메모리를 **페이지(Page) 단위로 관리**한다.

많은 시스템에서 기본 페이지 크기는:

```text
4 KB
```

이다.

각 물리 페이지에 대한 관리 정보는 Kernel에서:

```text
struct page
```

구조체를 이용해 표현한다.

`struct page`에는 해당 페이지의 상태와 관리에 필요한 정보가 들어 있다.

예:

```text
flags
→ 페이지의 여러 상태 정보

page_count()
→ 페이지의 참조 횟수 관련 정보 확인
```

---

<a id="notion-3e91d46c18fc809ebaaade5e654eca14"></a>

## 📝 페이지 구조체 배열 크기 계산

조건:

```text
Physical Memory = 256 MB
Page Size       = 4 KB
struct page     = 40 Byte
```

<a id="notion-3e91d46c18fc80c6ac2fc180a5c529d6"></a>

### 페이지 개수

```text
256 MB / 4 KB

= (256 × 1024 × 1024)
  -------------------
       (4 × 1024)

= 65,536 pages
```

즉 물리 메모리를 관리하려면:

```text
struct page × 65,536개
```

가 필요하다.

<a id="notion-3e91d46c18fc80db9059f0443a298f87"></a>

### `struct page` 배열 크기

```text
65,536 × 40 Byte
= 2,621,440 Byte
```

이를 MiB로 계산하면:

```text
2,621,440 / 1024 / 1024
= 2.5 MiB
```

따라서:

📝 **정답**

```text
페이지 개수
= 65,536개

struct page 배열 크기
= 2,621,440 Byte
= 약 2.5 MiB
```

<a id="notion-3e91d46c18fc8041812ae79d648f94b9"></a>

### 계산 공식

```text
페이지 개수
= 물리 메모리 크기 / 페이지 크기

페이지 관리 배열 크기
= 페이지 개수 × sizeof(struct page)
```

<a id="notion-3e91d46c18fc8048b918d142e4f21093"></a>

## Zone

Linux Kernel은 물리 메모리의 페이지들을 **용도와 접근 가능한 주소 범위에 따라 Zone으로 구분하여 관리**한다.

수업에서 다루는 주요 Zone은 다음과 같다.

<a id="notion-3e91d46c18fc8081b271f890e090d9b4"></a>

### `ZONE_DMA`

DMA에 사용할 수 있는 페이지 영역.

<a id="notion-3e91d46c18fc8061a986d35f24a1d7f8"></a>

### `ZONE_DMA32`

DMA 용도로 사용되며 **32비트 주소 범위에서 접근 가능한 페이지 영역**이다.

<a id="notion-3e91d46c18fc800eb0c9f0389d9ddb1f"></a>

### `ZONE_NORMAL`

Kernel에서 일반적으로 사용하는 페이지 영역.

<a id="notion-3e91d46c18fc80989a9edce402c4b25e"></a>

### `ZONE_HIGHMEM`

32bit 시스템에서 Low Memory 영역을 넘어서는 상위 물리 메모리를 관리하기 위한 영역이다.

필요한 경우 Kernel 주소 공간에 동적으로 매핑하여 접근한다.

---

<a id="notion-3e91d46c18fc80d68031c3d12600bcb9"></a>

## 페이지 테이블(Page Table)

페이지 테이블은:

> **가상 주소를 물리 주소로 변환하기 위한 테이블**

이다.

CPU가 가상 주소에 접근하면 MMU가 페이지 테이블을 참조하여 물리 주소로 변환한다.

```text
프로세스 가상 주소 공간
        ↓
       MMU
        ↓
프로세스의 Page Table 참조
        ↓
물리 주소
        ↓
물리 메모리
```

프로세스마다 자신의 주소 공간에 대응되는 페이지 테이블이 존재하며, 페이지 테이블의 구체적인 구조는 **CPU Architecture에 의존적**이다.

---

<a id="notion-3e91d46c18fc80938ea8e137b9fd2eef"></a>

### Page Fault

⚠️ **중요**

물리 메모리가 아직 매핑되지 않은 가상 메모리에 접근하면:

```text
Page Fault
```

가 발생한다.

가상 주소 공간 전체에 처음부터 물리 메모리를 할당하는 것은 비효율적이므로, 실제로 필요한 시점에 물리 페이지를 할당하여 사용하는 방식이 가능하다.

```text
가상 주소 공간 확보
        ↓
실제 접근
        ↓
필요한 물리 페이지가 없음
        ↓
Page Fault
        ↓
Kernel이 필요한 처리 수행
```

---

<a id="notion-3e91d46c18fc80cb91c5e8ae703818eb"></a>

## 커널 주소 공간 — 32bit 시스템

수업에서 다루는 32bit 시스템 기준:

```text
전체 가상 주소 공간 = 4 GB

User Space   = 3 GB
Kernel Space = 1 GB
```

```text
0 GB                    3 GB             4 GB
├────────────────────────┼─────────────────┤
│       User Space       │  Kernel Space   │
│          3 GB          │      1 GB       │
└────────────────────────┴─────────────────┘
```

---

<a id="notion-3e91d46c18fc80298ec9e6f2cbe71043"></a>

### Low Memory

Kernel 주소 공간 중 물리 메모리와 직접 매핑하여 사용하는 영역.

대표적으로:

```text
Kernel .text
Kernel .data
Kernel .init
동적 할당 영역
```

등이 위치한다.

수업 기준으로 Low Memory는 **물리 메모리와 1:1로 매핑되는 영역**으로 이해한다.

---

<a id="notion-3e91d46c18fc8034b490d715b2489b64"></a>

### 동적 매핑 영역

Kernel 주소 공간에는 필요에 따라 동적으로 매핑하여 사용하는 영역도 존재한다.

```text
vmalloc
pkmap
fixmap
```

---

<a id="notion-3e91d46c18fc80b6b75ff1e49fb0dfa8"></a>

## 페이지 단위 메모리 할당

Linux는 물리 메모리를 **Page 단위로 관리**하므로 Kernel에서도 기본적으로 페이지 단위로 메모리를 할당하거나 반납할 수 있다.

---

<a id="notion-3e91d46c18fc80d2b6e2c6d21bee811f"></a>

### `alloc_page()`

```text
alloc_page(...)
```

하나의 페이지를 할당한다.

반환값:

```text
할당된 페이지의 struct page *
```

즉 <strong>가상 주소가 아니라 해당 페이지를 표현하는</strong> **`struct page`** <strong>주소를 반환</strong>한다.

---

<a id="notion-3e91d46c18fc80f8b9d3da0f919c01d2"></a>

### `__get_free_page()`

```text
__get_free_page(...)
```

하나의 페이지를 할당한다.

반환값:

```text
할당된 페이지의 가상 주소
```

---

<a id="notion-3e91d46c18fc807eb124c3d85067f57a"></a>

### `get_zeroed_page()`

```text
get_zeroed_page(...)
```

하나의 페이지를 할당하고 **페이지 내용을 0으로 초기화**한다.

반환값:

```text
할당된 페이지의 가상 주소
```

```text
__get_free_page()
→ 1 Page 할당

get_zeroed_page()
→ 1 Page 할당
→ 메모리를 0으로 초기화
```

---

<a id="notion-3e91d46c18fc80469e02e24034e4bb3b"></a>

### `alloc_pages()`

```text
alloc_pages(..., order)
```

<strong>연속된</strong> <strong>`2^order`</strong>**개의 페이지**를 할당한다.

반환값:

```text
첫 번째 페이지의 struct page *
```

예:

```text
order = 0 → 2^0 = 1 Page
order = 1 → 2^1 = 2 Pages
order = 2 → 2^2 = 4 Pages
order = 3 → 2^3 = 8 Pages
```

⚠️ `order` 자체가 페이지 개수가 아니라:

```text
페이지 개수 = 2^order
```

이다.

---

<a id="notion-3e91d46c18fc80bfb2aacd28a272b220"></a>

### `__get_free_pages()`

여러 개의 연속된 페이지를 할당하며, 할당된 메모리의 **가상 주소를 반환**한다.

```text
alloc_pages()
→ struct page * 반환

__get_free_pages()
→ 가상 주소 반환
```

---

<a id="notion-3e91d46c18fc8018a094f3d7611262c7"></a>

## 페이지 반납

할당한 페이지는 사용이 끝난 뒤 반납해야 한다.

주요 함수:

```text
__free_pages()
free_pages()
free_page()
```

할당 방식과 페이지 개수에 맞는 함수를 사용하여 물리 페이지를 Kernel에 반환한다.

<a id="notion-3e91d46c18fc8094b217ef8b2279617d"></a>

# 오늘 배운 내용 요약정리

<a id="notion-3e91d46c18fc80fc8251c4a28c450223"></a>

## POSIX 세마포어

- Named Semaphore → 프로세스 간 동기화
- Unnamed Semaphore → 스레드 간 동기화
- `sem_wait()` → 획득 / 0이면 대기
- `sem_post()` → 반환 / 값 증가
- Mutex → 공유 자원 보호
- Semaphore → 실행 순서 동기화

<a id="notion-3e91d46c18fc8011a197e5b77114b546"></a>

## Reentrant / MT-Safe

- Reentrant → 공유 상태 간섭 없이 안전
- MT-Safe → 여러 스레드 동시 호출 안전
- `Reentrant ⊂ MT-Safe`
- `strtok()` ↔ `strtok_r()`
- `errno` → 스레드별 독립 관리

<a id="notion-3e91d46c18fc80e9bb1bd4906defdef7"></a>

## Linux Kernel Task

- Process / Thread / Kernel Thread → 모두 Task로 관리
- `task_struct` → Task 정보 관리
- 상태 → `R / S / D / T / Z`
- 생성 → `kernel_clone()` → `copy_process()`
- 종료 → `do_exit()` → `release_task()`

📝 **시험**

- 커널 스레드 생성 → `kernel_thread()`
- `task_struct` 최종 해제 → `release_task()`

<a id="notion-3e91d46c18fc80eeb105ec0130714f05"></a>

## 시스템 콜

- `read()`, `write()`, `open()` → System Call Wrapper API
- User Mode → Kernel Mode → 서비스 실행 → User Mode
- System Call 번호/인자/반환값 → 주로 Register 사용

<a id="notion-3e91d46c18fc802d9cb4e0eada1bc746"></a>

## Kernel 메모리

- 물리 메모리 → Page 단위 관리
- Page 정보 → `struct page`
- Zone → `DMA / DMA32 / NORMAL / HIGHMEM`
- Page Table → Virtual → Physical 주소 변환
- MMU → Page Table 참조
- 미매핑 주소 접근 → Page Fault

<a id="notion-3e91d46c18fc80f2841ddab73cfbe957"></a>

## Page 할당

- `alloc_page()` → 1 Page, `struct page *`
- `__get_free_page()` → 1 Page, 가상 주소
- `get_zeroed_page()` → 1 Page + 0 초기화
- `alloc_pages(order)` → `2^order` Page
- `__free_pages()`, `free_pages()`, `free_page()` → 반납
