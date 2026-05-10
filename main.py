import platform
from datetime import date
from pathlib import Path

import yaml

from modules.calendar import fetch_calendar
from modules.quote import fetch_quote
from modules.sports import fetch_sports
from modules.tts import speak
from modules.weather import fetch_weather

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            "config.yaml not found. Copy config.example.yaml to config.yaml and fill in your details."
        )
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def assemble_brief(config: dict) -> str:
    name = config["user"].get("name", "there")
    day_fmt = "%B %#d, %Y" if platform.system() == "Windows" else "%B %-d, %Y"
    today = date.today().strftime(day_fmt)

    parts = [
        f"Morning {name}, today is {today}.",
        fetch_weather(config),
        fetch_sports(config),
        fetch_calendar(config),
        fetch_quote(),
        f"Have a great day, {name}!",
    ]
    return " ".join(p for p in parts if p)


def main() -> None:
    config = load_config()
    brief = assemble_brief(config)
    print(brief)
    speak(brief, config)


if __name__ == "__main__":
    main()
