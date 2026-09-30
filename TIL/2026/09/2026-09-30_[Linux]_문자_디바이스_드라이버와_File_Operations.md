# \[Linux\] 문자 디바이스 드라이버와 File Operations

> 날짜: 2026-09-30
> 원본 노션: [링크](https://app.notion.com/p/Linux-File-Operations-3ea1d46c18fc80cc84c8d800aab25f16)

<!-- notion-page-id: 3ea1d46c18fc80cc84c8d800aab25f16 -->
<!-- notion-title: "[Linux] 문자 디바이스 드라이버와 File Operations" -->

---

<a id="notion-3eb1d46c18fc8060a37ac360ec167087"></a>

# 문자 드라이버

<a id="notion-3eb1d46c18fc8087be0df6e3fec92ca4"></a>

## 디바이스 번호

디바이스 번호(Device Number)는 **Major 번호와 Minor 번호를 결합한 값**이다.

```text
Device Number
= Major + Minor
```

디바이스 번호는:

```text
dev_t
```

타입으로 표현한다.

수업 기준 구성:

```text
Major → 12bit
Minor → 20bit
```

<a id="notion-3eb1d46c18fc80a59c34d312dc971a4f"></a>

### 디바이스 번호 관련 매크로

```text
MAJOR(dev)
```

- `dev`에서 Major 번호 추출

```text
MINOR(dev)
```

- `dev`에서 Minor 번호 추출

```text
MKDEV(ma, mi)
```

- Major와 Minor 번호를 결합하여 `dev_t` 생성

```text
dev → 디바이스 번호
ma  → Major 번호
mi  → Minor 번호
```

---

<a id="notion-3eb1d46c18fc809f9bdac4e4ecedbf99"></a>

## 디바이스 번호 등록 및 해제

<a id="notion-3eb1d46c18fc800daec3e75cd1961801"></a>

### `register_chrdev_region()`

**고정된 Major 번호**와 고정된 Minor 번호 범위를 등록한다.

```text
register_chrdev_region(from, count, name);
```

```text
from
→ Major + 시작 Minor 번호

count
→ 사용할 Minor 번호 개수

name
→ /proc/devices에 표시될 이름
```

- 성공 → `0`
- 실패 → 음수

즉:

```text
Major 번호 직접 지정
+
Minor 시작 번호 직접 지정
```

---

<a id="notion-3eb1d46c18fc80ebbebbe632655c134b"></a>

### `alloc_chrdev_region()`

**Major 번호를 자동으로 할당**받고 Minor 번호 범위를 등록한다.

```text
alloc_chrdev_region(dev, baseminor, count, name);
```

```text
dev
→ 자동 할당된 Major + Minor 번호 저장

baseminor
→ 시작 Minor 번호

count
→ 사용할 Minor 번호 개수

name
→ /proc/devices에 표시될 이름
```

- Major 번호 → Kernel이 자동 할당
- Minor 시작 번호 → 직접 지정
- 할당된 디바이스 번호는 `dev`가 가리키는 곳에 저장
- 실패 → 음수

즉:

```text
Major → 자동 할당
Minor → 시작 번호 지정
```

---

<a id="notion-3eb1d46c18fc809a9795c433dd57cebf"></a>

## `unregister_chrdev_region()`

등록했던 **디바이스 번호를 반납**한다.

```text
unregister_chrdev_region(from, count);
```

```text
from
→ Major + 시작 Minor 번호

count
→ 반납할 Minor 번호 개수
```

---

<a id="notion-3eb1d46c18fc80b888bad4ff1ae0b8ab"></a>

## 등록 방식 비교

```text
register_chrdev_region()
→ Major 번호 직접 지정

alloc_chrdev_region()
→ Major 번호 자동 할당

unregister_chrdev_region()
→ 등록한 디바이스 번호 반납
```

<a id="notion-3eb1d46c18fc80b18698f54884098460"></a>

### 디바이스 번호 등록

문자 디바이스를 사용하려면 먼저 **Major / Minor 번호 범위**를 등록해야 한다.

```text
devt = MKDEV(device_major, device_minor_start);

ret = register_chrdev_region(
    devt,
    device_minor_count,
    "my_device"
);
```

```text
device_major
→ Major 번호

device_minor_start
→ 시작 Minor 번호

device_minor_count
→ 사용할 Minor 번호 개수

devt
→ Major + Minor가 결합된 디바이스 번호
```

등록:

```text
register_chrdev_region(devt, device_minor_count, "my_device");
```

해제:

```text
unregister_chrdev_region(devt, device_minor_count);
```

---

<a id="notion-3eb1d46c18fc800b9d8ac39ff6308d54"></a>

## `inode`와 디바이스 번호

디바이스 파일의 `inode`에는 해당 디바이스 파일의 **디바이스 번호**가 저장된다.

```text
struct inode {
    dev_t i_rdev;
    ...
};
```

```text
i_rdev
→ 디바이스 파일의 Device Number
```

Major / Minor 번호 확인:

```text
imajor(inode);
iminor(inode);
```

```text
imajor()
→ Major 번호

iminor()
→ Minor 번호
```

---

<a id="notion-3eb1d46c18fc803bb0e2fd09024362e5"></a>

## 열린 디바이스 파일 — `file`

열린 디바이스 파일은 `struct file`로 표현된다.

주요 멤버:

```text
f_flags
→ O_RDONLY, O_RDWR, O_NONBLOCK 등의 Open Flag

f_op
→ 해당 파일의 file_operations 객체

private_data
→ Driver에서 자유롭게 사용할 수 있는 데이터
```

`O_NONBLOCK`이 설정되어 있으면 Nonblocking 방식으로 동작할 수 있다.

---

<a id="notion-3eb1d46c18fc80bc8fe2eace3b9dcedf"></a>

## 📝 디바이스 파일의 역할

📝 **시험 가능성 ★**

> **응용 프로그램과 디바이스 드라이버 간의 매개체 역할**

응용 프로그램의 File API와 Driver의 함수가 연결된다.

```text
open()   → open
read()   → read
write()  → write

close()  → release
ioctl()  → unlocked_ioctl
```

⚠️ `close()`와 `ioctl()`은 Driver 측 함수 이름이 다르므로 주의.

---

<a id="notion-3eb1d46c18fc8038a911fd1cf5b39300"></a>

# `cdev` 구조체

`struct cdev`는 **문자 디바이스의 핵심 구조체**이다.

주요 멤버:

```text
owner
→ cdev를 사용하는 Module
→ 대부분 THIS_MODULE

ops
→ file_operations 객체 주소

dev
→ Device Number

count
→ Minor 번호 개수
```

---

<a id="notion-3eb1d46c18fc80bcabb1fac047195229"></a>

## 문자 디바이스 등록 API

<a id="notion-3eb1d46c18fc80ba86eac651470d4968"></a>

### `cdev_alloc()`

```text
cdev_alloc();
```

- `cdev` 객체를 동적으로 할당
- 기본 초기화 수행

---

<a id="notion-3eb1d46c18fc805f9da3dfd98600f135"></a>

### `cdev_init()`

```text
cdev_init(cdev, fops);
```

- `cdev` 객체 초기화
- `file_operations`와 연결

---

<a id="notion-3eb1d46c18fc80dfb98bece852f9986a"></a>

### `cdev_add()`

```text
cdev_add(cdev, dev, count);
```

📝 **시험 가능성 ★**

**문자 디바이스를 Kernel에 등록**한다.

```text
cdev
→ 등록할 cdev 객체

dev
→ 시작 Device Number

count
→ 사용할 Minor 번호 개수
```

⚠️ 문자 디바이스를 실제로 Kernel에 등록하려면 `cdev_add()` 과정이 필요하다.

---

<a id="notion-3eb1d46c18fc80a9bd79d194de032dac"></a>

### `cdev_del()`

```text
cdev_del(cdev);
```

등록한 문자 디바이스를 Kernel에서 제거한다.

---

<a id="notion-3eb1d46c18fc803caa70d5d81b193ccd"></a>

# 문자 디바이스 등록 과정

문자 디바이스 등록은 크게 **2단계**로 볼 수 있다.

<a id="notion-3eb1d46c18fc80699010e88d70992331"></a>

## 1단계 — 디바이스 번호 등록

```text
devt = MKDEV(device_major, device_minor_start);

register_chrdev_region(
    devt,
    device_minor_count,
    "my_device"
);
```

```text
Major / Minor 번호 확보
```

---

<a id="notion-3eb1d46c18fc80e5b1efddd6fc1033f1"></a>

## 2단계 — `cdev` 등록

```text
my_cdev = cdev_alloc();

my_cdev->ops = &my_fops;
my_cdev->owner = THIS_MODULE;

cdev_add(
    my_cdev,
    devt,
    device_minor_count
);
```

흐름:

```text
cdev_alloc()
→ cdev 생성

ops
→ file_operations 연결

owner
→ Module 연결

cdev_add()
→ 문자 디바이스 Kernel 등록
```

---

<a id="notion-3eb1d46c18fc80018708ff17e0c9e6fe"></a>

## `file_operations`

```text
static const struct file_operations my_fops = {
    .owner = THIS_MODULE,
};
```

`file_operations`는 응용 프로그램의 File API와 Driver 함수를 연결한다.

예:

```text
read()
→ Driver의 read 함수

write()
→ Driver의 write 함수

open()
→ Driver의 open 함수

close()
→ Driver의 release 함수
```

---

<a id="notion-3eb1d46c18fc80bc9a2ff7523a28a32f"></a>

## 문자 디바이스 해제

Module 제거 시:

```text
cdev_del(my_cdev);

unregister_chrdev_region(
    devt,
    device_minor_count
);
```

순서:

```text
cdev_del()
→ 문자 디바이스 해제

unregister_chrdev_region()
→ 디바이스 번호 반납
```

---

<a id="notion-3eb1d46c18fc8070acf7d9d2b5d3173a"></a>

# 전통적인 문자 디바이스 등록

<a id="notion-3eb1d46c18fc80c5883def16967a5a61"></a>

## `register_chrdev()`

```text
register_chrdev(
    device_major,
    "my_device",
    &my_fops
);
```

전통적인 문자 디바이스 등록 함수이다.

내부적으로:

```text
1단계
→ 디바이스 번호 등록

2단계
→ cdev 객체 등록
```

을 함께 수행한다.

특징:

```text
Minor 번호
→ 0번부터 256개 사용
```

등록:

```text
ret = register_chrdev(
    device_major,
    "my_device",
    &my_fops
);
```

해제:

```text
unregister_chrdev(
    device_major,
    "my_device"
);
```

---

<a id="notion-3eb1d46c18fc801686a0d05313d8c9cf"></a>

## 등록 방식 비교

<a id="notion-3eb1d46c18fc807a9739d895c8d4f07f"></a>

### 현재 방식

```text
register_chrdev_region()
        ↓
cdev_alloc() / cdev_init()
        ↓
cdev_add()
```

디바이스 번호와 `cdev`를 각각 직접 관리한다.

<a id="notion-3eb1d46c18fc803c9842ec2983e5542a"></a>

### 전통적인 방식

```text
register_chrdev()
```

하나의 API에서 디바이스 번호 등록과 문자 디바이스 등록을 함께 처리한다.

<a id="notion-3eb1d46c18fc80919a14f349771a2935"></a>

## `xxx_open()`과 `xxx_release()`

<a id="notion-3eb1d46c18fc80a09a53f9c30b5b25c5"></a>

### `xxx_open()`

응용 프로그램이 디바이스 파일을 `open()`할 때 호출되는 드라이버 함수이다.

주요 역할:

- 디바이스 상태 확인
- 에러 상태 확인
- 디바이스 초기화

<a id="notion-3eb1d46c18fc80fd82b3c0d367a934b1"></a>

### `xxx_release()`

응용 프로그램이 디바이스 파일을 `close()`할 때 호출되는 드라이버 함수이다.

주요 역할:

- `xxx_open()`에서 수행한 작업의 반대 작업
- 디바이스 사용 종료 처리

즉:

```text
open()
→ xxx_open()

close()
→ xxx_release()
```

---

<a id="notion-3eb1d46c18fc8040a6d2fb50fd51ed05"></a>

## `xxx_open()` 호출 과정

응용 프로그램:

```text
fd = open("/dev/mydev", O_RDWR);
```

호출 과정:

```text
1. 문자 디바이스가 Kernel에 등록되어 있음
        ↓
2. Application에서 /dev/mydev open()
        ↓
3. Kernel이 mydev 관련 구조체를 찾음
        ↓
4. file 객체의 f_op를 my_fops와 연결
        ↓
5. my_fops.open에 등록된 device_open() 호출
```

즉:

```text
Application open()
        ↓
Device File
        ↓
cdev
        ↓
file_operations
        ↓
device_open()
```

---

<a id="notion-3eb1d46c18fc80b09babc06b7036c471"></a>

## Application 코드

```text
fd = open(DEV_NAME, O_RDWR);
```

디바이스 파일 열기.

```text
close(fd);
```

디바이스 파일 닫기.

실행 흐름:

```text
open("/dev/mydev")
→ Driver의 device_open()

close(fd)
→ Driver의 device_release()
```

---

<a id="notion-3eb1d46c18fc80b1861bd06dd25046d0"></a>

# Driver 구현

<a id="notion-3eb1d46c18fc808ba38cd11bbb26f49d"></a>

## `device_open()`

```text
static int device_open(struct inode *inode, struct file *filp)
{
    printk("devtest: device_open (minor = %d)\n", iminor(inode));

    return 0;
}
```

주요 매개변수:

```text
inode
→ Device File의 inode 정보

filp
→ 열린 Device File을 나타내는 struct file
```

```text
iminor(inode)
```

→ 열린 디바이스 파일의 Minor 번호 확인

---

<a id="notion-3eb1d46c18fc80aa9bffdb95010a7559"></a>

## `device_release()`

```text
static int device_release(struct inode *inode, struct file *filp)
{
    printk("devtest: device_release\n");

    return 0;
}
```

디바이스 파일이 닫힐 때 호출된다.

---

<a id="notion-3eb1d46c18fc80c7be87c77602950290"></a>

# `file_operations` 연결

```text
static const struct file_operations my_fops = {
    .owner = THIS_MODULE,
    .open = device_open,
    .release = device_release,
};
```

의미:

```text
.owner
→ 이 Driver를 사용하는 Module

.open
→ open() 시 호출할 함수

.release
→ close() 시 호출할 함수
```

연결 관계:

```text
Application        Driver

open()
   ↓
my_fops.open
   ↓
device_open()


close()
   ↓
my_fops.release
   ↓
device_release()
```

---

<a id="notion-3eb1d46c18fc800bb68be094a799446b"></a>

## 문자 디바이스 전체 흐름

```text
1. 디바이스 파일 생성

sudo mknod /dev/mydev c 120 0

c
→ 문자 디바이스 파일

120
→ Major 번호
→ 어떤 문자 디바이스 드라이버를 사용할지 구분

0
→ Minor 번호
→ 해당 드라이버가 관리하는 몇 번째 장치인지 구분
```

```text
2. 모듈 로드

sudo insmod devtest.ko
        ↓
device_init()
        ↓
MKDEV(120, 0)
        ↓
register_chrdev_region()
→ Major 120, Minor 0부터 번호 등록
        ↓
cdev_alloc() / cdev_init()
        ↓
cdev_add()
→ 문자 디바이스 등록
        ↓
file_operations 연결
        ↓
Driver 준비 완료
```

```text
3. Application에서 디바이스 열기

open("/dev/mydev", O_RDWR)
        ↓
/dev/mydev의 Device Number 확인
        ↓
Major 120
→ 해당 Driver 찾음

Minor 0
→ Driver가 관리하는 0번 Device
        ↓
file_operations.open
        ↓
device_open()
```

```text
4. 디바이스 닫기

close(fd)
        ↓
file_operations.release
        ↓
device_release()
```

```text
5. Application 종료

apptest 종료
→ Driver는 Kernel에 그대로 존재
```

```text
6. 모듈 제거

sudo rmmod devtest
        ↓
device_exit()
        ↓
cdev_del()
→ 문자 디바이스 해제
        ↓
unregister_chrdev_region()
→ Device Number 반납
```

<a id="notion-3eb1d46c18fc8046a55bed80525387d2"></a>

### 핵심 흐름

```text
mknod
→ Device File 생성

insmod
→ device_init()
→ Device Number 등록
→ cdev 등록

open()
→ /dev/mydev
→ Major / Minor
→ file_operations
→ device_open()

close()
→ file_operations
→ device_release()

rmmod
→ device_exit()
→ cdev 해제
→ Device Number 반납
```

<a id="notion-3eb1d46c18fc8085b55ccba0ff714445"></a>

## `xxx_read()` / `xxx_write()` 추가

📝 **시험 가능성 ★ — 코드 수정 문제**

응용 프로그램의:

```text
read()  → Driver의 xxx_read()
write() → Driver의 xxx_write()
```

가 호출되도록 `file_operations`에 연결한다.

```text
static const struct file_operations my_fops = {
    .owner = THIS_MODULE,
    .open = device_open,
    .release = device_release,
    .read = device_read,
    .write = device_write,
};
```

---

<a id="notion-3eb1d46c18fc8006b806f8c11895e2f4"></a>

## `xxx_read()`

응용 프로그램이 디바이스 파일을 `read()`하면 호출된다.

```text
static ssize_t device_read(
    struct file *filp,
    char __user *buf,
    size_t count,
    loff_t *f_pos)
```

주요 변수:

```text
buf
→ User Space의 읽기 버퍼

count
→ Application이 요청한 읽기 크기

rbuf
→ Kernel Driver의 읽기 버퍼

rlen
→ 실제 읽어줄 크기
```

읽을 크기 결정:

```text
if (count < MAX_BUF)
    rlen = count;
else
    rlen = MAX_BUF;
```

즉:

```text
rlen = min(count, MAX_BUF)
```

<a id="notion-3eb1d46c18fc8047a8aef169077c0c77"></a>

### `copy_to_user()`

```text
copy_to_user(buf, rbuf, rlen);
```

```text
Kernel Space
rbuf
 ↓
copy_to_user()
 ↓
User Space
buf
```

복사 실패:

```text
return -EFAULT;
```

<a id="notion-3eb1d46c18fc80dc90f5c4dc67fc8b47"></a>

### 핵심

```text
read()
→ device_read()
→ copy_to_user()
→ Kernel → User
```

---

<a id="notion-3eb1d46c18fc8077ac6ef391e16857db"></a>

## `xxx_write()`

응용 프로그램이 디바이스 파일을 `write()`하면 호출된다.

```text
static ssize_t device_write(
    struct file *filp,
    const char __user *buf,
    size_t count,
    loff_t *f_pos)
```

주요 변수:

```text
buf
→ User Space에서 전달한 데이터

count
→ Application이 요청한 쓰기 크기

wbuf
→ Kernel Driver의 쓰기 버퍼

wlen
→ 실제 쓸 크기
```

쓰기 크기 결정:

```text
if (count < MAX_BUF)
    wlen = count;
else
    wlen = MAX_BUF;
```

<a id="notion-3eb1d46c18fc806ca74bcc6f2b7d6072"></a>

### `copy_from_user()`

```text
copy_from_user(wbuf, buf, wlen);
```

```text
User Space
buf
 ↓
copy_from_user()
 ↓
Kernel Space
wbuf
```

복사 실패:

```text
return -EFAULT;
```

<a id="notion-3eb1d46c18fc80b1aa8feb6f7fe40ce3"></a>

### 핵심

```text
write()
→ device_write()
→ copy_from_user()
→ User → Kernel
```

---

<a id="notion-3eb1d46c18fc802e9c4bcd984f04b776"></a>

## `read()` / `write()` 핵심 암기

```text
copy_to_user()
→ Kernel → User
→ read()

copy_from_user()
→ User → Kernel
→ write()
```

---

<a id="notion-3eb1d46c18fc803d9c82c2c3004c7fc8"></a>

# `ioctl`

<a id="notion-3eb1d46c18fc8006803cf48178dc616a"></a>

## `xxx_ioctl()`

`read()` / `write()`만으로 처리하기 어려운 **디바이스 제어 동작**을 수행할 때 사용한다.

```text
read / write
→ 데이터 전달

ioctl
→ 디바이스 제어 명령
```

`ioctl()`의 인자는 `cmd`에 따라 의미가 달라진다.

User Space에서 포인터를 전달하면 Driver에서는:

```text
1. Application에서 Pointer 전달
2. Driver에서는 unsigned long arg로 받음
3. 필요한 Pointer Type으로 변환
4. copy_from_user() / copy_to_user() 등으로 처리
```

---

<a id="notion-3eb1d46c18fc804ea71bc24917ed647c"></a>

# ioctl 번호

ioctl 명령은 하나의 번호로 구성된다.

```text
dir  | size | type | nr
2bit   14bit  8bit  8bit
```

<a id="notion-3eb1d46c18fc80f1b168da28f946e3ff"></a>

## `dir`

Application 기준 데이터 전달 방향.

```text
0 → NONE
1 → WRITE
2 → READ
3 → READ / WRITE
```

즉:

```text
WRITE
→ Application → Driver

READ
→ Driver → Application
```

<a id="notion-3eb1d46c18fc80edaa4bd6f9d762175e"></a>

## `size`

- ioctl 인자가 가리키는 실제 데이터 크기

<a id="notion-3eb1d46c18fc8065868df7a8d19f49f3"></a>

## `type`

- Driver를 구분하기 위한 코드
- 보통 Magic Number 사용

<a id="notion-3eb1d46c18fc809a918fc92ff82e4c31"></a>

## `nr`

- 해당 Driver 내부의 ioctl 명령 일련번호

---

<a id="notion-3eb1d46c18fc801b8480e42d566adfeb"></a>

## ioctl 명령 생성 매크로

```text
_IO(type, nr)
```

→ 데이터 전달 없음

```text
_IOR(type, nr, size)
```

→ Driver → Application

```text
_IOW(type, nr, size)
```

→ Application → Driver

```text
_IOWR(type, nr, size)
```

→ 양방향

---

<a id="notion-3eb1d46c18fc80b69177f03084aa08e5"></a>

# `my_ioctl.h`

```text
#define MY_IOCTL_MAGIC 'k'

#define MY_IOCTL_CMD_ONE   _IO(MY_IOCTL_MAGIC, 1)
#define MY_IOCTL_CMD_TWO   _IOW(MY_IOCTL_MAGIC, 2, int)
#define MY_IOCTL_CMD_THREE _IO(MY_IOCTL_MAGIC, 3)
```

의미:

```text
MY_IOCTL_CMD_ONE
→ 데이터 전달 없음

MY_IOCTL_CMD_TWO
→ int 데이터
→ Application → Driver

MY_IOCTL_CMD_THREE
→ 데이터 전달 없음
```

---

<a id="notion-3eb1d46c18fc80b08c2ff9635486a720"></a>

# Application에서 `ioctl()` 호출

<a id="notion-3eb1d46c18fc807c85adfa34969950ef"></a>

## `MY_IOCTL_CMD_ONE`

```text
ret = ioctl(fd, MY_IOCTL_CMD_ONE);
```

데이터 전달 없이 명령만 전달한다.

---

<a id="notion-3eb1d46c18fc801682b5c58d357f6865"></a>

## `MY_IOCTL_CMD_TWO`

```text
int uarg = 12345678;

ret = ioctl(fd, MY_IOCTL_CMD_TWO, &uarg);
```

Application은 `uarg`의 주소를 전달한다.

```text
Application
&uarg
 ↓
ioctl()
 ↓
unsigned long arg
 ↓
Driver
```

---

<a id="notion-3eb1d46c18fc80579a00dd1a271ed073"></a>

# Driver의 `device_ioctl()`

```text
static long device_ioctl(
    struct file *filp,
    unsigned int cmd,
    unsigned long arg)
```

주요 변수:

```text
cmd
→ ioctl Command 번호

arg
→ Application에서 전달한 인자
```

`cmd`에 따라 처리한다.

```text
switch (cmd)
{
case MY_IOCTL_CMD_ONE:
    ...
    break;

case MY_IOCTL_CMD_TWO:
    ...
    break;

default:
    ...
    break;
}
```

---

<a id="notion-3eb1d46c18fc80509067f0b5682351c1"></a>

## `MY_IOCTL_CMD_TWO`

Application:

```text
int uarg = 12345678;

ioctl(fd, MY_IOCTL_CMD_TWO, &uarg);
```

Driver:

```text
if (copy_from_user(&data, (int *)arg, sizeof(int)))
{
    printk("devtest: copy_from_user error\n");
    return -EFAULT;
}
```

흐름:

```text
Application의 uarg
        ↓
      &uarg
        ↓
     ioctl()
        ↓
unsigned long arg
        ↓
   (int *)arg
        ↓
copy_from_user()
        ↓
Kernel의 data
```

출력:

```text
printk("devtest: MY_IOCTL_CMD_TWO(%d)\n", data);
```

---

<a id="notion-3eb1d46c18fc8019b596e78822225268"></a>

## 알 수 없는 ioctl 명령

```text
default:
    printk("devtest: unknown command\n");
    ret = -EINVAL;
    break;
```

지원하지 않는 명령이면 Error를 반환한다.

---

<a id="notion-3eb1d46c18fc8035a1f7fe664a6d3860"></a>

# `file_operations`에 ioctl 연결

```text
static const struct file_operations my_fops = {
    .owner = THIS_MODULE,
    .open = device_open,
    .release = device_release,
    .read = device_read,
    .write = device_write,
    .unlocked_ioctl = device_ioctl,
};
```

연결 관계:

```text
Application        Driver

open()
→ device_open()

read()
→ device_read()

write()
→ device_write()

ioctl()
→ device_ioctl()

close()
→ device_release()
```

---

<a id="notion-3eb1d46c18fc801cb015f3fef377bcc4"></a>

# 전체 핵심

```text
read()
→ copy_to_user()
→ Kernel → User

write()
→ copy_from_user()
→ User → Kernel

ioctl()
→ read/write 이외의 Device 제어
→ cmd에 따라 동작 결정
```

ioctl 번호:

```text
dir | size | type | nr
```

ioctl Macro:

```text
_IO   → 데이터 없음
_IOR  → Driver → Application
_IOW  → Application → Driver
_IOWR → 양방향
```

<a id="notion-3eb1d46c18fc80d18204ff4615548b26"></a>

# 오늘 배운 내용 요약정리

<a id="notion-3eb1d46c18fc80218ebde50a4a138f88"></a>

## 문자 디바이스 번호

- `dev_t` = Major + Minor
- `MAJOR()` / `MINOR()` / `MKDEV()`
- `register_chrdev_region()` → 고정 Major
- `alloc_chrdev_region()` → Major 자동 할당
- `unregister_chrdev_region()` → 번호 반납

<a id="notion-3eb1d46c18fc80aa9763e2a6d66a1b34"></a>

## 문자 디바이스 등록

- `cdev` → 문자 디바이스 핵심 구조체
- `cdev_alloc()` → 생성
- `cdev_init()` → 초기화 + `file_operations` 연결
- `cdev_add()` → 문자 디바이스 등록
- `cdev_del()` → 문자 디바이스 해제

📝 `cdev_add()` → 문자 디바이스 등록

<a id="notion-3eb1d46c18fc80f9b8dec2c739c37b01"></a>

## Device File / `file_operations`

- Device File → 응용 프로그램 ↔ Driver 매개체
- Major → Driver 구분
- Minor → Driver 내부 Device 구분
- `file_operations` → File API와 Driver 함수 연결

```text
open()  → xxx_open()
read()  → xxx_read()
write() → xxx_write()
ioctl() → xxx_ioctl()
close() → xxx_release()
```

<a id="notion-3eb1d46c18fc804fb500ec85658dbe53"></a>

## `open()` / `release()`

- `open()` → 디바이스 확인·초기화
- `close()` → `release()` 호출
- `iminor(inode)` → Minor 번호 확인

<a id="notion-3eb1d46c18fc80618bccfe8f07614a59"></a>

## `read()` / `write()`

📝 **시험 ★ — 코드 수정 문제**

- `read()` → `copy_to_user()` → Kernel → User
- `write()` → `copy_from_user()` → User → Kernel
- 실패 → `EFAULT`
- `count`와 Buffer 크기 중 작은 값만 복사

<a id="notion-3eb1d46c18fc80ca92d1efa29c9a33ac"></a>

## `ioctl()`

- I/O Control
- `read/write` 외의 Device 설정·제어
- `cmd` → 수행할 제어 명령
- `arg` → 추가 데이터

<a id="notion-3eb1d46c18fc80b590d2f08d429a6b6c"></a>

### ioctl 번호

```text
dir | size | type | nr
```

- `dir` → 데이터 전달 방향
- `size` → 데이터 크기
- `type` → Driver 구분 코드
- `nr` → 명령 번호

<a id="notion-3eb1d46c18fc80cfb9a3e9ad40fb10bc"></a>

### ioctl Macro

- `_IO` → 데이터 없음
- `_IOR` → Driver → Application
- `_IOW` → Application → Driver
- `_IOWR` → 양방향

<a id="notion-3eb1d46c18fc80a5aaa5f2e739322f2a"></a>

## 전체 흐름

```text
mknod
→ Device File 생성

insmod
→ device_init()
→ Device Number 등록
→ cdev 등록

open()
→ device_open()

read()
→ device_read()
→ copy_to_user()

write()
→ device_write()
→ copy_from_user()

ioctl()
→ device_ioctl()

close()
→ device_release()

rmmod
→ device_exit()
→ cdev 해제
→ Device Number 반납
```
