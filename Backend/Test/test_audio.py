import sys

from services.audio import AudioConversionError, transcribe_audio


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_audio.py /path/to/audio_file")
        sys.exit(1)

    path = sys.argv[1]

    with open(path, "rb") as f:
        raw_audio = f.read()

    print(f"Read {len(raw_audio)} bytes from {path}")
    print("Running ffmpeg conversion + Whisper transcription...")

    try:
        transcript = transcribe_audio(raw_audio, filename=path)
    except AudioConversionError as e:
        print(f"FFmpeg conversion failed: {e}")
        sys.exit(1)

    print("\n--- Transcript ---")
    print(transcript if transcript else "(empty — Whisper heard nothing)")
    print("------------------")


if __name__ == "__main__":
    main()