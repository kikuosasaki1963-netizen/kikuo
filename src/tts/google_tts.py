"""Google Cloud Text-to-Speech integration."""
from __future__ import annotations

from pathlib import Path
from google.cloud import texttospeech

from ..utils.config import Config


class GoogleTTS:
    """Google Cloud Text-to-Speech client."""

    def __init__(self, config: Config | None = None):
        """Initialize the TTS client.

        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or Config.load()
        self.client = texttospeech.TextToSpeechClient()

    def synthesize(
        self,
        text: str,
        output_path: str | Path,
        voice_name: str | None = None,
        language_code: str | None = None,
        speaking_rate: float | None = None,
        pitch: float = 0.0,
    ) -> Path:
        """Synthesize speech from text and save to file.

        Args:
            text: Text to convert to speech.
            output_path: Path to save the audio file.
            voice_name: Voice name (e.g., 'ja-JP-Neural2-B').
            language_code: Language code (e.g., 'ja-JP').
            speaking_rate: Speaking rate (0.25 to 4.0, default 1.0).
            pitch: Voice pitch (-20.0 to 20.0, default 0.0).

        Returns:
            Path to the saved audio file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        language_code = language_code or self.config.default_language
        speaking_rate = speaking_rate or self.config.default_speed

        synthesis_input = texttospeech.SynthesisInput(text=text)

        if voice_name:
            voice = texttospeech.VoiceSelectionParams(
                name=voice_name,
                language_code=language_code,
            )
        else:
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            )

        audio_encoding = self._get_audio_encoding(output_path)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=audio_encoding,
            speaking_rate=speaking_rate,
            pitch=pitch,
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        output_path.write_bytes(response.audio_content)
        return output_path

    def synthesize_ssml(
        self,
        ssml: str,
        output_path: str | Path,
        voice_name: str | None = None,
        language_code: str | None = None,
    ) -> Path:
        """Synthesize speech from SSML and save to file.

        Args:
            ssml: SSML markup to convert to speech.
            output_path: Path to save the audio file.
            voice_name: Voice name.
            language_code: Language code.

        Returns:
            Path to the saved audio file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        language_code = language_code or self.config.default_language

        synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

        if voice_name:
            voice = texttospeech.VoiceSelectionParams(
                name=voice_name,
                language_code=language_code,
            )
        else:
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            )

        audio_encoding = self._get_audio_encoding(output_path)
        audio_config = texttospeech.AudioConfig(audio_encoding=audio_encoding)

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        output_path.write_bytes(response.audio_content)
        return output_path

    def list_voices(self, language_code: str | None = None) -> list[dict]:
        """List available voices.

        Args:
            language_code: Filter by language code.

        Returns:
            List of voice information dictionaries.
        """
        response = self.client.list_voices(language_code=language_code)

        voices = []
        for voice in response.voices:
            voices.append(
                {
                    "name": voice.name,
                    "language_codes": list(voice.language_codes),
                    "ssml_gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                    "natural_sample_rate_hertz": voice.natural_sample_rate_hertz,
                }
            )

        return voices

    def _get_audio_encoding(self, output_path: Path) -> texttospeech.AudioEncoding:
        """Get audio encoding based on file extension."""
        suffix = output_path.suffix.lower()
        if suffix == ".mp3":
            return texttospeech.AudioEncoding.MP3
        elif suffix == ".wav":
            return texttospeech.AudioEncoding.LINEAR16
        elif suffix == ".ogg":
            return texttospeech.AudioEncoding.OGG_OPUS
        else:
            return texttospeech.AudioEncoding.MP3
