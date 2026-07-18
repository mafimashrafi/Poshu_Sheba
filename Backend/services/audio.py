import os
import subprocess
import tempfile
from typing import Optional

import imageio_ffmpeg
from faster_whisper import WhisperModel

_whisper_model = WhisperModel("small", device="cpu", compute_type="int8")


class AudioConversionError(Exception):
    """Raised when ffmpeg fails to convert the uploaded audio to WAV."""


def _convert_to_wav(raw_audio: bytes, original_filename: str) -> str:
    _, extension = os.path.splitext(original_filename or "")
    if not extension:
        extension = ".mp3"

    input_path = None
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
            f.write(raw_audio)
            input_path = f.name

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        result = subprocess.run(
            [
                ffmpeg, "-y",
                "-i", input_path,
                "-ar", "16000",
                "-ac", "1",
                "-c:a", "pcm_s16le",
                wav_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise AudioConversionError(f"FFmpeg failed:\n{result.stderr}")

        if not os.path.exists(wav_path):
            raise AudioConversionError("WAV file was not created.")

        return wav_path
    finally:
        if input_path and os.path.exists(input_path):
            os.remove(input_path)


def _transcribe_wav(wav_path: str, language: Optional[str] = None) -> str:
    segments, info = _whisper_model.transcribe(wav_path, language=language)
    print(
        f"[whisper] requested language={language!r}, "
        f"detected language={info.language!r} "
        f"(confidence={info.language_probability:.2f})"
    )
    return " ".join(segment.text.strip() for segment in segments).strip()


def transcribe_audio(
    raw_audio: bytes,
    filename: str,
    language: Optional[str] = None,
) -> str:
    wav_path = _convert_to_wav(raw_audio, filename)
    try:
        return _transcribe_wav(wav_path, language=language)
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
