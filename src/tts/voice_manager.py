"""Voice configuration manager."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VoiceConfig:
    """Voice configuration for a speaker."""

    name: str
    language_code: str = "ja-JP"
    speaking_rate: float = 1.0
    pitch: float = 0.0


# Predefined voice presets for Japanese
JAPANESE_VOICES = {
    "male_1": VoiceConfig(name="ja-JP-Neural2-C", language_code="ja-JP"),
    "male_2": VoiceConfig(name="ja-JP-Neural2-D", language_code="ja-JP"),
    "female_1": VoiceConfig(name="ja-JP-Neural2-B", language_code="ja-JP"),
    "female_2": VoiceConfig(name="ja-JP-Wavenet-A", language_code="ja-JP"),
    "narrator": VoiceConfig(name="ja-JP-Neural2-B", language_code="ja-JP", speaking_rate=0.9),
}

# Predefined voice presets for English
ENGLISH_VOICES = {
    "male_1": VoiceConfig(name="en-US-Neural2-D", language_code="en-US"),
    "male_2": VoiceConfig(name="en-US-Neural2-J", language_code="en-US"),
    "female_1": VoiceConfig(name="en-US-Neural2-F", language_code="en-US"),
    "female_2": VoiceConfig(name="en-US-Neural2-C", language_code="en-US"),
    "narrator": VoiceConfig(name="en-US-Neural2-F", language_code="en-US", speaking_rate=0.9),
}


class VoiceManager:
    """Manage voice configurations for speakers."""

    def __init__(self, default_language: str = "ja-JP"):
        """Initialize voice manager.

        Args:
            default_language: Default language code.
        """
        self.default_language = default_language
        self.speaker_voices: dict[str, VoiceConfig] = {}
        self._voice_index = 0

    def assign_voice(self, speaker: str, voice_config: VoiceConfig) -> None:
        """Assign a specific voice to a speaker.

        Args:
            speaker: Speaker name/identifier.
            voice_config: Voice configuration.
        """
        self.speaker_voices[speaker] = voice_config

    def get_voice(self, speaker: str) -> VoiceConfig:
        """Get voice configuration for a speaker.

        If no voice is assigned, automatically assigns one.

        Args:
            speaker: Speaker name/identifier.

        Returns:
            Voice configuration for the speaker.
        """
        if speaker not in self.speaker_voices:
            self._auto_assign_voice(speaker)

        return self.speaker_voices[speaker]

    def _auto_assign_voice(self, speaker: str) -> None:
        """Automatically assign a voice to a speaker."""
        if self.default_language.startswith("ja"):
            voices = list(JAPANESE_VOICES.values())
        else:
            voices = list(ENGLISH_VOICES.values())

        voice = voices[self._voice_index % len(voices)]
        self.speaker_voices[speaker] = voice
        self._voice_index += 1

    def assign_voices_for_dialogue(self, speakers: set[str]) -> dict[str, VoiceConfig]:
        """Assign distinct voices to multiple speakers.

        Args:
            speakers: Set of speaker names.

        Returns:
            Dictionary mapping speaker names to voice configurations.
        """
        if self.default_language.startswith("ja"):
            available_voices = list(JAPANESE_VOICES.values())
        else:
            available_voices = list(ENGLISH_VOICES.values())

        for i, speaker in enumerate(sorted(speakers)):
            if speaker not in self.speaker_voices:
                voice = available_voices[i % len(available_voices)]
                self.speaker_voices[speaker] = voice

        return self.speaker_voices

    def get_preset(self, preset_name: str) -> VoiceConfig | None:
        """Get a preset voice configuration.

        Args:
            preset_name: Name of the preset (e.g., 'male_1', 'narrator').

        Returns:
            Voice configuration or None if not found.
        """
        if self.default_language.startswith("ja"):
            return JAPANESE_VOICES.get(preset_name)
        else:
            return ENGLISH_VOICES.get(preset_name)
