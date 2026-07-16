import uuid
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Video Generator API", version="0.4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EXECUTOR = ThreadPoolExecutor(max_workers=3)
JOBS: dict = {}
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


class SceneConfig(BaseModel):
    text: str
    voiceover: str
    image_prompt: str
    duration: int = 5
    transition: str = "fade"  # fade, slide, zoom


class CreateVideoRequest(BaseModel):
    prompt: str
    format: str = "16:9"  # 16:9 ou 9:16
    style: str = "corporate"
    music: str = "corporate"  # corporate, cinematic, upbeat
    brand_text: Optional[str] = None
    scenes: Optional[List[SceneConfig]] = None


class PreviewSceneRequest(BaseModel):
    scene: SceneConfig
    format: str = "16:9"


def generate_storyboard(prompt: str, style: str) -> List[dict]:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Tu es un expert en creation de storyboards video. Genere un JSON avec 4 scenes."
            },
            {
                "role": "user",
                "content": f"Cree un storyboard pour: {prompt}. Style: {style}. "
                           f"Format JSON: [{{\"text\": str, \"voiceover\": str, "
                           f"\"image_prompt\": str, \"duration\": int, \"transition\": str}}]"
            }
        ],
        response_format={"type": "json_object"}
    )
    data = json.loads(response.choices[0].message.content)
    return data.get("scenes", [])


def process_video_job(job_id: str, req: dict):
    try:
        from tts import generate_tts_audio
        from renderer import render_scene, concat_scenes, add_music

        JOBS[job_id]["status"] = "generating_storyboard"
        JOBS[job_id]["progress"] = 10

        scenes = req.get("scenes") or generate_storyboard(
            req["prompt"], req.get("style", "corporate")
        )

        JOBS[job_id]["storyboard"] = scenes
        JOBS[job_id]["progress"] = 25

        scene_files = []
        for i, scene in enumerate(scenes):
            JOBS[job_id]["status"] = f"rendering_scene_{i+1}"
            JOBS[job_id]["progress"] = 25 + (i * 15)

            scene_dir = OUTPUT_DIR / job_id / f"scene_{i}"
            scene_dir.mkdir(parents=True, exist_ok=True)

            audio_path = scene_dir / "audio.mp3"
            generate_tts_audio(
                text=scene["voiceover"] if isinstance(scene, dict) else scene.voiceover,
                output_path=audio_path
            )

            video_path = render_scene(
                scene=scene,
                audio_path=audio_path,
                output_path=scene_dir / "scene.mp4",
                video_format=req.get("format", "16:9"),
                brand_text=req.get("brand_text"),
                transition=scene.get("transition", "fade") if isinstance(scene, dict) else scene.transition
            )
            scene_files.append(video_path)

        JOBS[job_id]["status"] = "concatenating"
        JOBS[job_id]["progress"] = 85

        final_path = OUTPUT_DIR / job_id / "final.mp4"
        concat_scenes(scene_files, final_path)

        if req.get("music") and req["music"] != "none":
            add_music(final_path, req["music"])

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["video_url"] = f"/api/videos/download/{job_id}"

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)


@app.post("/api/videos/create")
def create_video(req: CreateVideoRequest):
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {
        "status": "queued",
        "progress": 0,
        "video_url": None,
        "storyboard": None,
        "error": None
    }
    EXECUTOR.submit(process_video_job, job_id, req.model_dump())
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/videos/status/{job_id}")
def get_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]


@app.get("/api/videos/history")
def get_history():
    return [
        {"job_id": jid, **{k: v for k, v in data.items() if k != "storyboard"}}
        for jid, data in JOBS.items()
        if data["status"] == "completed"
    ]


@app.post("/api/videos/preview-scene")
def preview_scene(req: PreviewSceneRequest):
    from tts import generate_tts_audio
    from renderer import render_scene

    job_id = uuid.uuid4().hex
    scene_dir = OUTPUT_DIR / "previews" / job_id
    scene_dir.mkdir(parents=True, exist_ok=True)

    audio_path = scene_dir / "audio.mp3"
    generate_tts_audio(text=req.scene.voiceover, output_path=audio_path)

    video_path = render_scene(
        scene=req.scene.model_dump(),
        audio_path=audio_path,
        output_path=scene_dir / "preview.mp4",
        video_format=req.format,
        brand_text=None,
        transition=req.scene.transition
    )
    return FileResponse(str(video_path), media_type="video/mp4")


@app.get("/api/videos/download/{job_id}")
def download_video(job_id: str):
    video_path = OUTPUT_DIR / job_id / "final.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(str(video_path), media_type="video/mp4",
                        filename=f"video_{job_id}.mp4")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.4"}
