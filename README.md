# Cue

A voice-first morning brief that reads your day aloud. Weather, sports scores, calendar, and a daily quote — delivered in one personalized briefing.

Run it on your laptop, schedule it on a server, or connect it to a Raspberry Pi-based setup for a dedicated physical experience.

## What It Sounds Like

> "Morning Stef, today is September 8th, 2026. Weather in Louisville, KY is partly cloudy with a high of 82 and a low of 68. The Lions won 24 to 17 against the Bears yesterday. Michigan plays Saturday at 3:30 PM against Texas. Today you have team standup at 9:00 AM, dentist at 2:00 PM, and dinner with Emily at 7 at Taco Bell. Tomorrow you have nothing scheduled. Your quote of the day is: The best time to plant a tree was 20 years ago. The second best time is now. — Chinese Proverb. Have a great day, Stef!"

## Why Cue?

Cue started as a web dashboard called Morning WakeUP. It worked, but it still required opening another screen every morning.

I wanted the briefing to be something I could simply hear when I needed it, which led to rebuilding the experience as a lightweight Python application designed to work anywhere — including a dedicated Raspberry Pi device that sits on my desk.


## Quick Start

```bash
git clone https://github.com/StefHogan/cue.git
cd cue
pip install -r requirements.txt
cp config.example.yaml config.yaml
# Edit config.yaml with your details
python main.py
```

That's it. Fill in your name, location, weather API key, and favorite teams — Cue handles the rest.

## Configuration

All personal details live in `config.yaml` (gitignored). Copy the example and fill in what you want:

```bash
cp config.example.yaml config.yaml
```

### User

```yaml
user:
  name: YOUR_NAME           # Cue greets you by name
  location: YOUR_CITY, STATE # Spoken in the weather segment
  latitude: 0.0              # For weather lookup
  longitude: 0.0             # For weather lookup
```

Find your coordinates at [latlong.net](https://www.latlong.net/).

### Weather

```yaml
weather:
  api_key: YOUR_OPENWEATHER_API_KEY
  units: imperial  # imperial (F) or metric (C)
```

Get a free API key at [openweathermap.org](https://openweathermap.org/api) (the free tier is all you need).

### Sports

```yaml
sports_teams:
  - name: Detroit Lions
    sport: football
    league: nfl
```

Add as many teams as you want. Cue uses the ESPN API (no key needed) and will tell you:
- Yesterday's score if your team played
- The next upcoming game

**Common league slugs:** `nfl`, `nba`, `mlb`, `nhl`, `wnba`, `mls`, `mens-college-basketball`, `womens-college-basketball`, `college-football`

The `name` field should match what ESPN calls the team (e.g., "Detroit Lions", "Michigan Wolverines").

### Calendar

Cue reads today's and tomorrow's events. Both providers are optional — enable one, both, or neither.

**Google Calendar:**

```yaml
calendar:
  google:
    enabled: true
```

Requires a Google OAuth Desktop client credential:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project, enable the Google Calendar API
3. Create an OAuth 2.0 Desktop client credential
4. Download `credentials.json` and place it in the project root
5. On first run, a browser window opens for consent — after that, a `token.json` is saved for reuse

**iCloud Calendar:**

```yaml
calendar:
  icloud:
    enabled: true
    apple_id: you@icloud.com
    app_password: xxxx-xxxx-xxxx-xxxx
```

Requires an app-specific password (not your main Apple ID password). Generate one at [appleid.apple.com](https://appleid.apple.com/) under Sign-In and Security > App-Specific Passwords.

If you enable both, events are automatically merged and deduplicated.

### Voice

```yaml
tts:
  voice: en-US-AriaNeural
```

Cue uses [edge-tts](https://github.com/rany2/edge-tts) for natural-sounding neural voices. To see all available voices:

```bash
edge-tts --list-voices
```

Some good English options: `AriaNeural`, `AndrewNeural`, `EmmaNeural`, `AvaNeural`, `BrianNeural`, `JennyNeural`.

## Modules

Each module is independent. If a module's config is missing or an API is down, Cue skips it gracefully and continues with the rest.

| Module | Source | API Key? |
|--------|--------|----------|
| Weather | [OpenWeatherMap](https://openweathermap.org/api) | Yes (free tier) |
| Sports | [ESPN](https://site.api.espn.com) | No |
| Calendar | Google Calendar / iCloud CalDAV | OAuth / App password |
| Quote | [ZenQuotes](https://zenquotes.io/) | No |
| TTS | [edge-tts](https://github.com/rany2/edge-tts) | No |

## Adding Your Own Module

Cue is designed to be extended. To add a new module:

1. Create a file in `modules/` (e.g., `modules/stocks.py`)
2. Write a function that takes `config` and returns a string:
   ```python
   def fetch_stocks(config: dict) -> str:
       # Your logic here
       return "Tesla is up 3% today."
   ```
3. Import and add it to the `assemble_brief()` function in `main.py`

If your module returns an empty string, it's automatically skipped.

## Running on a Schedule

### Any Computer (cron / Task Scheduler)

**Linux/macOS (cron):**
```bash
# Run every morning at 7:00 AM
crontab -e
0 7 * * * cd /path/to/cue && python main.py
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create a Basic Task
3. Set the trigger to daily at your preferred time
4. Action: Start a Program — `python`, arguments: `main.py`, start in: `C:\path\to\cue`

### Raspberry Pi

Cue can also run on a dedicated Raspberry Pi-based device, turning the morning brief into a physical experience rather than something you have to open on a screen.

In my setup, Cue is triggered from the device and plays the briefing aloud through attached audio output.

The public repo focuses on the Cue software itself. Hardware-specific implementation details such as GPIO wiring, device configuration, startup services, and remote-access setup are intentionally not documented here.

The core application runs on Raspberry Pi the same way it does elsewhere:

python main.py 


## Requirements

- Python 3.10+
- Internet connection (all modules fetch live data)
- A speaker or audio output (for TTS playback)

## Security and Local Configuration

Cue relies on local configuration and, depending on which modules you enable, may use API keys, OAuth credentials, app passwords, and cached access tokens.

These files should stay local and should never be committed to Git:

```
config.yaml
.env
credentials.json
token.json
```

This repository includes example configuration files where appropriate, while real credentials and personal settings are excluded through `.gitignore`.

Before making a fork or derivative project public, review your Git history as well as your working directory to make sure no secrets were previously committed.

## License

MIT
