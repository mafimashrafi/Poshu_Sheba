import base64
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
import json

from services.audio import AudioConversionError, transcribe_audio
from services.ai import generate_guidance

router = APIRouter()


@router.post("/generate")
async def generate(
    info: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    images: list[UploadFile] = File(default=[]),
    audio: UploadFile | None = File(default=None),
    animal_type: Optional[str] = Form(None),
):
    info_dict: dict = {}
    if info:
        try:
            info_dict = json.loads(info)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="তথ্য সঠিক ফরম্যাটে পাওয়া যায়নি। আবার চেষ্টা করুন।",
            )
    """Generate preliminary veterinary support guidance."""
    if not text and not images and not audio and not info_dict:
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
            audio_transcript = transcribe_audio(
                raw,
                audio.filename,
                content_type=audio.content_type,
                language="bn",
            )
        except AudioConversionError as e:
            raise HTTPException(
                status_code=500,
                detail=f"অডিও প্রসেস করায় সমস্যা হয়েছে। দয়া করে কথায় লিখুন। \n {str(e)}",
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="অডিও প্রসেস করা যায়নি। অডিও ফাইল দিয়ে আবার চেষ্টা করুন।",
            )

    response_text = generate_guidance(info_dict, text, images_b64, audio_transcript, animal_type)
    return {"response": response_text}
