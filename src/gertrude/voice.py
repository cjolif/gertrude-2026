"""Voice input using OpenAI Whisper API."""

import io
import time
import wave

import numpy as np
import sounddevice as sd
from openai import OpenAI

SAMPLE_RATE = 16000
CHANNELS = 1

# Silence detection parameters
SILENCE_THRESHOLD = 250  # Amplitude threshold for silence (int16 range: -32768 to 32767)
SILENCE_DURATION = 1.5  # Seconds of silence before stopping
SPEECH_THRESHOLD = 500  # Amplitude threshold to detect speech started
MIN_SPEECH_DURATION = 0.3  # Minimum seconds of speech before enabling silence detection


def record_audio() -> bytes:
    """Record audio with automatic silence detection."""
    input("Press Enter to start recording...")
    print("Listening... (will stop when you stop speaking)")

    audio_chunks: list[np.ndarray] = []
    speech_started = False
    speech_start_time = 0.0
    silence_start_time = 0.0
    stop_recording = False

    def audio_callback(indata, frames, time_info, status):
        nonlocal speech_started, speech_start_time, silence_start_time, stop_recording

        if stop_recording:
            return

        audio_chunks.append(indata.copy())

        # Calculate amplitude (RMS)
        amplitude = np.abs(indata).mean()

        current_time = time.time()

        if not speech_started:
            # Wait for speech to start
            if amplitude > SPEECH_THRESHOLD:
                speech_started = True
                speech_start_time = current_time
                silence_start_time = 0.0
        else:
            # Speech has started, monitor for silence
            if amplitude < SILENCE_THRESHOLD:
                if silence_start_time == 0.0:
                    silence_start_time = current_time
                elif current_time - silence_start_time > SILENCE_DURATION:
                    # Check minimum speech duration
                    if current_time - speech_start_time > MIN_SPEECH_DURATION:
                        stop_recording = True
            else:
                # Reset silence timer when speech detected
                silence_start_time = 0.0

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=audio_callback,
        blocksize=int(SAMPLE_RATE * 0.1),  # 100ms blocks
    ):
        # Poll until recording should stop
        while not stop_recording:
            sd.sleep(100)

    if not audio_chunks:
        return b""

    print("Processing...")
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
