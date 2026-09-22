# Notion TIL 동기화

Notion 데이터베이스의 학습 기록을 `TIL/YYYY/MM/YYYY-MM-DD_제목.md`에 저장하고, 루트 README의 월별 목록을 갱신합니다. 실행 명령은 기존과 동일한 `python update_readme.py`입니다.

## 실행 방식

- **Auto Sync Notion TIL**: 매일 UTC 15:05(한국 시간 다음 날 00:05)에 **한국 날짜 기준 전날** 기록을 가져옵니다. 생성/수정 시각이 아니라 Notion의 `날짜` 속성으로 조회합니다. GitHub 예약 작업 실행은 지연될 수 있습니다.
- 일간 작업을 수동 실행할 때 `target_date`에 `YYYY-MM-DD`를 입력하면 특정 날짜를 다시 가져옵니다. 비우면 전날입니다.
- **Manual Sync & Init**: 날짜가 있는 전체 기록을 다시 가져옵니다. 과거 문서의 빠진 블록을 복구하거나, 예전 기록을 수정했을 때 사용합니다.
- `reset_readme`는 README 전체를 기본 템플릿으로 교체하는 옵션입니다. 기존 소개와 추가 링크를 유지하려면 **체크하지 않습니다**.
- 날짜가 비어 있는 페이지는 경고와 함께 건너뜁니다. 잘못된 날짜/속성 타입, API 오류, 다운로드 오류는 실행 실패로 표시합니다.

이번 변환 개선을 기존 기록에도 적용하려면 변경 사항을 GitHub에 반영한 뒤 **Manual Sync & Init을 한 번 실행**하세요. `reset_readme`는 필요하지 않습니다.

## GitHub 설정

기존 Actions secrets를 그대로 사용합니다.

| 설정                              | 용도                                                                                                      |
| --------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `NOTION_TOKEN`                    | Notion 연결의 API 토큰. 대상 데이터베이스에 읽기 권한을 부여해야 합니다.                                  |
| `NOTION_DATABASE_ID`              | 기존에 사용한 데이터베이스 ID                                                                             |
| `NOTION_DATA_SOURCE_ID`           | 선택. 데이터베이스에 데이터 소스가 여러 개일 때 가져올 표를 지정합니다. 이 값만 지정해도 실행 가능합니다. |
| `GIT_USER_NAME`, `GIT_USER_EMAIL` | 선택. 자동 커밋 작성자. 없으면 기존 기본값을 사용합니다.                                                  |

Notion API 버전은 `2026-03-11`로 고정했습니다. 기존 database ID에서 데이터 소스를 조회하여 실제 표의 내용을 가져옵니다. 데이터 소스가 여러 개면 임의로 선택하지 않고 `NOTION_DATA_SOURCE_ID`를 설정하도록 오류를 냅니다. [Notion 데이터 소스 전환 안내](https://developers.notion.com/guides/get-started/upgrade-guide-2025-09-03), [2026-03-11 변경 사항](https://developers.notion.com/guides/get-started/upgrade-guide-2026-03-11).

## 변환 범위

| Notion 내용                             | GitHub Markdown 표현                                                                       |
| --------------------------------------- | ------------------------------------------------------------------------------------------ |
| 문단, 제목 1–4, 구분선                  | 문단, 제목, 수평선                                                                         |
| 굵게, 기울임, 취소선, 밑줄, 인라인 코드 | Markdown 강조 및 `<ins>`                                                                   |
| 링크, 페이지/DB/사용자/날짜 멘션        | 링크 또는 API가 제공한 표시 텍스트                                                         |
| 글머리·번호 목록, 체크박스              | 중첩 깊이와 체크 상태를 유지한 목록                                                        |
| 토글, 토글 제목, 템플릿                 | `<details>` / `<summary>` 접기                                                             |
| 인용문, 콜아웃                          | 인용문, 아이콘, 하위 내용                                                                  |
| 코드, Mermaid                           | 원문 코드와 언어, 캡션. 코드 안의 백틱이 코드 블록을 닫지 않도록 구분자 길이를 조정합니다. |
| 인라인/블록 수식                        | GitHub의 `$...$`, `$$...$$` 표현                                                           |
| 표                                      | 헤더 유무, 첫 열 헤더, 빈 셀, 셀 내부 줄바꿈을 처리한 표                                   |
| 컬럼, 탭                                | 읽기 순서에 따른 세로 배치                                                                 |
| 동기화 블록                             | 원본 블록 내용 재사용. 순환 참조는 원본 링크로 표시                                        |
| 이미지                                  | 이미지와 캡션                                                                              |
| 파일, PDF, 오디오, 동영상               | 파일 링크와 캡션                                                                           |
| 북마크, 임베드, 링크 미리보기           | 원본 링크와 캡션                                                                           |
| 하위 페이지                             | 원본 링크 및 API가 반환하는 하위 블록                                                      |
| 하위 데이터베이스, 페이지 링크          | 원본 Notion 링크                                                                           |
| 목차                                    | 문서 제목을 가리키는 링크 목록                                                             |
| 회의록                                  | API가 제공하는 요약·메모·대화 기록 섹션                                                    |
| 경로 표시, API 미지원/새 블록           | 원본 링크와 설명. 제공되는 텍스트·하위 블록은 보존                                         |

Notion 화면과 GitHub Markdown은 표현 방식이 다릅니다. 글자색·배경색·컬럼 너비·임베드의 인터랙션·DB 보기/필터는 재현하지 않습니다. 버튼·폼 등 API가 내용을 제공하지 않는 블록은 원본 링크를 남깁니다. 멘션 대상의 접근 권한이 없으면 API가 제공한 제한된 표시만 사용할 수 있습니다. [Notion 블록 문서](https://developers.notion.com/reference/block), [리치 텍스트 문서](https://developers.notion.com/reference/rich-text).

## 첨부파일과 파일 보존

Notion 업로드 파일의 URL은 만료되므로 `TIL/YYYY/MM/assets/<페이지 ID>/`에 다운로드하여 문서에서 상대경로로 연결합니다. 같은 서명 URL이 매번 바뀌어도 파일명은 유지됩니다. 일반 외부 링크는 그대로 두며, 다운로드 요청에 Notion 토큰을 보내지 않습니다. [Notion 파일 URL 안내](https://developers.notion.com/reference/file-object).

- 다운로드는 메모리에 파일 전체를 올리지 않고 스트림으로 처리합니다.
- 파일당 최대 **50 MiB**입니다. 초과하면 실행을 실패시키므로 큰 파일은 외부 호스팅 링크로 첨부하거나 크기를 줄여 주세요.
- 페이지 내용을 모두 읽고 변환한 뒤 파일을 교체합니다. 실패한 페이지를 빈 문서로 덮어쓰지 않습니다.
- 이미 성공한 다른 페이지의 변경은 로컬에 남을 수 있지만, 하나라도 실패하면 README 갱신과 Actions의 커밋/푸시는 진행하지 않습니다.
- 같은 날짜·같은 제목의 서로 다른 페이지는 페이지 ID 접미사로 구별합니다. 제목/날짜 변경은 같은 Notion ID의 기존 파일을 찾아 이동합니다. 긴 제목은 파일명만 줄이며 본문과 목록의 제목은 보존합니다.
- 기존 문서의 `원본 노션` 링크를 통해 ID를 인식하므로 기존 기록도 새 방식으로 이어집니다.
- Notion에서 지운 페이지나 더 이상 쓰지 않는 첨부파일은 자동 삭제하지 않습니다. 학습 기록 저장소의 기존 자료는 유지합니다.
- README는 `TIL_LIST_START`와 `TIL_LIST_END` 사이만 바꿉니다. 두 마커가 모두 없으면 목록을 뒤에 추가하고, 마커가 하나만 있거나 순서가 잘못되면 기존 내용을 보존하고 실패합니다.

## 코드 구조와 검증

```text
update_readme.py       # 기존 실행 진입점
til_sync/
  constants.py         # 공통 경로, 속성 기본값, 요청 제한 시간
  config.py            # FetchMode 열거형, 환경 변수, KST 날짜 계산, 입력 검증
  notion.py            # API 조회, 페이지네이션, 재시도, 블록 캐시
  markdown.py          # 블록 트리와 리치 텍스트 변환
  assets.py            # 만료되는 첨부파일 다운로드
  storage.py           # 파일명, 페이지 식별, 원자적 저장, README 목록
  sync.py              # 전체 처리 순서와 실패 상태
tests/                 # 네트워크와 토큰 없이 실행하는 회귀 테스트
```

GitHub Actions의 Python 버전은 `.python-version`에서 관리합니다(현재 3.12). `requirements.txt`는 실행에 필요한 Requests만 포함하며, 개발용 `requirements-dev.txt`는 여기에 Ruff를 추가합니다. 테스트는 표준 라이브러리 `unittest`를 사용합니다.

VS Code와 CI는 프로젝트의 `ruff.toml`을 사용합니다. 기본 검사 규칙을 유지하면서 import 정리, Python 현대 문법, 오류 가능성 검사도 적용합니다. 검사 대상은 Python 파일이며, 생성된 `TIL/` 문서와 첨부파일은 포맷하지 않습니다. 프로젝트 설정 파일의 적용 방식은 [Ruff 공식 문서](https://docs.astral.sh/ruff/configuration/)를 참고하세요.

개발 환경에서 검사하려면 다음을 실행합니다.

```powershell
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
python -m unittest discover -s tests -v
```

코드 형식을 자동으로 정리할 때는 `python -m ruff format .`을 사용합니다. Python 최소 버전을 변경할 때는 `.python-version`과 `ruff.toml`의 `target-version`을 함께 맞춥니다.

실행용 패키지만 설치하여 동기화하려면 다음을 사용합니다.

```powershell
python -m pip install -r requirements.txt

# 현재 PowerShell 세션에 토큰과 데이터베이스 ID가 설정된 상태에서 실행
$env:FETCH_MODE = "DAILY"
$env:TARGET_DATE = "2026-09-21"  # 특정 날짜 재실행. 기본 전날은 이 변수를 제거
python update_readme.py
```

환경 변수 `NOTION_PROPERTY_TITLE`, `NOTION_PROPERTY_DATE`로 열 이름을 변경할 수 있으며 기본값은 `제목`, `날짜`입니다. 제목 열 이름이 달라져도 실제 `title` 타입 속성을 찾습니다. 로컬 실행은 현재 디렉터리에 기록하므로 저장소 루트에서 실행하세요. 전체 조회 시 `FETCH_MODE=ALL`로 설정하고 `TARGET_DATE`는 제거합니다. `.env`를 자동으로 읽지는 않습니다.

일간/전체 Actions는 같은 브랜치에서 순서대로 실행합니다. 동기화 전에 테스트를 수행하고, README와 TIL만 커밋합니다. 실제 커밋/푸시 오류는 실패로 표시되며, 원격 변경은 rebase 후 일반 push로 반영합니다. 코드·설정·workflow 변경 시 별도 CI에서 Ruff 검사, 형식 검사, 테스트를 순서대로 실행합니다.

## 설정과 상수를 변경할 때

- `config.py`의 `FetchMode`는 `DAILY`/`ALL` 실행 모드를 정의합니다. 환경 변수 입력은 공백·대소문자를 정리한 뒤 열거형으로 검증합니다.
- 공통 경로·속성 이름 기본값·HTTP 요청 제한 시간은 `constants.py`에서 관리합니다. 저장 경로를 바꾸면 workflow의 `git add` 대상도 함께 확인해야 합니다.
- API 버전·페이지 크기·재시도 정책은 `notion.py`, 첨부파일 크기·다운로드 정책은 `assets.py`, 파일명 길이는 `storage.py`의 상수에서 관리합니다.
- Notion JSON 필드명과 Markdown 문법은 해당 처리 코드에 유지합니다. 프로토콜에 정해진 값까지 별도 설정으로 노출하지 않습니다.

API·파일·설정 오류는 구체적인 예외 타입으로 처리합니다. 페이지 일부가 실패하면 `SyncError`로 실행을 실패시키고 README 갱신을 막습니다. 예상하지 못한 프로그래밍 오류는 원래 traceback을 남겨 원인을 확인할 수 있습니다.
