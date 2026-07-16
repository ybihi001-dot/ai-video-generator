import os
from pathlib import Path
from typing import Optional
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VOICES = {
    "nova": "nova",       # Feminine, natural
    "onyx": "onyx",       # Male, deep
    "alloy": "alloy",     # Neutral
    "echo": "echo",       # Male, clear
    "fable": "fable",     # British accent
    "shimmer": "shimmer"  # Feminine, warm
}


def generate_tts_audio(
    text: str,
    output_path: Path,
    voice: str = "nova",
    enabled: bool = True
) -> Path:
    """
    Generate TTS audio from text using OpenAI TTS API.
    Falls back to silence if disabled or on error.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not enabled or not text.strip():
        _generate_silence(output_path)
        return output_path

    # Validate voice
    voice = voice if voice in VOICES else "nova"

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3"
        )
        response.stream_to_file(str(output_path))
        print(f"[TTS] Generated audio: {output_path.name} ({len(text)} chars)")
    except Exception as e:
        print(f"[TTS] Error: {e} — falling back to silence")
        _generate_silence(output_path)

    return output_path


def _generate_silence(output_path: Path, duration: float = 3.0):
    """Generate a silent MP3 file as fallback."""
    import subprocess
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=stereo",
        "-t", str(duration),
        "-q:a", "9",
        "-acodec", "libmp3lame",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=False)
    print(f"[TTS] Silence generated: {output_path.name}")
