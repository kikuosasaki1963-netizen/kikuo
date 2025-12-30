"""Gemini TTS integration for natural, expressive speech."""
from __future__ import annotations

import os
import wave
import struct
from pathlib import Path
from google import genai
from google.genai import types

from ..utils.config import Config


# Gemini TTS voice options
GEMINI_VOICES = {
    # Female voices (Japanese-friendly)
    "female_bright": "Aoede",      # Bright female
    "female_warm": "Kore",         # Warm female
    "female_calm": "Leda",         # Calm female
    "female_upbeat": "Zephyr",     # Upbeat female
    # Male voices (Japanese-friendly)
    "male_firm": "Puck",           # Firm male
    "male_calm": "Charon",         # Calm male
    "male_deep": "Orus",           # Deep male
    "male_bright": "Fenrir",       # Bright male
}


class GeminiTTS:
    """Gemini Text-to-Speech client for natural, expressive speech."""

    def __init__(self, config: Config | None = None):
        """Initialize the Gemini TTS client."""
        self.config = config or Config.load()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)

    def synthesize(
        self,
        text: str,
        output_path: str | Path,
        voice_name: str = "Kore",
        style_prompt: str | None = None,
    ) -> Path:
        """Synthesize speech from text.

        Args:
            text: Text to convert to speech.
            output_path: Path to save the audio file.
            voice_name: Gemini voice name (e.g., 'Kore', 'Puck').
            style_prompt: Optional style instruction (e.g., 'cheerfully', 'seriously').

        Returns:
            Path to the saved audio file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build the prompt with optional style
        if style_prompt:
            prompt = f"Say {style_prompt}: {text}"
        else:
            prompt = text

        response = self.client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                ),
            ),
        )

        # Save audio
        audio_data = response.candidates[0].content.parts[0].inline_data.data

        # Convert to MP3 if needed
        if output_path.suffix.lower() == ".mp3":
            # Save as WAV first, then convert
            wav_path = output_path.with_suffix(".wav")
            self._save_wav(audio_data, wav_path)
            self._convert_to_mp3(wav_path, output_path)
            wav_path.unlink()  # Remove temp WAV
        else:
            self._save_wav(audio_data, output_path)

        return output_path

    def synthesize_dialogue(
        self,
        segments: list[dict],
        output_path: str | Path,
        speaker_voices: dict[str, str] | None = None,
        speaker_styles: dict[str, str] | None = None,
    ) -> Path:
        """Synthesize multi-speaker dialogue.

        Args:
            segments: List of {'speaker': str, 'text': str} dicts.
            output_path: Path to save the combined audio.
            speaker_voices: Map of speaker name to voice name.
            speaker_styles: Map of speaker name to style prompt.

        Returns:
            Path to the saved audio file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Default voice assignments
        if speaker_voices is None:
            speakers = list(set(seg["speaker"] for seg in segments))
            speaker_voices = {}
            female_voices = ["Aoede", "Kore", "Leda", "Zephyr"]
            male_voices = ["Puck", "Charon", "Orus", "Fenrir"]

            for i, speaker in enumerate(sorted(speakers)):
                # Alternate between female and male voices
                if i % 2 == 0:
                    speaker_voices[speaker] = female_voices[i // 2 % len(female_voices)]
                else:
                    speaker_voices[speaker] = male_voices[i // 2 % len(male_voices)]

        # Default styles
        if speaker_styles is None:
            speaker_styles = {}

        # Generate audio for each segment
        temp_files = []
        for i, segment in enumerate(segments):
            speaker = segment["speaker"]
            text = segment["text"]
            voice = speaker_voices.get(speaker, "Kore")
            style = speaker_styles.get(speaker)

            temp_path = output_path.parent / f"_temp_segment_{i}.wav"

            try:
                if style:
                    prompt = f"Say {style}: {text}"
                else:
                    prompt = text

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice,
                                )
                            )
                        ),
                    ),
                )

                audio_data = response.candidates[0].content.parts[0].inline_data.data
                self._save_wav(audio_data, temp_path)
                temp_files.append(temp_path)
                print(f"  [{i+1}/{len(segments)}] {speaker}: {text[:30]}...")

            except Exception as e:
                print(f"  Error on segment {i}: {e}")
                continue

        # Combine all segments
        if temp_files:
            self._combine_audio_files(temp_files, output_path)

            # Clean up temp files
            for f in temp_files:
                if f.exists():
                    f.unlink()

        return output_path

    def _save_wav(self, audio_data: bytes, output_path: Path) -> None:
        """Save raw audio data as WAV file."""
        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(24000)
            wf.writeframes(audio_data)

    def _convert_to_mp3(self, wav_path: Path, mp3_path: Path) -> None:
        """Convert WAV to MP3 using ffmpeg."""
        import subprocess
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path)],
            capture_output=True,
        )

    def _combine_audio_files(self, files: list[Path], output_path: Path) -> None:
        """Combine multiple audio files into one."""
        from pydub import AudioSegment

        combined = AudioSegment.empty()
        silence = AudioSegment.silent(duration=300)  # 300ms pause between segments

        for f in files:
            segment = AudioSegment.from_wav(str(f))
            combined += segment + silence

        # Export based on output format
        if output_path.suffix.lower() == ".mp3":
            combined.export(str(output_path), format="mp3")
        else:
            combined.export(str(output_path), format="wav")
