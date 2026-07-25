import base64
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from Backend.services.audio import AudioConversionError, transcribe_audio
from Backend.services.ai import generate_guidance

router = APIRouter()


@router.post("/generate")
async def generate(
    text: Optional[str] = Form(None),
    images: list[UploadFile] = File(default=[]),
    audio: UploadFile | None = File(default=None),
    animal_type: Optional[str] = Form(None),
):
    """Generate preliminary veterinary support guidance."""
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
            raise HTTPException(
                status_code=500,
                detail=f"অডিও প্রসেস করায় সমস্যা হয়েছে। দয়া করে কথায় লিখুন। \n {str(e)}",
            )

    response_text = generate_guidance(text, images_b64, audio_transcript, animal_type)
    return {"response": response_text}
