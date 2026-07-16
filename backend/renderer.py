import subprocess
import requests
from pathlib import Path
from typing import Optional, List

PEXELS_API_KEY = __import__('os').getenv("PEXELS_API_KEY", "")

# Video format dimensions
FORMATS = {
    "16:9": {"w": 1280, "h": 720},
    "9:16": {"w": 720, "h": 1280},
    "1:1":  {"w": 720, "h": 720},
}

# Music mood frequencies (generated via ffmpeg sine waves as placeholder)
MUSIC_MOODS = {
    "corporate": {"freq": 440, "vol": 0.08},
    "cinematic": {"freq": 220, "vol": 0.06},
    "upbeat":    {"freq": 660, "vol": 0.10},
}


def fetch_pexels_image(query: str, output_path: Path) -> Path:
    """Download a stock image from Pexels API."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not PEXELS_API_KEY:
        _generate_placeholder_image(output_path, query)
        return output_path

    try:
        headers = {"Authorization": PEXELS_API_KEY}
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            timeout=10
        )
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if photos:
            img_url = photos[0]["src"]["large"]
            img_data = requests.get(img_url, timeout=15).content
            output_path.write_bytes(img_data)
            return output_path
    except Exception as e:
        print(f"[PEXELS] Error: {e}")

    _generate_placeholder_image(output_path, query)
    return output_path


def _generate_placeholder_image(output_path: Path, text: str = "Scene"):
    """Generate a colored placeholder image with text using FFmpeg."""
    safe_text = text[:30].replace("'", "").replace('"', '')
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=0x1a1a2e:size=1280x720:rate=1",
        "-vf", f"drawtext=text='{safe_text}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2",
        "-frames:v", "1",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=False)


def render_scene(
    scene: dict,
    audio_path: Path,
    output_path: Path,
    video_format: str = "16:9",
    brand_text: Optional[str] = None,
    transition: str = "fade"
) -> Path:
    """Render a single scene: image + audio + subtitles + branding."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dims = FORMATS.get(video_format, FORMATS["16:9"])
    w, h = dims["w"], dims["h"]

    image_path = output_path.parent / "bg.jpg"
    fetch_pexels_image(
        scene.get("image_prompt", "abstract background"),
        image_path
    )

    subtitle = scene.get("text", "")[:80].replace("'", "").replace('"', '')
    duration = scene.get("duration", 5)

    # Build video filter chain
    vf_parts = [
        f"scale={w}:{h}:force_original_aspect_ratio=increase",
        f"crop={w}:{h}",
    ]

    # Subtitle overlay
    if subtitle:
        vf_parts.append(
            f"drawtext=text='{subtitle}':fontcolor=white:fontsize=28"
            f":x=(w-text_w)/2:y=h-80:box=1:boxcolor=black@0.6:boxborderw=8"
        )

    # Brand watermark
    if brand_text:
        safe_brand = brand_text[:20].replace("'", "").replace('"', '')
        vf_parts.append(
            f"drawtext=text='{safe_brand}':fontcolor=white@0.7:fontsize=20"
            f":x=w-text_w-20:y=20"
        )

    # Transition effect (fade in)
    if transition in ("fade", "zoom"):
        vf_parts.append(f"fade=t=in:st=0:d=0.5")
    if transition == "zoom":
        vf_parts.append("zoompan=z='min(zoom+0.001,1.3)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'")

    vf = ",".join(vf_parts)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "30",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "28",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[RENDERER] FFmpeg error: {result.stderr[-500:]}")

    return output_path


def concat_scenes(scene_files: List[Path], output_path: Path) -> Path:
    """Concatenate scene videos into one final video."""
    output_path = Path(output_path)
    list_file = output_path.parent / "filelist.txt"

    with open(list_file, "w") as f:
        for sf in scene_files:
            f.write(f"file '{sf.resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[CONCAT] FFmpeg error: {result.stderr[-500:]}")

    list_file.unlink(missing_ok=True)
    return output_path


def add_music(video_path: Path, mood: str = "corporate") -> Path:
    """Mix background music (generated sine tone) with video audio."""
    mood_cfg = MUSIC_MOODS.get(mood, MUSIC_MOODS["corporate"])
    freq = mood_cfg["freq"]
    vol = mood_cfg["vol"]

    temp_path = video_path.parent / "final_music.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-f", "lavfi",
        "-i", f"sine=frequency={freq}:sample_rate=44100",
        "-filter_complex",
        f"[0:a]volume=1.0[a0];[1:a]volume={vol}[a1];[a0][a1]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        str(temp_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        temp_path.replace(video_path)
        print(f"[MUSIC] Added {mood} music to {video_path.name}")
    else:
        print(f"[MUSIC] Error: {result.stderr[-300:]}")
        temp_path.unlink(missing_ok=True)

    return video_path
