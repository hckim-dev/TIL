# \[Linux\] 셸 스크립트와 빌드 툴체인 (GCC, Make, Library)

> 날짜: 2026-09-18
> 원본 노션: [링크](https://app.notion.com/p/Linux-GCC-Make-Library-3de1d46c18fc809eb6ead3a2d4495841)

<!-- notion-page-id: 3de1d46c18fc809eb6ead3a2d4495841 -->
<!-- notion-title: "[Linux] 셸 스크립트와 빌드 툴체인 (GCC, Make, Library)" -->

---

<a id="notion-3df1d46c18fc80e9acebe30db8faf4e6"></a>

### 1\. 쉘의 종류와 특징 &amp; 프로그래밍 언어 구분

<a id="notion-3df1d46c18fc80e69f9cdcc4881a8f3a"></a>

#### \[수업 내용 / 시험 범위\]

**1\) 쉘의 종류와 역할**

|  |  |  |
| --- | --- | --- |
| **쉘 종류** | **주요 용도 및 시스템 특징** | **실습 환경 매핑** |
| **`sh`** | **시스템용 표준 쉘**. 대개 다른 경량 쉘을 가리키는 **심볼릭 링크**로 구성됨 | `/bin/sh` -&gt; `dash`로 링크 |
| **`dash`** | 기능은 최소화되었으나 **실행 속도가 매우 빠르고 메모리 점유가 적음** -&gt; OS 부팅 및 시스템 스크립트 실행에 최적화 | Ubuntu 기본 시스템 쉘 |
| **`bash`** | 명령어 자동 완성, 히스토리 등 다양한 편의 기능을 제공하여 **사용자용 쉘**로 가장 널리 사용됨 | 기본 대화형 로그인 쉘 |

**2\) 컴파일 언어 vs 스크립트 언어 비교**

|  |  |  |
| --- | --- | --- |
| **비교 항목** | **컴파일 언어 (Compiled Language)** | **스크립트 언어 (Script Language)** |
| **대표 언어** | C, C++ 등 | 쉘 스크립트(Bash), Python 등 |
| **변환 과정** | 소스 코드 전체를 **컴파일러가 기계어로 일괄 번역** | **인터프리터가 한 줄씩 읽어가며 기계어로 즉각 변환** |
| **실행 주체** | **CPU**가 기계어 바이너리를 직접 실행 | **인터프리터 엔진**을 통해 간접 실행 |
| **실행 속도** | **빠름** | 상대적으로 **느림** |
| **시스템 종속성** | **종속적** (OS/CPU 아키텍처에 맞춰 재컴파일 필요) | **비종속적** (해당 인터프리터만 설치되어 있으면 동일 동작) |

**3\) 쉘 스크립트 기본 구조 및 실행 2단계**

- <strong>기본 코드 작성 (</strong><strong>`hello.sh`</strong><strong>)</strong>:

  ```bash
  #!/bin/bash

  # print messages
  echo "Hello! shell script"
  exit 0
  ```

  - `#!/bin/bash` (**샤뱅, Shebang**): 스크립트 맨 첫 줄에 작성하여 이 코드를 해석할 인터프리터의 절대 경로를 지정
  - `#`: 주석 (컴파일/실행 시 무시)
  - `echo`: 문자열을 화면(stdout)에 출력
  - `exit 0`: 정상 종료를 시스템에 알리는 종료 코드(0) 반환
- <strong>실행 절차 (코드 수필 및 실습 순서)</strong>:

  1. **실행 권한 부여**: `chmod a+x hello.sh` (파일 생성 직후 기본 상태에는 `x` 권한이 없으므로 필수)
  2. **현재 디렉터리 경로 명시 실행**: `./hello.sh`

<a id="notion-3df1d46c18fc80cc8775c371349d8482"></a>

#### \[시험 대비 핵심 포인트\]

- **`dash`** <strong>vs</strong> **`bash`** <strong>채점 기준</strong>: 시스템 쉘로 `dash`를 쓰는 이유를 묻는 주관식에서는 "빠른 실행 속도"와 "낮은 메모리 점유"라는 키워드가 반드시 들어가야 정답 처리됨.
- <strong>코드 수필 감점 방지 (3대 필수 체크)</strong>:

  1. **샤뱅 공백 금지**: `#! /bin/bash`처럼 `#!` 사이에 공백이 들어가거나 2번째 줄 이하에 작성하면 일반 주석으로 무시되어 인터프리터 지정 오류 발생.
  2. **경로 생략 금지**: 실행 시 `hello.sh`만 쓰면 명령어를 찾지 못함. 현재 디렉터리는 보안상 기본 검색 경로(`$PATH`)에 없으므로 <strong>반드시</strong> <strong>`./hello.sh`</strong>**로 작성**해야 함.
  3. **실행 권한 필수**: `umask` 기본값에 의해 새로 만든 스크립트는 `664` 또는 `644` 권한(`rw-r--r--`)이므로, 실행 전 **`chmod +x`** <strong>단계</strong>를 거치지 않고 바로 `./hello.sh`를 실행하면 `Permission denied` 에러가 발생함.

<a id="notion-3df1d46c18fc806cbb32f957e90892cd"></a>

#### 💡 \[선별 참고\]

- **권한 부여 없이 즉시 실행하는 방법**: 스크립트에 실행(`x`) 권한이 없더라도 `bash hello.sh`와 같이 인터프리터 프로그램 뒤에 파일 경로를 직접 인자로 넘기면 파일 읽기(`r`) 권한만으로도 즉시 실행할 수 있습니다.

<a id="notion-3df1d46c18fc805986f9e2c374c6c0f2"></a>

### 2\. 셸 변수 (Shell Variables)

<a id="notion-3df1d46c18fc80c79550cd45c260b5c8"></a>

#### \[수업 내용 / 시험 범위\]

**1\) 변수 정의 및 호출 기본 문법**

```abap
#!/bin/bash

name=linux
echo name: $name        # 출력: name: linux ($ 기호로 변수 값 참조)
echo name: ${name}      # 출력: name: linux ($name과 동일)

name=programming        # 기존 변수에 새로운 값 재할당 (덮어쓰기)
echo name: $name        # 출력: name: programming

echo course: $course    # 출력: course: (선언되지 않은 변수는 에러 없이 '빈 문자열'로 처리됨)
```

**2\) 변수 사용 핵심 규칙**

- **`=`** <strong>앞뒤 공백 절대 금지</strong>: `name = linux`처럼 띄어쓰기를 넣으면 셸은 `name`을 실행 명령어로, `=`와 `linux`를 명령어의 인자(Argument)로 취급하여 `command not found` 에러가 발생함.
- <strong>중괄호(</strong><strong>`${}`</strong><strong>) 명시의 필요성</strong>: 변수명 바로 뒤에 다른 문자나 언더바(`_`)가 이어질 때 변수명의 경계를 명확히 분리하기 위해 사용.

  - `echo "$name_backup"` -&gt; 셸이 `name_backup`이라는 별개의 변수를 찾으므로 빈 값 출력
  - `echo "${name}_backup"` -&gt; `linux_backup` 정상 출력

<a id="notion-3df1d46c18fc80e3b3ccfeae9ca3fb23"></a>

#### \[시험 대비 핵심 포인트\]

- <strong>코드 수필 0점 방지 (</strong><strong>`=`</strong> <strong>공백)</strong>: C언어 습관 때문에 `VAR = 10`처럼 공백을 넣는 실수가 가장 많이 감점됨. <strong>반드시</strong> <strong>`VAR=10`</strong>**으로 붙여 쓸 것**.
- <strong>변수 명명 규칙 (객관식/단답형)</strong>:

  - 영문 대소문자, 숫자, 언더바(`_`)만 사용 가능.
  - **숫자로 시작할 수 없음** (`1var=x`는 문법 에러).
  - 대소문자를 엄격히 구분함 (`NAME`과 `name`은 서로 다른 변수).
- **미선언 변수 처리**: 리눅스 셸은 선언되지 않은 변수를 참조해도 실행이 중단되지 않고 단순히 빈 문자열(Null)로 치환됨.

<a id="notion-3df1d46c18fc80abbe92db25efa34ba5"></a>

### 3\. 인용 부호 (Quoting: 큰따옴표 vs 작은따옴표)

<a id="notion-3df1d46c18fc808681affa5fa26cbb05"></a>

#### \[수업 내용 / 시험 범위\]

인용 부호는 공백을 묶어 하나의 인자로 유지하거나, 특수 기호(메타문자)의 확장 기능을 제어할 때 사용합니다.

```bash
#!/bin/bash
var=hello

touch aaa bbb           # 공백을 인자 구분자로 인식 -> 파일 2개('aaa', 'bbb') 생성
touch "aaa bbb"         # 큰따옴표가 공백을 하나로 묶음 -> 파일 1개('aaa bbb') 생성

# 1. 큰따옴표 ("", Weak Quoting)
echo "$var"             # 출력: hello (변수 치환 $ 동작 유지)
ls "/etc/issue*"        # 에러 발생 (와일드카드 * 기능이 무력화되어 글자 그대로 'issue*'인 파일 검색)

# 2. 작은따옴표 ('', Strong Quoting)
touch 'ccc ddd'         # 공백을 하나로 묶음 -> 파일 1개('ccc ddd') 생성
echo '$var'             # 출력: $var (모든 기호 무력화, $조차 문자 그대로 출력)
ls '/etc/issue*'        # 에러 발생 (* 기능 무력화)
```

**인용 부호 동작 비교**

|  |  |  |  |
| --- | --- | --- | --- |
| **기호** | **명칭** | **기능 설명** | **치환/확장 유지 여부** |
| **`""`** | **Weak Quoting**<br><br>(약한 인용) | • 공백을 포함해 하나의 인자로 묶음<br><br>• 와일드카드(`*`, `?`)는 일반 문자로 무력화 | <strong>`$`</strong><strong>,</strong> <strong>`` ` ``</strong><strong>,</strong> <strong>`\`</strong><strong>,</strong> **`!`** <strong>유지</strong><br><br>(변수 및 명령어 치환 실행됨) |
| **`''`** | **Strong Quoting**<br><br>(강한 인용) | • 공백을 포함해 하나의 인자로 묶음<br><br>• 내부의 **모든 특수 문자 기능을 100% 무력화** | **모두 무력화**<br><br>(글자 그대로 인식) |

<a id="notion-3df1d46c18fc80ea9d6afc1b8daa9192"></a>

#### \[시험 대비 핵심 포인트\]

- **와일드카드(Glob) 무력화**: `ls /etc/issue*`는 정상 동작하지만, `ls "/etc/issue*"`나 `ls '/etc/issue*'`는 가 와일드카드가 아닌 일반 특수문자로 취급되어 `No such file or directory` 에러가 발생함.
- **작은따옴표 내부 이스케이프 불가**: 작은따옴표(`''`) 안에서는 `\'`를 써도 이스케이프가 동작하지 않음. 작은따옴표 안에는 작은따옴표 자체를 포함할 수 없음.

<a id="notion-3df1d46c18fc80f59590e225cc75d280"></a>

### 4\. 이스케이프와 제어 문자 (Escaping &amp; Backslash Sequences)

<a id="notion-3df1d46c18fc8035b3c8f78da7ba4360"></a>

#### \[수업 내용 / 시험 범위\]

백슬래시(`\`)는 바로 뒤에 오는 단일 문자의 특수 기능을 무력화하거나, 특정 제어 문자를 표현할 때 사용합니다.

**1\) 특수 문자 이스케이프**

```bash
var=hello

echo \$var              # 출력: $var       ($의 변수 호출 기능 무력화)
echo \\$var             # 출력: \hello     (앞의 \가 뒤의 \를 문자화, $var는 정상 치환)
echo \"$var\"           # 출력: "hello"    (" 자체를 문자로 출력, $var는 정상 치환)
echo \'$var\'           # 출력: 'hello'    ('의 인용 기능이 꺼져 문자가 되고, $var는 치환됨)
echo \`pwd\`            # 출력: `pwd`      (백틱의 명령어 치환 기능 무력화)
```

<strong>2\) 따옴표 유무에 따른 일반 문자 앞</strong> **`\`** <strong>처리 차이</strong>

- <strong>따옴표 밖 (</strong><strong>`echo \a\b\c\d`</strong><strong>)</strong> -&gt; **`abcd`**

  - 셸 파서가 특별한 의미가 없는 일반 문자 앞의 `\`를 문법적으로 불필요한 것으로 판단해 자동 제거함.
- <strong>큰따옴표 안 (</strong><strong>`echo "\a\b\c\d"`</strong><strong>)</strong> -&gt; **`\a\b\c\d`**

  - 큰따옴표 안에서 `\`는 오직 <strong>`$`</strong><strong>,</strong> <strong>`` ` ``</strong><strong>,</strong> <strong>`"`</strong><strong>,</strong> <strong>`\`</strong><strong>, 개행문자</strong> 바로 앞에 올 때만 기능을 무력화하는 역할을 함. 그 외 일반 문자 앞에서는 `\`가 제거되지 않고 그대로 출력됨.

<strong>3\) 제어 문자 출력 (</strong><strong>`echo -e`</strong> <strong>vs</strong> <strong>`$'...'`</strong><strong>)</strong>

```bash
echo "111\n222\t333"    # 출력: 111\n222\t333 (기본 echo는 \n, \t를 줄바꿈/탭으로 해석하지 않음)
echo -e "111\n222\t333" # 출력: 줄바꿈과 탭 적용 (-e 옵션이 백슬래시 시퀀스를 활성화함)

# 16진수 ASCII 코드 변환
echo -e "\x31\x32\x33"  # 출력: 123 (0x31='1', 0x32='2', 0x33='3')
echo -e '\x31\x32\x33'  # 출력: 123 (작은따옴표로 감싸도 -e에 의해 해석됨)

# ANSI-C Quoting ($'...')
echo $'\x31\x32\x33'    # 출력: 123 (echo의 -e 옵션 없이도 셸 자체가 사전 해석)
```

<a id="notion-3df1d46c18fc80c583b7fb5da815033c"></a>

#### \[시험 대비 핵심 포인트\]

- **`echo -e`** <strong>옵션의 역할 (단답형/객관식)</strong>:

  - `echo`는 기본적으로 `\n`(줄바꿈), `\t`(탭)을 글자 그대로 출력함.
  - 백슬래시 제어 문자를 실제 줄바꿈/탭으로 동작하게 하려면 반드시 **`e`** <strong>(Enable interpretation of backslash escapes)</strong> 옵션을 명시해야 함.
- **`\'$var\'`** <strong>평가 순서 (주관식 단골 분석)</strong>:

  - `\`에 의해 `'`의 인용 기능이 꺼졌기 때문에 셸은 이를 문자 `'`로 인식함.
  - 따라서 가운데에 있는 `$var`는 인용구에 묶인 상태가 아니므로 정상적으로 변수 치환되어 `'hello'`가 출력됨.

<a id="notion-3df1d46c18fc808bb5a6df93f4a2c242"></a>

#### 💡 \[선별 참고\]

- **`echo -e`** <strong>대신</strong> **`printf`** <strong>권장 이유</strong>: 시스템 쉘(`dash`, `sh`)이나 다른 유닉스 환경에서는 `echo -e` 동작이 표준화되어 있지 않아 시스템마다 다르게 동작할 수 있습니다. C 언어 스타일의 완벽한 이스케이프 포맷팅이 필요할 때는 이식성이 높은 `printf "%s\n" "hello"` 사용이 권장됩니다.

<a id="notion-3df1d46c18fc80179f5dfcd95de113c9"></a>

### 5\. 변수 내보내기 (`export`) 및 지역 vs 환경 변수

<a id="notion-3df1d46c18fc8090b8b9c4f63e82ede4"></a>

#### \[수업 내용 / 시험 범위\]

**1\) 지역 변수 vs 환경 변수**

- <strong>지역 변수 (Local Variable)</strong>: 선언된 현재 셸 세션 내부에서만 유효하며, 실행되는 자식 프로세스(서브셸, 외부 스크립트)로 전달되지 않는 변수
- <strong>환경 변수 (Environment Variable)</strong>: `export` 명령을 통해 등록되며, 현재 셸뿐만 아니라 현재 셸에서 파생되는 **모든 자식 프로세스(스크립트 포함)로 복사 및 상속**되는 변수

<strong>2\) 변수 내보내기 (</strong><strong>`export`</strong><strong>) 동작 실습</strong>

```bash
# var_export.sh
#!/bin/bash
echo name: $name
echo course: $course
```

```bash
$ export name=linux     # name을 환경 변수로 등록
$ course=expert         # course를 지역 변수로 선언
$ ./var_export.sh
name: linux             # 자식 스크립트로 전달되어 출력
course:                 # 지역 변수이므로 자식에게 전달되지 않아 빈 값 출력

$ name=programming      # 이미 export된 변수는 재할당해도 환경 변수 속성 유지
$ export course         # 기존 지역 변수를 환경 변수로 승격
$ ./var_export.sh
name: programming
course: expert          # 둘 다 정상 출력
```

**3\) 변수 확인 및 제거 명령어**

|  |  |  |
| --- | --- | --- |
| **명령어** | **대상 범위** | **특징 및 용도** |
| **`set`** | **모든 변수 + 함수** | 지역 변수, 환경 변수, 셸 함수 전체 출력 (양이 방대하므로 `set \| more`로 확인) |
| **`env`** (또는 `printenv`) | **환경 변수만** | 자식 프로세스로 상속되는 환경 변수 목록만 출력 |
| **`unset <변수명>`** | 변수 해제 | 지정한 변수를 메모리에서 완전히 삭제 (지역/환경 변수 모두 제거) |

**4\) 주요 시스템 변수**

- <strong>주요 환경 변수 (대문자)</strong>:

  - `HOME`: 현재 사용자의 홈 디렉터리 절대 경로
  - `PATH`: 실행 파일을 검색할 디렉터리 경로 목록 (콜론 `:` 구분)
  - `USER`: 현재 로그인한 사용자 계정명
  - `PWD`: 현재 작업 디렉터리 경로
- <strong>주요 셸 변수 (셸이 자동 생성하는 내부 변수)</strong>:

  - `PS1`: 기본 명령 프롬프트 형태 정의 (`aidl@ubuntu:~$ `)
  - `PS2`: 2차 프롬프트 (명령어가 다음 줄로 이어질 때 표시되는 `>`)
  - `RANDOM`: 호출할 때마다 $0 \sim 32767$ 사이의 정수형 난수 반환
  - `UID`: 현재 사용자의 고유 User ID 번호 (root는 0)
  - `PPID`: 현재 셸의 부모 프로세스 PID (Parent Process ID)

<a id="notion-3df1d46c18fc8033b984efc8e6cca305"></a>

### 6\. 스크립트 실행 방식과 상속 범위 (`./` vs `source`)

<a id="notion-3df1d46c18fc80939ab0c13097e449e8"></a>

#### \[수업 내용 / 시험 범위\]

```bash
# var_source.sh
#!/bin/bash
lvar="local"
export gvar="global"
```

<strong>1\) 일반 실행 방식 (</strong><strong>`./var_source.sh`</strong><strong>)</strong>

```bash
$ ./var_source.sh
$ echo $lvar            # 빈 값 (출력 없음)
$ echo $gvar            # 빈 값 (출력 없음)
```

- **원리**: 셸은 스크립트를 실행할 때 새로운 자식 프로세스(Subshell)를 Fork(생성)하여 실행함.
- 스크립트 실행이 끝나면 해당 자식 프로세스는 소멸하므로, 스크립트 내부에서 선언된 변수(`lvar`, `gvar`)도 함께 메모리에서 사라짐.
- **핵심 대원칙**: **"자식 프로세스는 부모 프로세스의 환경을 변경할 수 없다."**

<strong>2\) 소스 실행 방식 (</strong><strong>`source ./var_source.sh`</strong> <strong>또는</strong> <strong>`. ./var_source.sh`</strong><strong>)</strong>

```bash
$ source ./var_source.sh    # 또는 . ./var_source.sh (점 명령어)
$ echo $lvar                # 출력: local
$ echo $gvar                # 출력: global
$ env | grep gvar
gvar=global                 # 현재 셸의 환경 변수로 정상 등록 확인
```

- **원리**: 새 자식 프로세스를 띄우지 않고, **현재 부모 셸의 컨텍스트에서 스크립트 코드를 직접 한 줄씩 읽어 실행**함.
- 따라서 스크립트 안에서 선언된 지역 변수와 `export`된 환경 변수가 **현재 셸에 그대로 영구 적용**됨.

<a id="notion-3df1d46c18fc806c8d3fcdb5ca27db3e"></a>

#### \[시험 대비 핵심 포인트\] (★ 킬러 문항 대비)

- <strong>`export`</strong><strong>의 일방향성 (부모 -&gt; 자식 O / 자식 -&gt; 부모 X)</strong>:

  - 부모 셸에서 `export`한 변수는 자식 스크립트로 상속되지만, <strong>자식 스크립트 안에서 아무리</strong> <strong>`export`</strong>**를 해도 스크립트가 종료되면 부모 셸에는 절대 반영되지 않음**.
- <strong>한 번</strong> <strong>`export`</strong>**된 변수의 수정**:

  - 처음에 `export name=linux`로 선언한 후, 나중에 `name=programming`처럼 `export` 키워드 없이 단순 값만 변경해도 **환경 변수 속성은 그대로 유지**되어 자식에게 변경된 값이 전달됨.
- **`./script.sh`** <strong>vs</strong> **`source script.sh`** <strong>(코드 수필 및 서술형 1순위)</strong>:

|  |  |  |
| --- | --- | --- |
| **비교 항목** | **./script.sh (일반 실행)** | **source script.sh 또는 . script.sh** |
| **프로세스 생성** | **새로운 자식 프로세스(Subshell)** 생성 | **현재 셸 프로세스** 내부에서 직접 실행 |
| **변수 반영 여부** | 스크립트 종료 시 내부 변수 **소멸** (부모 셸 영향 없음) | 스크립트 내 변수/환경설정이 **현재 셸에 유지됨** |
| **필요 파일 권한** | 실행 권한(<strong>`x`</strong>) 필수 (`chmod +x`) | <strong>읽기 권한(</strong><strong>`r`</strong><strong>)만 있으면 실행 가능</strong> (`x` 없어도 됨) |

- **`set`** <strong>vs</strong> **`env`** <strong>구분</strong>:

  - 환경 변수만 확인하려면 `env`.
  - 지역 변수와 셸 함수까지 모두 확인하려면 `set`.

<a id="notion-3df1d46c18fc8066bb1fc46ad4a4f71f"></a>

#### 💡 \[선별 참고\]

- <strong>`source ~/.bashrc`</strong>**를 쓰는 이유**: 터미널 설정 파일(`.bashrc`)을 수정한 후 터미널 창을 닫았다 다시 열지 않고, 현재 열려 있는 셸에 바뀐 환경 변수와 별칭(alias)을 즉시 적용하기 위해 `source`(또는 `.`) 명령을 사용합니다.

<a id="notion-3df1d46c18fc80c184dfe185c598f664"></a>

### 7\. 셸 특수 변수 (Special Variables)

<a id="notion-3df1d46c18fc80a69a07d1d8d688f40b"></a>

#### \[수업 내용 / 시험 범위\]

스크립트 실행 시 전달되는 명령행 인자(인수)와 프로세스 상태 정보를 담고 있는 예약된 변수입니다.

<strong>1\) 특수 변수 실습 스크립트 (</strong><strong>`var_sp.sh`</strong><strong>)</strong>

```bash
#!/bin/bash

echo '$#': $#      # 전달된 인자의 총 개수 (스크립트명 $0 제외)
echo '$0': $0      # 실행된 스크립트의 파일명/경로
echo '$1': $1      # 1번째 인자
echo '$2': $2      # 2번째 인자

echo '$$': $$      # 현재 실행 중인 스크립트 프로세스의 PID

echo '$?': $?      # 직전 명령의 종료 상태 코드 (성공 시 0)

ls xxxx            # 존재하지 않는 파일 조회 -> 에러 발생
echo '$?': $?      # 에러 종료 상태 코드 출력 (2)
```

<strong>2\) 실행 결과 분석 (</strong><strong>`./var_sp.sh 1st 2nd`</strong><strong>)</strong>

```text
$#: 2
$0: ./var_sp.sh
$1: 1st
$2: 2nd
$$: 15324          # (실행 시점의 실제 PID 출력)
$?: 0              # 직전 echo 명령이 정상 실행되었으므로 0
ls: cannot access 'xxxx': No such file or directory
$?: 2              # ls 에러로 인해 0이 아닌 비정상 종료 코드(2) 출력
```

**3\) 주요 특수 변수 정리**

|  |  |  |
| --- | --- | --- |
| **변수** | **명칭 및 의미** | **예시 (./var\_sp.sh 1st 2nd)** |
| **`$0`** | 실행된 스크립트의 이름 또는 실행 경로 | `./var_sp.sh` |
| <strong>`$1`</strong><strong>,</strong> <strong>`$2`</strong><strong>...</strong> | 위치 매개변수 (Positional Arguments, 인자 순번) | `$1` = `1st`, `$2` = `2nd` |
| **`$#`** | 전달된 위치 매개변수의 **총 개수** (`$0` 제외) | `2` |
| **`$$`** | 현재 스크립트가 동작 중인 **프로세스 ID (PID)** | 시스템 할당 정수 (예: `15324`) |
| **`$?`** | **직전 실행된 명령어의 리턴값 (종료 상태 코드)** | 성공 시 `0`, 실패 시 `1~255` (위 실습에선 `2`) |

<a id="notion-3df1d46c18fc8080ac37e714fae8db5a"></a>

#### \[시험 대비 핵심 포인트\]

- **`$?`** <strong>리턴값 판별 (단답형/코드 수필 1순위)</strong>:

  - <strong>`0`</strong>: 정상 종료(성공)
  - <strong>`0이 아닌 값 (1~255)`</strong>: 비정상 종료(오류 발생)
  - 조건문 `if [ $? -eq 0 ]; then` 형태로 직전 명령의 성공/실패를 검증하는 스크립트 패턴이 빈출됨.
- **`$#`** <strong>카운트 범위 주의</strong>:

  - `$#`는 스크립트 이름(`$0`)을 포함하지 않고, 오직 뒤에 전달된 인자의 개수(`$1`부터)만 센다는 점이 객관식 함정으로 자주 출제됨.
- <strong>단일 인용구(</strong><strong>`''`</strong><strong>)와 변수 치환의 결합</strong>:

  - `echo '$#': $#` 코드에서 앞의 `'$#'`는 작은따옴표로 묶여 글자 그대로 `$#`가 출력되고, 뒤의 `$#`는 따옴표가 없어 실제 인자 개수로 치환됨 (Quoting 원리 복합 문항).

<a id="notion-3df1d46c18fc80dea7eee7e8e92fa25f"></a>

#### 💡 \[선별 참고\]

- <strong>10번째 이상의 매개변수 표기 (</strong><strong>`${10}`</strong><strong>)</strong>: 인자가 10개 이상일 때 `$10`으로 작성하면 셸은 `$1`의 값 뒤에 문자 `0`을 붙인 것으로 잘못 해석합니다. 따라서 두 자리 이상의 위치 매개변수는 반드시 `${10}`, `${11}`처럼 중괄호로 묶어야 합니다.

<a id="notion-3df1d46c18fc8073a146c6e49b639ab0"></a>

### 8\. GNU 툴체인(Toolchain)과 C 프로그램 빌드 과정

<a id="notion-3df1d46c18fc8007a1a4fd236547d2ca"></a>

#### \[수업 내용 / 시험 범위\]

**1\) 툴체인(Toolchain)의 개념**

- **개념**: 소스 코드(`.c`)를 컴퓨터 CPU가 실행할 수 있는 바이너리 실행 파일로 만들기 위해 사슬(Chain)처럼 엮어 사용하는 **모든 개발 도구들의 묶음**
- **대표 종류**:

  - **GNU 툴체인**: 리눅스 표준 개발 환경 (`gcc`, `gdb`, `glibc`, `binutils` 등)
  - **Clang / LLVM**: 빠른 컴파일 속도와 모듈식 설계가 특징인 최신 대안 툴체인

**2\) C 프로그램 4단계 빌드 과정 (★ 단골 출제)**

우리가 터미널에서 `gcc`를 실행하면 보이지 않는 뒷단에서 4단계 도구들이 순서대로 동작합니다. `gcc`는 컴파일러 본체가 아니라, 이 과정 전체를 총괄 지휘하는 관리자(Driver)입니다.

```text
[ 소스 코드 (.c) ]
      ↓  cpp (선행처리기)
[ 선행처리 파일 (.i) ]
      ↓  cc1 (C 컴파일러)
[ 어셈블리어 파일 (.s) ]
      ↓  as (어셈블러)
[ 오브젝트 파일 (.o) ]
      ↓  ld (링커) + 라이브러리
[ 최종 실행 파일 (ELF) ]
```

|  |  |  |  |
| --- | --- | --- | --- |
| **단계** | **담당 도구 (명령)** | **입력 → 출력** | **주요 작업 및 역할** |
| **1\. 선행처리**<br><br>(Preprocess) | **`cpp`**<br><br>(C Preprocessor) | `.c` -&gt; **`.i`** | • `#include`로 선언된 헤더 파일 내용 복사<br><br>• `#define` 매크로 치환 및 코드 내 주석 제거 |
| **2\. 컴파일**<br><br>(Compile) | **`cc1`**<br><br>(C Compiler) | `.i` -&gt; **`.s`** | • C 언어 문법 검사<br><br>• 해당 CPU 아키텍처 전용 \*\*어셈블리어(기호 언어)\*\*로 번역 |
| **3\. 어셈블**<br><br>(Assemble) | **`as`**<br><br>(Assembler) | `.s` -&gt; **`.o`** | • 어셈블리어를 기계어(0과 1)로 변환하여 **오브젝트 파일(Object File)** 생성 |
| **4\. 링크**<br><br>(Link) | **`ld`**<br><br>(Linker) | `.o` -&gt; **실행 파일** | • 여러 오브젝트 파일과 C 표준 라이브러리(libc)를 하나로 묶음<br><br>• 최종 리눅스 표준 실행 포맷인 **ELF(Executable and Linkable Format)** 파일 완성 |

**3\) Native 툴체인 vs Cross 툴체인 비교**

|  |  |  |
| --- | --- | --- |
| **구분** | **Native(네이티브) 툴체인** | **Cross(크로스) 툴체인** |
| **정의** | **빌드하는 기기(Host)와 실행 기기(Target)가 동일** | **빌드하는 기기(Host)와 실행 기기(Target)가 다름** |
| **예시** | • x86 PC에서 빌드 -&gt; x86 PC에서 실행<br><br>• 젯슨 오린 나노 보드 안에서 직접 빌드 -&gt; 젯슨에서 실행 | • 고성능 PC(x86)에서 빌드 -&gt; 임베디드 보드(ARM)에서 실행 |
| **사용 이유** | 환경 설정이 간단하고 직관적임 | **대부분의 임베디드 시스템에서 채택**<br><br>(보드의 CPU 성능이 낮고 메모리·저장소가 부족하여 빌드가 매우 느리기 때문) |
| **확보 방법** | 배포판 기본 패키지(`gcc`) 설치 | ① 사전 빌드된 툴체인 다운로드<br><br>② **Buildroot, Yocto** 등 빌드 시스템 활용<br><br>③ 툴체인 소스 코드를 직접 컴파일 |

**4\) 다중 소스 파일 빌드 실습 분석**

- **소스 코드**:

  - `func.c`: 실제 동작하는 `func()` 함수 구현
- **컴파일 명령어:**

  - `main.c`: `extern void func(void);`로 외부 파일에 있는 함수임을 컴파일러에 선언하고 호출

  ```bash
  $ aarch64-linux-gnu-gcc func.c main.c
  $ ./a.out
  main: Hello!
  func: Hello!
  ```
- **동작 원리**:

  - `aarch64-linux-gnu-gcc`: 64비트 ARM(`aarch64`) 타겟으로 크로스 컴파일하는 GNU GCC 컴파일러
  - 소스 파일 2개를 한 번에 넘기면 내부적으로 각각 `.o` 파일을 만든 뒤, 링커(`ld`)가 `main`에서 부른 `func()`의 실제 메모리 주소를 연결하여 실행 파일 생성
  - <strong>출력 파일명을 지정하지 않으면 기본 실행 파일 이름은 항상</strong> <strong>`a.out`</strong>**으로 생성됨**

<a id="notion-3df1d46c18fc80ff965dffe6b292aec7"></a>

#### \[시험 대비 핵심 포인트\]

- <strong>4단계 빌드 순서와 파일 확장자 짝짓기 (객관식/단답형 1순위)</strong>:

  - 확장자 변화: **`.c`** <strong>-&gt;</strong> **`.i`** <strong>-&gt;</strong> **`.s`** <strong>-&gt;</strong> **`.o`** <strong>-&gt; ELF 실행 파일</strong>
  - 각 단계 도구 연결: 선행처리(<strong>`cpp`</strong>) -&gt; 컴파일(<strong>`cc1`</strong>) -&gt; 어셈블(<strong>`as`</strong>) -&gt; 링크(<strong>`ld`</strong>)
- <strong>`gcc`</strong>**의 정확한 역할**:

  - "gcc는 컴파일만 수행한다"는 오답. "선행처리, 컴파일, 어셈블, 링크 전체 과정을 순차적으로 지휘하는 드라이버"가 정답.
- **Native vs Cross 채점 기준**:

  - Host(빌드 기기)와 Target(실행 기기)의 **CPU 아키텍처 일치 여부**를 묻는 문제가 빈출됨.
  - `aarch64-linux-gnu-gcc`처럼 이름 앞에 아키텍처 접두사(Prefix)가 붙어 있으면 Cross 컴파일러임.

**5\) GCC 주요 단계 제어 및 출력 옵션**

|  |  |  |  |
| --- | --- | --- | --- |
| **옵션** | **진행 범위 ("\~단계까지")** | **최종 생성 파일** | **설명** |
| **`-E`** | **선행처리(Preprocess)까지** | 표준 출력 (또는 `.i`) | 매크로 치환 및 헤더 복사까지만 진행하고 화면에 출력 |
| **`-S`** | **컴파일(Compile)까지** | **`.s`** | C 코드를 어셈블리어 파일까지만 변환 |
| **`-c`** | **어셈블(Assemble)까지** | **`.o`** | 기계어 오브젝트 파일까지만 생성 (링크 단계 미수행) |
| *(미사용)* | **링크(Link)까지 (전 과정)** | **실행 파일** (기본 `a.out`) | 선행처리부터 링크까지 전체 단계를 완벽히 끝마침 |
| **`-o <파일>`** | — | 사용자가 지정한 이름 | 최종 결과물(실행 파일 또는 오브젝트 파일)의 **출력 파일명을 직접 지정** |
| **`-save-temps`** | 전 과정 | `.i`, `.s`, `.o`, 실행 파일 | 컴파일 중 생성되는 **모든 중간 임시 파일들을 지우지 않고 전부 저장** |

**6\) 핵심 개념: 옵션은 단일 실행이 아니라 "\~단계까지" 순차 진행**

- GCC의 단계 옵션은 특정 단계만 뚝 떼어 실행하는 것이 아니라, 맨 처음(선행처리)부터 **해당 옵션이 가리키는 단계 "까지" 순서대로 실행한 뒤 멈추는 것**임.

  - **예시**: `gcc -c main.c`
  - -&gt; 선행처리(cpp) -&gt; 컴파일(cc1) -&gt; 어셈블(as) **단계까지 순차 진행**된 후, 링크(ld)를 실행하지 않고 멈춰서 `main.o`를 남김.

**7\) 실습 명령어 상세 분석**

- <strong>오브젝트 파일 이름 변경 생성 (</strong><strong>`c`</strong> <strong>\+</strong> <strong>`o`</strong><strong>)</strong>:

  ```bash
  $ aarch64-linux-gnu-gcc -c main.c -o temp.o
  ```

  - `main.c`를 어셈블 단계까지 빌드함.
  - 기본 규칙대로라면 `main.o`가 생성되어야 하지만, `o temp.o` 옵션을 지정했으므로 최종 결과물이 `temp.o`라는 이름으로 생성됨.
- <strong>오브젝트 파일들을 링크하여 실행 파일 생성 (</strong><strong>`o`</strong><strong>)</strong>:

  ```bash
  $ aarch64-linux-gnu-gcc -o hello main.o func.o
  $ ./hello
  main: Hello!
  func: Hello!
  ```

  - 이미 컴파일이 완료된 `main.o`와 `func.o`를 링커(`ld`)를 통해 하나로 결합함.
  - `o hello`를 주었으므로 기본값인 `a.out` 대신 `hello`라는 이름의 실행 파일이 완성됨.

<a id="notion-3df1d46c18fc807e88fff3c5ad8bb193"></a>

#### \[시험 대비 핵심 포인트\] (★ 무조건 출제 영역)

- **`o`** <strong>옵션 작성 시 치명적 감점 주의 (코드 수필 1순위)</strong>:

  - `o` 바로 뒤에는 반드시 '새로 만들어질 출력 파일 이름'이 와야 함.
  - **오답 함정**: `gcc -o main.c main.o` 처럼 작성하면 소스 파일인 `main.c`가 덮어씌워져 원본 코드가 완전히 날아가므로 시험 채점 시 즉시 0점 처리됨.
  - **올바른 순서**: `gcc main.c -o myprog` 또는 `gcc -o myprog main.c`
- **`c`** <strong>옵션의 역할 서술 (단답형/주관식 단골)</strong>:

  - "링크(Link)를 수행하지 않고 목적 파일(Object File, `.o`)까지만 생성하고자 할 때 사용하는 옵션"으로 정확히 서술해야 함.
- <strong>`save-temps`</strong><strong>의 기능 (객관식)</strong>:

  - 빌드 과정 중 내부적으로 자동 삭제되는 중간 산출물(`.i`, `.s`, `.o`)을 현재 디렉터리에 그대로 남겨 확인/디버깅할 수 있게 해주는 옵션.
- **출력 옵션 미지정 시 기본 파일명**:

  - 최종 링크 단계까지 수행할 때 `o` 옵션을 생략하면 실행 파일 이름은 무조건 `a.out`으로 고정됨.

<a id="notion-3df1d46c18fc80e1ac8eef3da32719cf"></a>

### 9\. 빌드 자동화 도구 (GNU make &amp; Makefile)

<a id="notion-3df1d46c18fc8047a458cba0176735ab"></a>

#### \[수업 내용 / 시험 범위\]

**1\) GNU make와 Makefile의 개념**

- <strong>`make`</strong>: 소스 코드 파일 간의 의존성(Dependency)을 추적하여, **수정된 파일만 선별적으로 다시 컴파일(증분 빌드)해 주는 빌드 자동화 도구**
- <strong>`Makefile`</strong>: 프로젝트를 빌드하기 위한 규칙(타겟, 의존 파일, 실행 명령어)을 기술해 둔 설정 파일

**2\) Makefile의 기본 규칙 구조 (Rule)**

```makefile
타겟(Target): 의존파일들(Prerequisites/Dependencies)
	[TAB] 명령(Commands)
```

- <strong>타겟 (Target)</strong>: 규칙을 통해 생성하고자 하는 결과물 (주로 실행 파일, 오브젝트 파일) 또는 작업 이름 (예: `clean`)
- <strong>의존 파일 (Dependencies)</strong>: 타겟을 생성하기 위해 사전에 반드시 존재하거나 먼저 만들어져야 하는 입력 파일들
- <strong>명령 (Commands)</strong>: 타겟을 만들기 위해 셸에서 실제로 실행할 명령어

  - **문법 제약**: <strong>명령어 앞의 들여쓰기는 반드시</strong> **`TAB`** <strong>문자</strong>여야 함 (스페이스 공백 사용 시 문법 에러 발생)
  - **`@`** <strong>접두사</strong>: 명령어 맨 앞에 `@`를 붙이면, 터미널에 명령어 텍스트 자체를 출력하지 않고 **명령어의 실행 결과(출력값)만 표시**함 (명령어 에코 억제)

**3\) 실행 방식 및 타겟 지정**

- **`make`** <strong>(타겟 미지정)</strong>: Makefile 내에 정의된 맨 첫 번째 규칙(Default Target)을 자동으로 실행함 (관례상 `all`을 첫 타겟으로 둠)
- **`make <타겟명>`** <strong>(타겟 지정)</strong>: 지정한 특정 타겟의 규칙만 찾아서 실행함 (예: `make clean`, `make hello`)

**4\) 실습 Makefile 분석 및 실행 순서**

```makefile
all: hello
	@echo "build finished!"

hello: main.o func.o
	aarch64-linux-gnu-gcc -o hello main.o func.o

main.o: main.c
	aarch64-linux-gnu-gcc -c main.c

func.o: func.c
	aarch64-linux-gnu-gcc -c func.c

clean:
	@rm -f hello main.o func.o
	@echo "clean finished!"
```

**의존성 검사 순서 vs 실제 명령어 실행 순서 (★ 구분 필수)**

- <strong>의존성 탐색 순서 (Top-Down)</strong>:

  `all` 확인 -&gt; `hello` 필요 -&gt; `main.o`, `func.o` 필요 -&gt; `main.c`, `func.c` 확인
- <strong>실제 명령어 실행 순서 (Bottom-Up)</strong>:

  하위 의존 파일이 먼저 만들어져야 상위 타겟을 빌드할 수 있으므로 **역순으로 실행**됨.

  1. `main.o` 생성 명령 실행 (`aarch64-linux-gnu-gcc -c main.c`)
  2. `func.o` 생성 명령 실행 (`aarch64-linux-gnu-gcc -c func.c`)
  3. `hello` 링크 명령 실행 (`aarch64-linux-gnu-gcc -o hello main.o func.o`)
  4. `all` 명령 실행 (`build finished!` 출력)

**5\) ★ 타임스탬프 기반 증분 빌드 (Incremental Build) 원리**

`make`는 파일의 최종 수정 시간(<strong>`mtime`</strong><strong>, Modification Time</strong>)을 비교하여 빌드 수행 여부를 결정합니다.

- <strong>명령이 건너뛰어지는 경우 (Up to date)</strong>:

  - 타겟 파일과 의존 파일이 모두 디스크에 실제로 존재하고,
  - **타겟 파일의 수정 시간이 모든 의존 파일의 수정 시간보다 최신(Newer)인 경우**
  - -&gt; "변경된 내용이 없다"고 판단하여 해당 명령을 실행하지 않음 (`make: 'hello' is up to date.`)
- **명령이 반드시 실행되는 경우**:

  - 타겟 파일이 아예 존재하지 않는 경우
  - **의존 파일 중 단 하나라도 타겟 파일보다 수정 시간이 최신인 경우** (코드가 수정됨)

<a id="notion-3df1d46c18fc80109154f19eea053b05"></a>

#### \[시험 대비 핵심 포인트\]

- <strong>코드 수필 0점 방지 (</strong><strong>`TAB`</strong> <strong>키)</strong>:

  - Makefile에서 명령어 라인 시작에 스페이스바(Space)를 사용하면 make 실행 시 **`Makefile:...: *** missing separator. Stop.`** 에러가 발생함. **반드시 TAB 키로 들여쓰기**를 해야 함.
- <strong>증분 빌드 판별 기준 (단답형/서술형 1순위)</strong>:

  - make가 파일 수정 여부를 판단하는 근거는 파일의 최종 수정 타임스탬프(`mtime`)임.
  - 의존 파일(`.c`)의 `mtime`이 타겟 파일(`.o` 또는 실행 파일)의 `mtime`보다 뒤(최신)이면 재컴파일을 수행함.
- **실행 순서 채점 기준**:

  - 의존성 트리를 파악하는 순서와 터미널에서 실제로 컴파일 명령이 수행되는 순서는 반대(가장 하위 의존 파일부터 상위 타겟 순으로 빌드)라는 점을 정확히 기술해야 감점을 피할 수 있음.
- **`@`** <strong>기호의 기능 (단답형)</strong>:

  - Makefile 내에서 실행되는 명령어 자체의 출력을 화면에 숨기고, 명령어 실행 결과만 깔끔하게 표시하고자 할 때 명령어 맨 앞에 붙이는 특수 기호.

<a id="notion-3df1d46c18fc80529ae5e6076cf68ca7"></a>

#### 💡 \[선별 참고\]

- **`.PHONY`** <strong>타겟 (가상 타겟 선언)</strong>:

  - `clean`처럼 실제 생성되는 파일 이름이 아닌 작업용 타겟의 경우, 만약 디렉터리 안에 우연히 이름이 `clean`인 실제 파일이 생성되면 `make clean` 실행 시 "clean is up to date"가 뜨며 명령이 동작하지 않습니다.
  - 이를 방지하기 위해 파일이 아님을 명시하는 **`.PHONY: clean all`** 선언을 상단에 적어주는 것이 실무 표준입니다.

<a id="notion-3df1d46c18fc802ab860e6e6126888ea"></a>

### 10\. Makefile 매크로(Macro)와 패턴 규칙(Pattern Rule)

<a id="notion-3df1d46c18fc8059a957ffdf4014ab81"></a>

#### \[수업 내용 / 시험 범위\]

**1\) 매크로(Macro)의 개념과 도입 목적**

- **개념**: Makefile 내에서 반복적으로 사용되는 컴파일러 명령어, 옵션, 파일 목록 등을 변수 형태로 정의하여 사용하는 기능
- **장점**:

  - 빌드 설정(컴파일러 변경, 타겟 아키텍처 변경, 컴파일 플래그 추가 등)을 상단에서 일괄 제어 가능
  - 코드 중복을 줄이고 유지보수성 및 가독성을 대폭 향상

**2\) 사용자 정의 매크로 (User-Defined Macro)**

- <strong>정의(할당)</strong>: `매크로_이름 = 값` (관례적으로 대문자 사용)
- <strong>참조(호출)</strong>: `$(매크로_이름)` 형태로 괄호로 감싸서 사용

|  |  |  |
| --- | --- | --- |
| **관례적 매크로명** | **표준 용도** | **실습 예시** |
| **`CC`** | C 컴파일러 프로그램 | `CC = aarch64-linux-gnu-gcc` (또는 `gcc`) |
| **`CFLAGS`** | C 컴파일 옵션 (Compile Flags) | `CFLAGS = -c` (또는 `-Wall -O2`) |
| **`TARGET`** | 최종 생성할 실행 파일 이름 | `TARGET = hello` |
| **`OBJS`** | 링크에 필요한 오브젝트 파일(`.o`) 목록 | `OBJS = main.o func.o` |

**3\) 내장 매크로 (자동 변수, Automatic Variables)**

규칙(Rule) 내의 명령(Commands) 블록에서 타겟과 의존 파일의 이름을 자동으로 가져와 치환해 주는 특수 예약 변수입니다.

|  |  |  |
| --- | --- | --- |
| **자동 변수** | **의미 및 역할** | **실습 코드 매핑 예시** |
| **`$@`** | \*\*현재 타겟(Target)\*\*의 파일 이름 | `$(TARGET): ...` 에서 `hello` |
| **`$<`** | 의존 파일들 중 **첫 번째 의존 파일(First Prerequisite)** | `main.o: main.c` 에서 `main.c` |
| **`$^`** | 현재 타겟이 의존하는 **모든 의존 파일 목록** (공백 구분) | `$(TARGET): $(OBJS)` 에서 `main.o func.o` |
| **`$?`** | 타겟보다 **최신인(수정된) 의존 파일들**의 목록 | 갱신된 파일만 다시 링크/처리할 때 사용 |
| **`$*`** | 패턴 규칙에서 <strong>`%`</strong>**에 일치하는 줄기(Stem)** 문자열 | `%.o: %.c`에서 파일명 부분 (확장자 제외) |

**4\) 매크로 및 패턴 규칙 적용 코드 분석**

```makefile
TARGET = hello
OBJS = main.o func.o
CC = aarch64-linux-gnu-gcc
CFLAGS = -c

all: $(TARGET)
	@echo "build finished!"

# [1] 실행 파일 생성 규칙 ($@ 사용)
$(TARGET): $(OBJS)
	$(CC) -o $@ $^

# [2] 패턴 규칙 (%.o: %.c 및 $< 사용)
%.o: %.c
	$(CC) $(CFLAGS) $<

clean:
	@rm -f $(TARGET) $(OBJS)
	@echo "clean finished!"
```

- **`$(TARGET): $(OBJS)`** <strong>분석</strong>:

  - `$(CC) -o $@ $(OBJS)` -&gt; `aarch64-linux-gnu-gcc -o hello main.o func.o`로 치환됨 (`$@`는 타겟인 `hello`를 의미).
- <strong>패턴 규칙 (</strong><strong>`%.o: %.c`</strong><strong>) 분석</strong>:

  - **`%`** <strong>(Pattern Matching)</strong>: 와일드카드 역할을 수행하며, 양변의 동일한 파일명(Stem)을 1:1로 매칭함.
  - `main.o`를 만들 때는 `main.c`를 찾아 매칭하고, `func.o`를 만들 때는 `func.c`를 찾아 매칭함.
  - `$<`는 첫 번째 의존 파일이므로, `main.o` 작업 시에는 `main.c`, `func.o` 작업 시에는 `func.c`로 자동 치환됨.
  - **효과**: 소스 파일이 수십 개로 늘어나더라도 `main.o: main.c`, `func.o: func.c` 처럼 규칙을 일일이 나열할 필요 없이 **단 2줄의 패턴 규칙으로 통합 처리 가능**.

<a id="notion-3df1d46c18fc804aa278c6f295039411"></a>

#### \[시험 대비 핵심 포인트\]

- <strong>내장 매크로 3대장 구별 및 빈칸 채우기 (시험 출제 1순위)</strong>:

  - <strong>`$@`</strong>: 타겟 이름 (**T**arget -&gt; 골뱅이 `@`)
  - <strong>`$<`</strong>: 첫 번째 의존 파일 (왼쪽 화살표처럼 첫 번째 입력을 가리킴)
  - <strong>`$^`</strong>: 모든 의존 파일 전체 목록 (위로 펼쳐진 우산처럼 전체를 포함)
- **매크로 참조 시 괄호 누락 주의**:

  - 셸 스크립트와 달리 Makefile에서는 단일 문자 매크로(예: `$@`, `$<`)를 제외하고는 <strong>반드시</strong> <strong>`$(TARGET)`</strong><strong>처럼 괄호(</strong><strong>`()`</strong><strong>)를 붙여야 함</strong>.
  - `$TARGET`으로 쓰면 `$T`라는 한 글자 매크로 뒤에 `ARGET`이라는 문자열이 붙은 것으로 잘못 해석됨.
- <strong>패턴 규칙</strong> <strong>`%`</strong><strong>의 역할 서술 (단답형)</strong>:

  - `%.o: %.c`에서 `%`의 역할을 묻는다면 "타겟과 의존 파일 간에 확장자를 제외한 동일한 파일 이름(Stem)을 매칭하는 기호"로 서술해야 정답 인정.

<a id="notion-3df1d46c18fc802c81ddd319935529bd"></a>

#### 💡 \[선별 참고\]

- **`$(OBJS)`** <strong>대신</strong> **`$^`** <strong>활용</strong>:

  `$(TARGET): $(OBJS)` 규칙의 링크 명령어는 `$(CC) -o $@ $(OBJS)` 대신 모든 의존 파일을 가리키는 자동 변수 `$^`를 사용하여 `$(CC) -o $@ $^` 형태로 작성하는 것이 더 간결하고 보편적인 표준 작성 방식입니다.

<a id="notion-3df1d46c18fc807ca3f2c67adc930619"></a>

### 11\. C 라이브러리 개요 및 정적 라이브러리 (Static Library)

<a id="notion-3df1d46c18fc80d9b7c7c967bf5395c0"></a>

#### \[수업 내용 / 시험 범위\]

**1\) 라이브러리 개념 및 종류 비교**

- <strong>라이브러리(Library)</strong>: 자주 사용되는 공통 함수들을 미리 컴파일해 둔 목적 파일들의 집합
- **명명 규칙**: 반드시 접두사 `lib`로 시작해야 함 (`lib<이름>.확장자`)

|  |  |  |
| --- | --- | --- |
| **구분** | **정적 라이브러리 (Static Library)** | **공유 라이브러리 (Shared Library)** |
| **확장자** | **`.a`** (Archive) | **`.so`** (Shared Object) |
| **링크 시점** | **컴파일(빌드) 시점**에 실행 파일에 직접 포함 | 프로그램 **실행(런타임) 시점**에 동적으로 적재/연결 |
| **파일 크기** | 라이브러리 코드가 복사되므로 **실행 파일 크기가 큼** | 코드 본체가 빠져 있어 **실행 파일 크기가 작음** |
| **메모리 효율** | 프로세스마다 동일 코드가 메모리에 중복 적재됨 | 여러 프로그램이 메모리의 단일 인스턴스를 **공유**함 |
| **기본 정책** | 수동 지정 필요 (`--static` 등) | **리눅스 GCC 링크 시 기본값(Default)** |

<strong>2\) 정적 라이브러리 생성 및 심볼 확인 (</strong><strong>`ar`</strong><strong>,</strong> <strong>`nm`</strong><strong>)</strong>

정적 라이브러리는 오브젝트 파일(`.o`)들을 묶어놓은 단순 아카이브 파일입니다.

```bash
# 1. 소스 코드를 오브젝트 파일로 컴파일
aarch64-linux-gnu-gcc -c plus.c minus.c

# 2. 오브젝트 파일들을 묶어 정적 라이브러리(.a) 생성
aarch64-linux-gnu-ar crv libmycal.a plus.o minus.o

# 3. 라이브러리 내부 심볼(함수 목록) 확인
aarch64-linux-gnu-nm libmycal.a
```

- **`ar`** <strong>(Archive)</strong>: 여러 오브젝트 파일을 하나의 정적 라이브러리(`.a`)로 패키징하는 도구

  - **`c`** (Create): 아카이브 파일이 없으면 새로 생성
  - **`r`** (Replace): 아카이브에 이미 존재하는 오브젝트 파일을 새 파일로 대체/추가
  - **`v`** (Verbose): 생성 과정 및 포함되는 파일 목록을 화면에 상세 출력
- **`nm`** <strong>(Names)</strong>: 라이브러리나 실행 파일 내부의 심볼(함수명, 전역 변수 등) 목록을 조회하는 도구

**3\) 라이브러리 링크 3가지 방식 비교**

GCC에서 라이브러리를 연결하는 방법과 용량·의존성 차이입니다.

```bash
# [방법 1] 아카이브 파일 경로를 직접 지정
aarch64-linux-gnu-gcc -o mycalStatic1 main.c lib/libmycal.a

# [방법 2] 라이브러리 디렉터리 경로(-L)와 라이브러리명(-l) 지정
aarch64-linux-gnu-gcc -o mycalStatic2 main.c -Llib -lmycal

# [방법 3] 전체 정적 링크 옵션(--static) 추가
aarch64-linux-gnu-gcc -o mycalStatic3 main.c -Llib -lmycal --static
```

- **링크 옵션 해석**:

  - <strong>`L<경로>`</strong>: 컴파일러에게 라이브러리를 검색할 **디렉터리 경로**를 추가 지정 (예: `Llib` -&gt; 현재 디렉터리 하위 `lib/` 탐색)
  - <strong>`l<이름>`</strong>: 링크할 **라이브러리 이름**을 지정 (`lib` 접두사와 확장자를 제외한 고유 이름만 작성)

    - `gcc`는 `lmycal` 옵션을 보면 기본적으로 <strong>`libmycal.so`</strong>**를 우선 검색**하고, 없으면 <strong>`libmycal.a`</strong>**를 대체 검색**함.
- <strong>실행 파일 특성 및 크기 차이 (1, 2 vs 3)</strong>:

  - <strong>`mycalStatic1`</strong><strong>,</strong> **`mycalStatic2`** <strong>(경량)</strong>: `libmycal` 코드는 포함되지만, C 표준 라이브러리(`libc.so`)는 여전히 공유 라이브러리로 동적 링크됩니다. 실행 파일 용량은 작지만 타겟 OS에 표준 C 라이브러리가 없으면 실행되지 않습니다.
  - **`mycalStatic3`** <strong>(대용량, 완전 독립)</strong>: **`-static`** 플래그에 의해 사용자가 만든 라이브러리뿐 아니라 C 표준 라이브러리(`libc.a`)까지 모조리 바이너리 안에 복사·포함합니다. 용량은 수백 KB\~수 MB로 대폭 증가하지만, 외부 라이브러리 의존성이 전혀 없어 단일 파일만으로 즉시 실행 가능합니다.

**4\) 정적 라이브러리 빌드 자동화 Makefile**

```makefile
TARGET = mycalStatic1
OBJS = main.o
LIB_DIR = lib
LIB_TARGET = $(LIB_DIR)/libmycal.a
LIB_OBJS = $(LIB_DIR)/plus.o $(LIB_DIR)/minus.o
CC = aarch64-linux-gnu-gcc
AR = aarch64-linux-gnu-ar
CFLAGS = -c

all: $(TARGET)
	@echo "build finished!"

# [1] 실행 파일 링크: main.o와 libmycal.a를 결합
$(TARGET): $(OBJS) $(LIB_TARGET)
	$(CC) -o $@ $^

# [2] 정적 라이브러리 생성 규칙: ar crv 실행
$(LIB_TARGET): $(LIB_OBJS)
	$(AR) crv $@ $^

# [3] 오브젝트 파일 패턴 규칙
%.o: %.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	@rm -f $(TARGET) $(OBJS) $(LIB_TARGET) $(LIB_OBJS)
	@echo "clean finished!"
```

<a id="notion-3df1d46c18fc80adb266e17baac5fd57"></a>

#### \[시험 대비 핵심 포인트\]

- **`l`** <strong>옵션 문법 감점 주의 (코드 수필 1순위)</strong>:

  - `l` 뒤에는 `lib`와 확장자를 붙이지 않음.
  - `libmycal.a`를 링크할 때 `gcc -llibmycal.a`로 적으면 컴파일러가 `liblibmycal.a.so`를 찾으려다 에러 발생 -&gt; <strong>반드시</strong> <strong>`gcc -lmycal`</strong>**로 작성**.
- <strong>`L`</strong><strong>과</strong> <strong>`l`</strong><strong>의 역할 구분 (단답형)</strong>:

  - 대문자 <strong>`L`</strong>: 라이브러리가 위치한 **폴더(디렉터리) 경로** 지정
  - 소문자 <strong>`l`</strong>: 링크할 라이브러리의 **순수 파일 명칭** 지정
- **공유 라이브러리 우선순위**:

  - 동일한 이름의 `libmycal.so`와 `libmycal.a`가 같은 디렉터리에 공존할 때, `lmycal`만 부여하면 리눅스는 기본적으로 <strong>공유 라이브러리(</strong><strong>`.so`</strong><strong>)를 우선 링크</strong>함.
- **`-static`** <strong>옵션의 정확한 의미</strong>:

  - 단순히 내 라이브러리만 정적으로 묶는 것이 아니라, 시스템 C 표준 라이브러리(`libc`)까지 포함한 **모든 라이브러리를 완전 정적 링크**하여 외부 의존성이 없는 독립 실행 파일을 생성하는 옵션.

<a id="notion-3df1d46c18fc8019af21f8c921a850fa"></a>

#### 💡 \[선별 참고\]

- **`nm`** <strong>명령어 주요 심볼 타입</strong>:

  - **`T`** (Text segment): 해당 오브젝트 파일 내부에 정상 구현(정의)된 함수
  - **`U`** (Undefined): 해당 파일에서 호출은 되었으나 실제 코드는 외부 다른 파일에 정의되어 있는 심볼 (링크 단계에서 해결되어야 함)

<a id="notion-3df1d46c18fc807eb3c6ff8f60d844c9"></a>

### 12\. 공유 라이브러리 (Shared Library)

공유 라이브러리는 프로그램 실행 시(런타임) 여러 프로세스가 메모리에 올려 함께 사용하는 라이브러리입니다. 정적 라이브러리와 달리 **컴파일 시점의 링크**와 **실행 시점의 동적 로딩**이 분리되어 동작합니다.

<a id="notion-3df1d46c18fc80c3923bef2caff5d31b"></a>

#### \[수업 내용 / 시험 범위\]

**1\) 공유 라이브러리의 3가지 파일 명명 체계 (버전 관리)**

공유 라이브러리는 ABI(호환성) 관리를 위해 3가지 이름의 파일(실제 파일 1개 + 심볼릭 링크 2개) 구조를 가집니다.

```text
[링크 이름] libmycal.so  ──(링크)──>  libmycal.so.1.2  <──(링크)──  libmycal.so.1 [soname]
```

|  |  |  |
| --- | --- | --- |
| **구분** | **파일명 예시** | **역할 및 사용 시점** |
| **실제 파일**<br><br>(Real Name) | `libmycal.so.1.2` | 실제 기계어 코드가 들어있는 바이너리 파일 (메이저.마이너 버전 포함) |
| **soname 파일**<br><br>(Short for SO-Name) | `libmycal.so.1` | **실행 파일이 런타임에 찾아 실행할 호환성 기준 이름** (메이저 버전만 표기). 호환성이 유지되는 한 마이너 업데이트 시 심볼릭 링크 대상만 교체함 |
| **링크 파일**<br><br>(Linker Name) | `libmycal.so` | <strong>개발자가 컴파일할 때</strong> **`-lmycal`** <strong>옵션으로 참조하는 링크용 심볼릭 링크</strong> |

**2\) 공유 라이브러리 생성 필수 GCC 옵션**

|  |  |  |
| --- | --- | --- |
| **옵션** | **명칭 / 역할** | **상세 설명** |
| **`-fPIC`** | Position Independent Code | **위치 독립적 코드 생성**. 코드가 메모리의 어떤 주소에 로드되더라도 정상 실행되도록 상대 주소 기반 코드로 컴파일 (공유 라이브러리 오브젝트 생성 시 필수) |
| **`-shared`** | Shared Object | `main()` 함수가 없는 공유 라이브러리(`.so`) 파일 형태로 빌드하도록 지정 |
| **`-Wl,<옵션>`** | Warn Linker | GCC 컴파일러를 거치지 않고 <strong>링커(</strong><strong>`ld`</strong><strong>)에게 직접 옵션을 전달</strong>하는 플래그 |
| **`-soname,<이름>`** | SO Name 지정 | 생성되는 라이브러리 바이너리 헤더 내부에 공식 `soname`을 각인함 |

**3\) 공유 라이브러리 생성 및 심볼릭 링크 실습**

```bash
cd lib

# 1. 위치 독립적 코드(-fPIC)로 오브젝트 파일 컴파일
aarch64-linux-gnu-gcc -c -fPIC plus.c minus.c

# 2. soname을 각인하여 공유 라이브러리 본체(.so.1.2) 생성
aarch64-linux-gnu-gcc -shared -Wl,-soname,libmycal.so.1 -o libmycal.so.1.2 plus.o minus.o

# 3. soname 심볼릭 링크 생성 (런타임 호환성 연결용)
ln -s libmycal.so.1.2 libmycal.so.1

# 4. 링커용 심볼릭 링크 생성 (컴파일 시 -lmycal 매핑용)
ln -s libmycal.so.1.2 libmycal.so

cd ..
```

**4\) 프로그램 빌드 및 런타임 에러 분석**

```bash
# 컴파일 및 링크 (모두 동일하게 정상 빌드됨)
aarch64-linux-gnu-gcc -o mycalDynamic main.c -Llib -lmycal

# 실행 시도시 에러 발생!
./mycalDynamic
# ./mycalDynamic: error while loading shared libraries: libmycal.so.1: cannot open shared object file: No such file or directory
```

- **에러 원인**:

  - 컴파일할 때 준 `Llib` 옵션은 **컴파일 시점(빌드 타임)에만 컴파일러에게 위치를 알려주는 옵션**입니다.
  - 실행할 때는 OS의 동적 링커(런타임 로더)가 라이브러리를 메모리에 올려야 하는데, 동적 링커는 사용자의 작업 폴더(`lib/`)를 기본적으로 탐색하지 않고 표준 시스템 라이브러리 디렉터리(`/lib`, `/usr/lib` 등)만 뒤지기 때문에 `libmycal.so.1`을 찾지 못해 에러가 발생합니다.

**5\) 동적 링커가 라이브러리를 찾게 만드는 3가지 방법**

<a id="notion-3df1d46c18fc80768406ddfcb2015544"></a>

#### 방법 1: 임시 환경 변수 설정 (`LD_LIBRARY_PATH`) — \[개발/테스트용\]

동적 링커가 기본 시스템 경로 외에 추가로 탐색할 디렉터리를 환경 변수로 지정합니다.

```bash
mkdir -p /home/aidl/work/lib
cp -a lib/libmycal* /home/aidl/work/lib

# 런타임 라이브러리 검색 경로 등록
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/aidl/work/lib

./mycalDynamic       # 정상 실행!

# 변수 해제 시 다시 에러 발생
unset LD_LIBRARY_PATH
./mycalDynamic       # 에러 발생
```

<a id="notion-3df1d46c18fc8089a54ad48cfc2fc7c1"></a>

#### 방법 2: 표준 시스템 라이브러리 디렉터리로 복사 — \[단순 배포용\]

동적 링커가 기본적으로 탐색하는 `/lib` 디렉터리에 라이브러리를 직접 넣습니다.

```bash
sudo cp -a lib/libmycal* /lib

./mycalDynamic       # 별도 설정 없이 즉시 정상 실행!

sudo rm /lib/libmycal*
./mycalDynamic       # 에러 발생
```

<a id="notion-3df1d46c18fc80f78fb4ff324a8cd3d5"></a>

#### 방법 3: 시스템 라이브러리 설정 파일 등록 및 갱신 (`/etc/ld.so.conf` \+ `ldconfig`) — \[정석 운영용\]

새로운 라이브러리 경로를 OS 설정 파일에 영구 등록하고 캐시를 갱신합니다.

```bash
# 1. /etc/ld.so.conf 파일 맨 아래에 라이브러리 절대 경로 추가
#    (/home/aidl/work/lib 한 줄 추가)

# 2. 변경된 설정을 바탕으로 동적 링커 캐시(/etc/ld.so.cache) 즉시 갱신 (필수!)
sudo ldconfig

./mycalDynamic       # 환경변수 없이도 정상 실행!
```

<a id="notion-3df1d46c18fc809da50bfcf7ec63e2ca"></a>

#### \[시험 대비 핵심 포인트\]

- <strong>`fPIC`</strong><strong>의 의미와 필요성 (단답형/서술형 단골)</strong>:

  - <strong>Position Independent Code (위치 독립 코드)</strong>.
  - 정적 라이브러리와 달리 공유 라이브러리는 여러 프로세스가 서로 다른 가상 메모리 공간에 적재하여 공유해야 하므로, **절대 주소가 아닌 상대 주소로 동작하는 코드를 생성**하도록 컴파일러에 지시하는 필수 옵션.
- **`Wl,-soname,<이름>`** <strong>문법 구조 (코드 수필 감점 방지)</strong>:

  - `Wl,` (W 대문자, l 소문자, 콤마)는 GCC가 뒤이어 오는 옵션들을 <strong>링커(</strong><strong>`ld`</strong><strong>)에게 직접 넘기라는 지시문</strong>임.
  - 띄어쓰기 없이 콤마(`,`)로 인자를 연결해야 함 (`Wl,-soname,libmycal.so.1`).
- <strong>빌드 성공 후 실행 실패 원인 서술 (주관식 1순위)</strong>:

  - "`L` 옵션은 컴파일 시점에 라이브러리 심볼을 검증하기 위한 경로일 뿐, 프로그램 실행 시 동작하는 동적 링커의 기본 탐색 경로에는 포함되지 않기 때문"이라고 서술해야 완벽한 정답 인정.
- <strong>`ldconfig`</strong>**의 역할**:

  - `/etc/ld.so.conf` 파일에 적힌 디렉터리들을 검색하여 동적 링커가 고속으로 라이브러리를 찾을 수 있도록 **`/etc/ld.so.cache`** <strong>바이너리 캐시 파일을 갱신</strong>해 주는 관리 명령.

<a id="notion-3df1d46c18fc80fdbb74d8ca324f7990"></a>

### 응용 프로그램과 공유 라이브러리의 관계 구조

```text
       [ 빌드 시점 (Build Time) ]                      [ 실행 시점 (Runtime) ]
                 gcc                                          동적 링커
                  │ (참조)                                        │ (탐색/로드)
                  ▼                                               ▼
         [ 링크 파일: libmycal.so ]                      [ soname 파일: libmycal.so.1 ]
                  │                                               │
                  │ (가리킴)                                      │ (가리킴)
                  ▼                                               ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │                      [ 원본 파일: libmycal.so.1.2 ]             │
     │                      (내부에 soname=libmycal.so.1 각인)          │
     └────────────────────────────────┬────────────────────────────────┘
                                      │ (soname 정보 추출 및 기록)
                                      ▼
                        [ 응용 프로그램: mycalDynamic ]
                        (필요한 라이브러리: libmycal.so.1 기록)
```

<a id="notion-3df1d46c18fc8092a0d3fac7abaa45da"></a>

#### \[수업 내용 / 시험 범위\]

**1\) 2단계 동작 흐름 분석**

- **1단계: 빌드 시점 (컴파일 &amp; 링크 단계)**

  - **gcc의 동작**: 사용자가 `lmycal` 옵션을 주면 gcc는 우선 링크 파일(`libmycal.so`)을 참조합니다.
  - **심볼릭 링크 추적**: 링크 파일(`libmycal.so`)은 심볼릭 링크이므로 실제 원본 파일(`libmycal.so.1.2`)을 가리킵니다.
  - **soname 추출 및 기록**: gcc는 원본 파일 바이너리 헤더에 각인되어 있는 <strong>`soname`</strong><strong>(</strong><strong>`libmycal.so.1`</strong><strong>)</strong> 정보를 확인한 뒤, 완성되는 <strong>응용 프로그램(</strong><strong>`mycalDynamic`</strong><strong>) 내부에 "실행 시 필요한 라이브러리는</strong> <strong>`libmycal.so.1`</strong>**이다"라고 기록**합니다.
- **2단계: 프로그램 로드 및 실행 시점 (런타임 단계)**

  - **동적 링커의 동작**: 프로그램을 실행하면 리눅스 커널의 동적 링커(Dynamic Linker)가 응용 프로그램 내부에 기록된 라이브러리 정보인 `soname` 파일(`libmycal.so.1`)을 시스템에서 찾습니다.
  - **경로 탐색**: 이때 앞서 학습한 3가지 탐색 방법(`LD_LIBRARY_PATH`, `/lib` 직접 복사, `/etc/ld.so.conf` 등록)을 거쳐 파일을 탐색합니다.
  - **최종 코드 실행**: 찾아낸 soname 파일(`libmycal.so.1`) 역시 심볼릭 링크로 원본 파일(`libmycal.so.1.2`)을 가리키고 있으므로, 실제 기계어 코드가 메모리에 매핑되어 정상 실행됩니다.

<a id="notion-3df1d46c18fc8022acbcd19dc1fc8d87"></a>

#### \[시험 대비 핵심 포인트\] (★ 교수님 강조 킬러 문항)

- <strong>참조하는 파일 대상 구분 (객관식/단답형 1순위)</strong>:

  - **gcc가 빌드할 때 참조하는 파일**: -&gt; <strong>링크 파일 (</strong><strong>`libmycal.so`</strong><strong>)</strong>
  - **동적 링커가 실행할 때 찾는 파일**: -&gt; <strong>soname 파일 (</strong><strong>`libmycal.so.1`</strong><strong>)</strong>
  - **실제 함수 기계어 코드가 들어있는 파일**: -&gt; <strong>원본 파일 (</strong><strong>`libmycal.so.1.2`</strong><strong>)</strong>
- <strong>응용 프로그램 내부에 기록되는 라이브러리 이름 (주관식 단골)</strong>:

  - 응용 프로그램(`mycalDynamic`) 내부에는 컴파일할 때 쓴 링크 파일명(`libmycal.so`)이나 실제 파일명(`libmycal.so.1.2`)이 적히는 것이 아니라, <strong>오직</strong> <strong>`soname`</strong><strong>(</strong><strong>`libmycal.so.1`</strong><strong>)이 기록</strong>된다는 점.
- **심볼릭 링크의 방향성 서술**:

  - 링크 파일(`libmycal.so`)과 soname 파일(`libmycal.so.1`)은 <strong>둘 다 실제 원본 바이너리 파일(</strong><strong>`libmycal.so.1.2`</strong><strong>)을 가리키는 심볼릭 링크</strong>라는 점.
