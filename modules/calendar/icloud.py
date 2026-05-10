from datetime import date, datetime, time, timezone
from typing import Any

import caldav
from caldav.lib.error import AuthorizationError, DAVError

from .types import CalEvent

ICLOUD_URL = "https://caldav.icloud.com"


def fetch_events(config: dict[str, Any], day: date) -> list[CalEvent]:
    apple_id = config.get("apple_id")
    app_password = config.get("app_password")
    if not apple_id or not app_password:
        print("[calendar/icloud] enabled but apple_id or app_password missing.")
        return []

    try:
        client = caldav.DAVClient(url=ICLOUD_URL, username=apple_id, password=app_password)
        principal = client.principal()
        calendars = principal.calendars()
    except AuthorizationError:
        print("[calendar/icloud] authorization failed — check Apple ID and app-specific password.")
        return []
    except (DAVError, OSError) as e:
        print(f"[calendar/icloud] connection error: {e}")
        return []

    start = datetime.combine(day, time.min).astimezone()
    end = datetime.combine(day, time.max).astimezone()

    out: list[CalEvent] = []
    for cal in calendars:
        try:
            results = cal.search(start=start, end=end, event=True, expand=True)
        except (DAVError, OSError):
            continue
        for raw in results:
            evt = _to_calevent(raw)
            if evt:
                out.append(evt)
    return out


def _to_calevent(raw) -> CalEvent | None:
    try:
        comp = raw.icalendar_component
    except (AttributeError, ValueError):
        return None

    summary = str(comp.get("SUMMARY") or "an untitled event")
    uid = str(comp.get("UID") or "")

    dtstart_prop = comp.get("DTSTART")
    if dtstart_prop is None:
        return None
    dtstart = dtstart_prop.dt

    dtend_prop = comp.get("DTEND")
    dtend = dtend_prop.dt if dtend_prop is not None else dtstart

    if isinstance(dtstart, datetime):
        if dtstart.tzinfo is None:
            dtstart = dtstart.replace(tzinfo=timezone.utc)
        if isinstance(dtend, datetime) and dtend.tzinfo is None:
            dtend = dtend.replace(tzinfo=timezone.utc)
        elif not isinstance(dtend, datetime):
            dtend = datetime.combine(dtend, time.min, tzinfo=timezone.utc)
        return CalEvent(summary=summary, start=dtstart, end=dtend, all_day=False, uid=uid)

    start_dt = datetime.combine(dtstart, time.min, tzinfo=timezone.utc)
    if isinstance(dtend, datetime):
        end_dt = dtend if dtend.tzinfo else dtend.replace(tzinfo=timezone.utc)
    else:
        end_dt = datetime.combine(dtend, time.min, tzinfo=timezone.utc)
    return CalEvent(summary=summary, start=start_dt, end=end_dt, all_day=True, uid=uid)
