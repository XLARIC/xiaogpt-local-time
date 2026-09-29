"""Deterministic local time/date answers; no LLM or external time API."""

from datetime import datetime
import os
from pathlib import Path
import re
from zoneinfo import ZoneInfo

TIME_QUESTIONS = frozenset({
    "几点", "几点了", "现在几点", "现在几点了", "现在是几点", "现在是几点了",
    "现在的时间", "现在时间", "现在是什么时间", "现在是什么时候",
})
DATE_QUESTIONS = frozenset({
    "今天几号", "今天几号了", "今天是几号", "今天是几号了",
    "今天几月几号", "今天是几月几号", "今天几月几日", "今天是几月几日",
    "今天什么日期", "今天是什么日期", "今天的日期", "今天日期",
    "现在几号", "现在几号了", "现在是几号", "现在是几号了",
})
DATETIME_QUESTIONS = frozenset({
    "今天几号现在几点", "今天几号了现在几点了", "今天几号几点了",
    "今天是几号现在几点", "今天是几号现在几点了", "现在的日期和时间",
    "现在日期和时间", "现在是什么日期和时间", "今天的日期和时间",
})
WEEKDAY_QUESTIONS = frozenset({
    "今天星期几", "今天是星期几", "今天周几", "今天是周几",
})
PREFIXES = ("请告诉我", "帮我查一下", "帮我看看", "告诉我", "问一下", "我想问", "帮我", "请")
WEEKDAYS = ("一", "二", "三", "四", "五", "六", "日")


def configured_timezone() -> ZoneInfo:
    """TZ takes priority; otherwise use a mounted host /etc/localtime."""
    timezone_name = os.environ.get("TZ", "").strip()
    if timezone_name:
        return ZoneInfo(timezone_name)
    path = Path("/etc/localtime")
    if path.is_file():
        with path.open("rb") as f:
            return ZoneInfo.from_file(f)
    return ZoneInfo("Etc/UTC")


def normalize_question(query: str) -> str:
    normalized = re.sub(r"[\s，,？?。.!！、]", "", query)
    for prefix in PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
            break
    return normalized


def local_clock_answer(query: str, now: datetime | None = None) -> str | None:
    normalized = normalize_question(query)
    if normalized not in TIME_QUESTIONS | DATE_QUESTIONS | DATETIME_QUESTIONS | WEEKDAY_QUESTIONS:
        return None
    timezone = configured_timezone()
    if now is None:
        local = datetime.now(timezone)
    else:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("The test clock must include a timezone")
        local = now.astimezone(timezone)

    weekday = "星期" + WEEKDAYS[local.weekday()]
    date = f"{local.year}年{local.month}月{local.day}日"
    if normalized in WEEKDAY_QUESTIONS:
        return f"今天是{weekday}"
    if normalized in DATE_QUESTIONS:
        return f"今天是{date}，{weekday}"
    period = (
        "凌晨" if local.hour < 5 else
        "早上" if local.hour < 9 else
        "上午" if local.hour < 12 else
        "中午" if local.hour < 13 else
        "下午" if local.hour < 18 else "晚上"
    )
    hour = local.hour % 12 or 12
    clock = f"{period}{hour}点{local.minute:02d}分"
    if normalized in DATETIME_QUESTIONS:
        return f"今天是{date}，{weekday}，现在是{clock}"
    return f"现在是{clock}"
