from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .types import CalEvent

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
PROJECT_ROOT = Path(__file__).parent.parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"


def fetch_events(config: dict[str, Any], day: date) -> list[CalEvent]:
    if not CREDENTIALS_FILE.exists():
        print("[calendar/google] enabled but credentials.json not found.")
        return []

    try:
        service = _build_service()
        return _events_for_day(service, day)
    except (HttpError, OSError, ValueError) as e:
        print(f"[calendar/google] error: {e}")
        return []


def _build_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def _events_for_day(service, day: date) -> list[CalEvent]:
    start = datetime.combine(day, time.min).astimezone()
    end = datetime.combine(day, time.max).astimezone()

    cal_list = service.calendarList().list().execute()
    calendars = [
        c for c in cal_list.get("items", [])
        if c.get("primary") or c.get("selected")
    ]

    out: list[CalEvent] = []
    for cal in calendars:
        result = service.events().list(
            calendarId=cal["id"],
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        for raw in result.get("items", []):
            if _declined(raw):
                continue
            evt = _to_calevent(raw)
            if evt:
                out.append(evt)
    return out


def _declined(event: dict) -> bool:
    for attendee in event.get("attendees", []):
        if attendee.get("self") and attendee.get("responseStatus") == "declined":
            return True
    return False


def _to_calevent(raw: dict) -> CalEvent | None:
    summary = raw.get("summary", "an untitled event")
    start = raw.get("start", {})
    end = raw.get("end", {})
    uid = raw.get("iCalUID", "")

    if "dateTime" in start:
        start_dt = datetime.fromisoformat(start["dateTime"])
        end_raw = end.get("dateTime", start["dateTime"])
        end_dt = datetime.fromisoformat(end_raw)
        return CalEvent(summary=summary, start=start_dt, end=end_dt, all_day=False, uid=uid)
    if "date" in start:
        start_dt = datetime.fromisoformat(start["date"]).replace(tzinfo=timezone.utc)
        end_raw = end.get("date", start["date"])
        end_dt = datetime.fromisoformat(end_raw).replace(tzinfo=timezone.utc)
        return CalEvent(summary=summary, start=start_dt, end=end_dt, all_day=True, uid=uid)
    return None
