# \[Python\] 예외 흐름 통제(Exception)와 모듈 스코프 네임스페이스 관리

> 날짜: 2026-07-10
> 원본 노션: [링크](https://app.notion.com/p/Python-Exception-3991d46c18fc8066bfa0f4527adfd00f)

<!-- notion-page-id: 3991d46c18fc8066bfa0f4527adfd00f -->
<!-- notion-title: "[Python] 예외 흐름 통제(Exception)와 모듈 스코프 네임스페이스 관리" -->

---

<a id="notion-3991d46c18fc80629414dfc55eb7235e"></a>

# 🛠️ \[Chapter 11\]

<a id="notion-3991d46c18fc80c196dffd115fbe7e44"></a>

#### 1\. 예외 처리(Exception Handling)의 4단 구조와 에러 탐색

- <strong>지정 매칭 vs</strong> **`Exception`** <strong>(</strong><strong>`[11-13]`</strong><strong>,</strong> <strong>`[11-14]`</strong><strong>) :</strong> `except NameError:`처럼 특정 에러를 명시하면 해당 에러만 포착합니다. 모든 종류의 예외를 빠짐없이 입구 컷 하려면 최상위 예외 클래스인 `except Exception:`을 사용합니다.
- <strong>에러 객체 해부 (</strong><strong>`[11-15]`</strong><strong>) :</strong> `except Exception as e:` 문법으로 에러 객체를 변수 `e`로 포착할 수 있습니다. `type(e).__name__`은 발생한 에러의 이름 문자열을, `e`는 에러의 상세 사유 메시지를 반환합니다.
- **`else`** <strong>vs</strong> **`finally`** <strong>분기 법칙 (</strong><strong>`[11-16]`</strong><strong>,</strong> <strong>`[11-17]`</strong><strong>) :</strong>

  - **`else`** <strong>:</strong> `try` 블록 내부에서 예외가 **단 한 번도 발생하지 않고 성공했을 때만** 진입합니다.
  - **`finally`** <strong>:</strong> 예외 발생 여부, 예외 처리 여부와 관계없이 코드의 마지막에 **무조건 100% 실행**되는 절대 보장 공간입니다.

```python
# [11-16-2] 예외 처리의 완전체 실행 흐름 복습
try:
    a = 10; a = b  # NameError 발생!
except NameError:
    a = 0          # 예외 포착 -> 실행 (a=0)
else:
    a += 30        # 에러가 터졌으므로 실행 스킵!
finally:
    a += 40        # 에러 여부 무관 무조건 실행! -> 최종 a = 40
```

<a id="notion-3991d46c18fc8026aae7feaa7ebceb17"></a>

#### 2\. 모듈(Module) 호출과 이름 충돌(Shadowing) 방어

- **`import`** <strong>vs</strong> **`from ... import`** <strong>(</strong><strong>`[11-18]`</strong><strong>,</strong> <strong>`[11-19]`</strong><strong>) :</strong>

  - `import my_module` 은 모듈 방을 통째로 들고 와 `my_module.add()` 형태로 호출하므로 로컬 네임스페이스 충돌을 방지합니다.
  - `from my_module import add` 는 특정 명칭을 현재 장부에 직수입하므로, 같은 공간에 동명의 로컬 `def add()`가 존재할 경우 **나중에 선언되거나 수입된 이름이 이전 것을 덮어써 버리는(Shadowing)** 대참사가 납니다.
- **`globals()`** <strong>장부 검증 (</strong><strong>`[11-20]`</strong><strong>) :</strong> `from 모듈 import *`는 모듈 내 모든 요소를 현재 스크립트 전역 공간(`globals()`)에 풀어버리므로, 관리 불가능한 이름 오염이 발생해 실무에서 기피하는 안티 패턴입니다.

<a id="notion-3991d46c18fc80b289c5fcb5ddfd607f"></a>

#### 3\. 패키지(Package) 구조 탐색과 시스템 경로 관리

- <strong>점(</strong><strong>`.`</strong> <strong>) 계층 디렉토리 구조 (</strong><strong>`[11-21]`</strong><strong>) :</strong> 폴더 내부에 모듈들이 갇혀 있는 패키지 형태는 **`import 패키지명.모듈명`** 혹은 `from 패키지명 import 모듈명` 구조로 닷(`.`) 연산자를 타고 들어가 안전하게 로드합니다.
- **`sys.path`** <strong>동적 탐색 경로 주입 (</strong><strong>`[11-21]`</strong><strong>) :</strong> 파이썬의 표준 패키지 경로 밖에 존재하는 모듈을 호출해야 할 때 사용하는 고급 경로 제어 테크닉입니다.

```python
import sys
sys.path.append(r".\my_package\files") # 1. 수동으로 외부 경로를 검색 엔진에 바인딩
import my_module2 as mm2              # 2. 경로가 뚫렸으므로 정상 임포트 완료
sys.path.pop()                        # 3. 임포트 완료 후 경로 리스트를 꺼내 장부 복구
```

<br>
