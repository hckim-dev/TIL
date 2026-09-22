"""실행 시 환경 변수를 읽고 기존 일간/전체 동기화 규칙을 검증합니다."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from enum import StrEnum
from pathlib import Path
from typing import Self

from .constants import DEFAULT_DATE_PROPERTY, DEFAULT_TITLE_PROPERTY

KST_UTC_OFFSET_HOURS = 9
KST = timezone(timedelta(hours=KST_UTC_OFFSET_HOURS))


class FetchMode(StrEnum):
    DAILY = "DAILY"
    ALL = "ALL"


@dataclass(frozen=True)
class Config:
    token: str = field(repr=False)
    database_id: str = ""
    data_source_id: str = ""
    fetch_mode: FetchMode = FetchMode.DAILY
    reset_readme: bool = False
    target_date: str | None = None
    title_property: str = DEFAULT_TITLE_PROPERTY
    date_property: str = DEFAULT_DATE_PROPERTY
    root: Path = Path(".")

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | None = None,
        *,
        now: datetime | None = None,
        root: Path = Path("."),
    ) -> Self:
        env = os.environ if env is None else env
        token = env.get("NOTION_TOKEN", "").strip()
        database_id = env.get("NOTION_DATABASE_ID", "").strip()
        data_source_id = env.get("NOTION_DATA_SOURCE_ID", "").strip()
        if not token:
            raise ValueError("NOTION_TOKEN을 설정하세요.")
        if not database_id and not data_source_id:
            raise ValueError(
                "NOTION_DATABASE_ID 또는 NOTION_DATA_SOURCE_ID를 설정하세요."
            )
        try:
            mode = FetchMode(env.get("FETCH_MODE", FetchMode.DAILY).strip().upper())
        except ValueError:
            choices = ", ".join(FetchMode)
            raise ValueError(f"FETCH_MODE는 {choices} 중 하나여야 합니다.") from None
        reset = env.get("RESET_MODE", "false").strip().lower()
        if reset not in {"true", "false"}:
            raise ValueError("RESET_MODE는 true 또는 false이어야 합니다.")
        target = env.get("TARGET_DATE", "").strip()
        if target:
            if mode != FetchMode.DAILY:
                raise ValueError("TARGET_DATE는 DAILY 모드에서만 지정할 수 있습니다.")
            if date.fromisoformat(target).isoformat() != target:
                raise ValueError("TARGET_DATE는 YYYY-MM-DD 형식이어야 합니다.")
        elif mode == FetchMode.DAILY:
            current = now or datetime.now(KST)
            if current.tzinfo is None:
                raise ValueError("현재 시각에는 시간대 정보가 필요합니다.")
            target = (current.astimezone(KST).date() - timedelta(days=1)).isoformat()
        title_property = env.get(
            "NOTION_PROPERTY_TITLE", DEFAULT_TITLE_PROPERTY
        ).strip()
        date_property = env.get("NOTION_PROPERTY_DATE", DEFAULT_DATE_PROPERTY).strip()
        if not title_property or not date_property:
            raise ValueError("Notion 제목/날짜 속성 이름은 비어 있을 수 없습니다.")
        return cls(
            token=token,
            database_id=database_id,
            data_source_id=data_source_id,
            fetch_mode=mode,
            reset_readme=reset == "true",
            target_date=target or None,
            title_property=title_property,
            date_property=date_property,
            root=root.resolve(),
        )
