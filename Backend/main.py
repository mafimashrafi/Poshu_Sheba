import base64
from typing import Optional

from Middleware.Audio2Text import AudioConversionError, transcribe_audio
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
import ollama

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
    audio_transcript: Optional[str] = None

    if images:
        for img in images:
            raw = await img.read()
            images_b64.append(base64.b64encode(raw).decode("utf-8"))

    if audio is not None:
        raw = await audio.read()
        try:
            audio_transcript = transcribe_audio(raw, audio.filename, language="bn")
        except AudioConversionError as e:
            raise HTTPException(status_code=500, detail=f"অডিও প্রসেস করায় সমস্যা হয়েছে। দয়া করে কথায় লিখুন। \ন {str(e)}")

    content_parts = []
    if text:
        content_parts.append(text)
    if audio_transcript:
        content_parts.append(
            "[Audio transcript — note: this was transcribed from Bengali "
            "(Bangla) speech using automatic speech recognition, which "
            "sometimes mistakenly renders Bangla in Hindi wording/script "
            "due to phonetic similarity. Interpret the following as "
            f"Bengali speech and reply entirely in Bengali]: {audio_transcript}")
    content = "\n\n".join(content_parts)
    print(content)

    message = {"role": "user", "content": content}
    if images_b64:
        message["images"] = images_b64

    try:
        response = ollama.chat(model="gemma4:e4b-it-q4_K_M", messages=[
            message])
    except ollama.ResponseError as e:
        raise HTTPException( status_code=e.status_code or 502, detail=f"এই মুহূর্তে AI সাহায্য করতে পারছে না। বিকল্প উপায় দেখুন বা আবার চেষ্টা করুন।\n{str(e)}", )
    except ollama.RequestError as e:
        raise HTTPException( status_code=503, detail=f"AI পর্যন্ত কল যায়নি। বিকল্প উপায় দেখুন।\n{str(e)}", )
    return {"response": response["message"]["content"]}