import base64
from typing import Optional
import os
import subprocess
import tempfile

import imageio_ffmpeg
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
import ollama
import requests


app = FastAPI()


@app.post("/generate")
async def generate(
        text: Optional[str] = Form(None),
        images: list[UploadFile] = File(default=[]),
        audio: UploadFile | None = File(default=None),
):
    if not text and not images and not audio:
        raise HTTPException(
            status_code=400,
            detail="লিখিত তথ্য, ছবি অথবা অডিও এর থেকে কমপক্ষে একটি দিন।",
        )

    images_b64: list[str] = []
    wav_b64 = None

    if images:
        for img in images:
            raw = await img.read()
            images_b64.append(base64.b64encode(raw).decode("utf-8"))
    if audio is not None:
        raw = await audio.read()

        _, extension = os.path.splitext(audio.filename)
        if not extension:
            extension = ".mp3"

        mp_path = None
        wav_path = None

        try:
            # Save uploaded audio
            with tempfile.NamedTemporaryFile(
                    suffix=extension,
                    delete=False
            ) as input_file:
                input_file.write(raw)
                mp_path = input_file.name

            # Temporary wav output
            with tempfile.NamedTemporaryFile(
                    suffix=".wav",
                    delete=False
            ) as output_file:
                wav_path = output_file.name

            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

            result = subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-i", mp_path,
                    "-ar", "16000",
                    "-ac", "1",
                    "-c:a", "pcm_s16le",
                    wav_path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print(result.stderr)

            if not os.path.exists(wav_path):
                raise HTTPException(
                    status_code=500,
                    detail="WAV file was not created."
                )

            with open(wav_path, "rb") as f:
                wav_bytes = f.read()

            wav_b64 = base64.b64encode(wav_bytes).decode("utf-8")

            print("Original bytes:", len(raw))
            print("WAV bytes:", len(wav_bytes))
            print("WAV Base64 length:", len(wav_b64))

        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"FFmpeg failed:\n{e.stderr}"
            )

        finally:
            if mp_path and os.path.exists(mp_path):
                os.remove(mp_path)

            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)

    print("Original bytes:", len(raw))
    print("WAV Base64 length:", len(wav_b64) if wav_b64 else 0)

    message = {
        "role": "user",
        "content": text or "",
    }

    if images_b64:
        message["images"] = images_b64

    if wav_b64:
        message["audio"] = [wav_b64]

    print(message.keys())

    payload = {
        "model": "gemma4:e4b-it-q4_K_M",
        "messages": [message],
        "stream": False,
    }

    r = requests.post(
        "http://localhost:11434/api/chat",
        json=payload,
    )

    print(r.status_code)
    print(r.text)

    return r.json()