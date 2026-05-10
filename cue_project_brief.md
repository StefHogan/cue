# Cue — Project Brief for Claude Code

## What is Cue?

Cue is a physical desk assistant built on a Raspberry Pi. When you press a button, it lights up and reads aloud a personalized morning brief. Think of it as a smart, voice-first daily summary that lives on your desk — no phone, no screen, just a button press.

The goal is for this to be a **public, modular GitHub repo** so others can clone it, fill in a config file with their own details, and have their own Cue device.

---

## Hardware Target

- **Raspberry Pi 4** (with built-in WiFi)
- Physical button (GPIO)
- Speaker (via 3.5mm or USB audio)
- LED indicator light (GPIO)
- SD card running Raspberry Pi OS (headless setup)
- Deployed via SSH from a Windows PC; code lives on GitHub

---

## V1 Features (build this first)

When the button is pressed, Cue speaks a morning brief that includes:

1. **Greeting + date** — "Morning Stef, today is May 10th, 2026."
2. **Weather** — current conditions and high/low for the day (Louisville, KY — but configurable)
3. **Sports scores** — scores from yesterday's games for configured teams
4. **Upcoming games** — games today or next for configured teams
5. **Calendar events** — today's events and a look at tomorrow (Google Calendar)
6. **Inspirational quote** — one quote to close out the brief

Example output:
> "Morning Stef, today is May 10th, 2026. Weather in Louisville looks great, high of 75 and cloudy. Michigan men's basketball won 76-72 against Ohio State yesterday. The women's team plays tonight at 7pm against UNC. The Lions play Sunday against the Raiders. You have no events today — tomorrow you have dinner with Anna at 7pm. 'The only way to do great work is to love what you do.' Have a great day, Stef!"

---

## V2 Features (plan for, don't build yet)

- Workout stats from the previous day (Garmin or Oura Ring integration)
- Stock watchlist performance
- Troubleshooting section (see notes below)
- Optional local status/health dashboard web page

---

## Modular Design — Critical

Everything personal must live in a **`config.yaml`** file that is listed in `.gitignore`. The repo ships with a `config.example.yaml` showing all the fields someone needs to fill in. This way:

- The repo is fully public with no personal data
- A friend clones it, fills in `config.yaml`, and has their own Cue

### Config fields to support:
```yaml
user:
  name: Stef
  location: Louisville, KY
  latitude: 38.2527
  longitude: -85.7585

sports_teams:
  - name: Michigan Wolverines Men's Basketball
    sport: basketball
    league: NCAA
  - name: Michigan Wolverines Women's Basketball
    sport: basketball
    league: NCAA
  - name: Detroit Lions
    sport: football
    league: NFL

calendar:
  google_calendar_enabled: true

weather:
  api_key: YOUR_OPENWEATHER_API_KEY

tts:
  voice: en-US  # text-to-speech voice setting

quote:
  source: api  # or "local" for a static list
```

---

## Suggested Repo Structure

```
cue/
├── main.py                  # Entry point — listens for button press, runs brief
├── config.example.yaml      # Template config (committed to repo)
├── config.yaml              # Personal config (gitignored)
├── requirements.txt
├── README.md
├── modules/
│   ├── weather.py           # Fetches weather via OpenWeatherMap API
│   ├── sports.py            # Fetches scores/schedule (ESPN API or similar)
│   ├── calendar_events.py   # Google Calendar integration
│   ├── quote.py             # Daily quote
│   └── tts.py               # Text-to-speech (pyttsx3 or gTTS)
├── scripts/
│   └── install.sh           # Setup script for new Pi installs
└── hardware/
    └── wiring_guide.md      # GPIO pin layout for button + LED
```

---

## APIs and Services

| Feature | Service | Notes |
|---|---|---|
| Weather | OpenWeatherMap | Free tier is fine |
| Sports | ESPN API (unofficial) or SportsDB | No key needed for ESPN |
| Calendar | Google Calendar API | Requires OAuth setup |
| Text-to-speech | pyttsx3 (offline) or gTTS (online) | pyttsx3 preferred for offline use |
| Quotes | They Said So API or local JSON file | Local file is simpler |

---

## V2 Troubleshooting Notes (include in repo eventually)

When building V2, include a troubleshooting section in the README covering:
- Device speaks partial brief / cuts off mid-sentence
- How to SSH in and check the log file remotely
- Common failure points: WiFi drop, expired API keys, Google OAuth token expiry, SD card corruption, loose wiring on GPIO
- Optional local status/health dashboard (lightweight web page served from the Pi)

---

## Deployment Flow

1. Developer writes code on Windows PC
2. Pushes to GitHub
3. SSH into Pi, pull latest from GitHub
4. Pi runs `main.py` on boot (via cron or systemd service)

---

## What to Build First

Start with a working Python script that:
1. Reads from `config.yaml`
2. Fetches weather, sports, and a quote
3. Assembles a spoken brief as a string
4. Speaks it aloud using TTS

No GPIO/button yet — just run it with `python main.py` and confirm the voice output works. Hardware integration comes after the software core is solid.
