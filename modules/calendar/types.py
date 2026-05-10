from dataclasses import dataclass
from datetime import datetime


@dataclass
class CalEvent:
    summary: str
    start: datetime
    end: datetime
    all_day: bool
    uid: str
