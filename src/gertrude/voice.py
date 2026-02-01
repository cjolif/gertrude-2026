"""Voice input using OpenAI Whisper API."""

import io
import threading
import wave

import numpy as np
import sounddevice as sd
from openai import OpenAI

SAMPLE_RATE = 16000
CHANNELS = 1


def record_audio() -> bytes:
    """Record audio using push-to-talk (Enter to start, Enter to stop)."""
    input("Press Enter to start recording...")
    print("Recording... (press Enter to stop)")

    audio_chunks: list[np.ndarray] = []
    stop_event = threading.Event()

    def audio_callback(indata, frames, time, status):
        if not stop_event.is_set():
            audio_chunks.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=audio_callback,
    ):
        input()  # Wait for Enter to stop
        stop_event.set()

    if not audio_chunks:
        return b""

    audio_data = np.concatenate(audio_chunks)
    return audio_data.tobytes()


def audio_to_wav(audio_bytes: bytes) -> bytes:
    """Convert raw audio bytes to WAV format."""
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)  # 16-bit audio
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_bytes)
    wav_buffer.seek(0)
    return wav_buffer.read()


def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio using OpenAI Whisper API."""
    if not audio_bytes:
        return ""

    wav_data = audio_to_wav(audio_bytes)
    client = OpenAI()

    # Create a file-like object for the API
    audio_file = io.BytesIO(wav_data)
    audio_file.name = "audio.wav"

    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript.text


def get_voice_input() -> str:
    """Record and transcribe voice input."""
    audio = record_audio()
    if not audio:
        return ""

    print("Transcribing...")
    text = transcribe_audio(audio)
    print(f"You said: {text}")
    return text
