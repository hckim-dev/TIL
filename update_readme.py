"""기존 GitHub Actions에서 사용하는 Notion TIL 동기화 진입점."""

from til_sync.sync import main

if __name__ == "__main__":
    raise SystemExit(main())
