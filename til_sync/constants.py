"""여러 모듈이 공유하는 기본값. API 필드 이름과 Markdown 문법은 각 모듈에 둡니다."""

TIL_DIRECTORY = "TIL"
README_FILENAME = "README.md"
ASSETS_DIRECTORY = "assets"

DEFAULT_TITLE_PROPERTY = "제목"
DEFAULT_DATE_PROPERTY = "날짜"
DEFAULT_PAGE_TITLE = "제목없음"

NOTION_WEB_BASE = "https://www.notion.so"
REQUEST_TIMEOUT = (10, 60)  # requests의 (연결, 읽기) 제한 시간, 초 단위.
BYTES_PER_MIB = 1024 * 1024
RELATIVE_URL_SAFE = "/-._~"
ISO_DATE_LENGTH = 10  # YYYY-MM-DD
