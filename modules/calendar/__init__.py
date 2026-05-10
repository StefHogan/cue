import platform
from datetime import date, timedelta
from typing import Any

from .google import fetch_events as fetch_google_events
from .icloud import fetch_events as fetch_icloud_events
from .types import CalEvent

HOUR_FMT = "%#I:%M %p" if platform.system() == "Windows" else "%-I:%M %p"
MAX_EVENTS_LISTED = 5


def fetch_calendar(config: dict[str, Any]) -> str:
    cal_cfg = config.get("calendar") or {}
    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_events: list[CalEvent] = []
    tomorrow_events: list[CalEvent] = []

    if (cal_cfg.get("google") or {}).get("enabled"):
        today_events.extend(fetch_google_events(cal_cfg["google"], today))
        tomorrow_events.extend(fetch_google_events(cal_cfg["google"], tomorrow))

    if (cal_cfg.get("icloud") or {}).get("enabled"):
        today_events.extend(fetch_icloud_events(cal_cfg["icloud"], today))
        tomorrow_events.extend(fetch_icloud_events(cal_cfg["icloud"], tomorrow))

    today_events = _dedupe_and_sort(today_events)
    tomorrow_events = _dedupe_and_sort(tomorrow_events)

    parts = [_summary(today_events, "today"), _summary(tomorrow_events, "tomorrow")]
    return " ".join(p for p in parts if p)


def _dedupe_and_sort(events: list[CalEvent]) -> list[CalEvent]:
    seen: set[str] = set()
    out: list[CalEvent] = []
    for event in events:
        if event.uid and event.uid in seen:
            continue
        if event.uid:
            seen.add(event.uid)
        out.append(event)
    out.sort(key=lambda e: e.start)
    return out


def _summary(events: list[CalEvent], when: str) -> str:
    prefix = "Today" if when == "today" else "Tomorrow"
    if not events:
        if when == "today":
            return "You have no events today."
        return "Tomorrow you have nothing scheduled."

    formatted = [_format_event(e) for e in events[:MAX_EVENTS_LISTED]]
    if len(events) == 1:
        return f"{prefix} you have {formatted[0]}."
    if len(events) <= MAX_EVENTS_LISTED:
        return f"{prefix} you have {len(events)} events: {', '.join(formatted)}."
    return f"{prefix} you have {len(events)} events, starting with {formatted[0]}."


def _format_event(event: CalEvent) -> str:
    if event.all_day:
        return f"{event.summary} all day"
    time_str = event.start.astimezone().strftime(HOUR_FMT).lstrip("0")
    return f"{event.summary} at {time_str}"
