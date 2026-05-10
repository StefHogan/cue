import asyncio
import tempfile
from pathlib import Path
from typing import Any

import edge_tts
from playsound3 import playsound

DEFAULT_VOICE = "en-US-AriaNeural"


def speak(text: str, config: dict[str, Any]) -> None:
    voice = (config.get("tts", {}) or {}).get("voice") or DEFAULT_VOICE

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp_path = tmp.name

    try:
        asyncio.run(_synthesize(text, voice, tmp_path))
        playsound(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


async def _synthesize(text: str, voice: str, output_path: str) -> None:
    await edge_tts.Communicate(text, voice).save(output_path)
