import platform
from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports"
HOUR_FMT = "%#I:%M %p" if platform.system() == "Windows" else "%-I:%M %p"
DAY_FMT = "%B %#d" if platform.system() == "Windows" else "%B %-d"


def fetch_sports(config: dict[str, Any]) -> str:
    teams = config.get("sports_teams") or []
    sentences: list[str] = []
    for team in teams:
        sentences.extend(_team_sentences(team))
    return " ".join(sentences)


def _team_sentences(team: dict[str, Any]) -> list[str]:
    name = team.get("name", "")
    sport = team.get("sport", "")
    league = team.get("league", "")
    if not (name and sport and league):
        return []

    try:
        team_id = _resolve_team_id(sport, league, name)
        if not team_id:
            return []
        schedule = _fetch_schedule(sport, league, team_id)
    except (requests.RequestException, KeyError, ValueError):
        return [f"{name} update unavailable."]

    out: list[str] = []
    recap = _yesterday_recap(schedule, name)
    if recap:
        out.append(recap)
    upcoming = _upcoming_game(schedule, name)
    if upcoming:
        out.append(upcoming)
    return out


def _resolve_team_id(sport: str, league: str, name: str) -> str | None:
    url = f"{ESPN_BASE}/{sport}/{league}/teams"
    data = requests.get(url, params={"limit": 500}, timeout=10).json()
    teams_list = data["sports"][0]["leagues"][0]["teams"]
    name_lower = name.lower()
    for entry in teams_list:
        team = entry["team"]
        for candidate in (team.get("displayName"), team.get("location"), team.get("name")):
            if candidate and candidate.lower() in name_lower:
                return team["id"]
    return None


def _fetch_schedule(sport: str, league: str, team_id: str) -> dict[str, Any]:
    url = f"{ESPN_BASE}/{sport}/{league}/teams/{team_id}/schedule"
    return requests.get(url, timeout=10).json()


def _matches(competitor: dict[str, Any], team_name: str) -> bool:
    name_lower = team_name.lower()
    team = competitor.get("team", {})
    for candidate in (team.get("displayName"), team.get("location"), team.get("name")):
        if candidate and candidate.lower() in name_lower:
            return True
    return False


def _score(competitor: dict[str, Any]) -> int | None:
    s = competitor.get("score")
    if isinstance(s, dict):
        s = s.get("value") or s.get("displayValue")
    if s is None or s == "":
        return None
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


def _short(team: dict[str, Any], default: str) -> str:
    return team.get("shortDisplayName") or team.get("displayName") or default


def _yesterday_recap(schedule: dict[str, Any], team_name: str) -> str | None:
    yesterday = date.today() - timedelta(days=1)
    for event in schedule.get("events", []):
        date_str = event.get("date", "")
        try:
            event_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            continue
        if event_dt.astimezone().date() != yesterday:
            continue
        comp = (event.get("competitions") or [{}])[0]
        if not comp.get("status", {}).get("type", {}).get("completed"):
            continue
        return _format_recap(comp, team_name)
    return None


def _format_recap(comp: dict[str, Any], team_name: str) -> str | None:
    competitors = comp.get("competitors", [])
    if len(competitors) != 2:
        return None
    me = next((c for c in competitors if _matches(c, team_name)), None)
    them = next((c for c in competitors if c is not me), None) if me else None
    if not me or not them:
        return None
    me_score = _score(me)
    them_score = _score(them)
    if me_score is None or them_score is None:
        return None
    me_label = _short(me["team"], team_name)
    opp = _short(them["team"], "their opponent")
    if me_score > them_score:
        return f"{me_label} won {me_score} to {them_score} against {opp} yesterday."
    if me_score < them_score:
        return f"{me_label} lost {me_score} to {them_score} against {opp} yesterday."
    return f"{me_label} tied {opp} {me_score} to {them_score} yesterday."


def _upcoming_game(schedule: dict[str, Any], team_name: str) -> str | None:
    now = datetime.now(timezone.utc)
    candidates = []
    for event in schedule.get("events", []):
        date_str = event.get("date", "")
        try:
            event_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            continue
        if event_dt < now:
            continue
        comp = (event.get("competitions") or [{}])[0]
        state = comp.get("status", {}).get("type", {}).get("state", "")
        if state == "post":
            continue
        candidates.append((event_dt, comp))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    event_dt, comp = candidates[0]
    return _format_upcoming(comp, event_dt, team_name)


def _format_upcoming(comp: dict[str, Any], event_dt: datetime, team_name: str) -> str | None:
    competitors = comp.get("competitors", [])
    if len(competitors) != 2:
        return None
    me = next((c for c in competitors if _matches(c, team_name)), None)
    them = next((c for c in competitors if c is not me), None) if me else None
    if not me or not them:
        return None
    me_label = _short(me["team"], team_name)
    opp = _short(them["team"], "their opponent")
    verb = "play" if me_label.lower().endswith("s") else "plays"
    when = _humanize(event_dt)
    return f"{me_label} {verb} {when} against {opp}."


def _humanize(event_dt: datetime) -> str:
    local_dt = event_dt.astimezone()
    diff = (local_dt.date() - date.today()).days
    time_str = local_dt.strftime(HOUR_FMT).lstrip("0")
    if diff == 0:
        return f"today at {time_str}"
    if diff == 1:
        return f"tomorrow at {time_str}"
    if 2 <= diff <= 6:
        return f"{local_dt.strftime('%A')} at {time_str}"
    return f"on {local_dt.strftime(DAY_FMT)}"
