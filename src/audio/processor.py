"""Audio processing utilities."""
from __future__ import annotations

from pathlib import Path
from pydub import AudioSegment


class AudioProcessor:
    """Audio processing and manipulation."""

    @staticmethod
    def load(file_path: str | Path) -> AudioSegment:
        """Load an audio file.

        Args:
            file_path: Path to the audio file.

        Returns:
            AudioSegment object.
        """
        path = Path(file_path)
        return AudioSegment.from_file(path)

    @staticmethod
    def save(audio: AudioSegment, output_path: str | Path, format: str = "mp3") -> Path:
        """Save audio to file.

        Args:
            audio: AudioSegment to save.
            output_path: Output file path.
            format: Audio format (mp3, wav).

        Returns:
            Path to saved file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        audio.export(output_path, format=format)
        return output_path

    @staticmethod
    def concatenate(segments: list[AudioSegment]) -> AudioSegment:
        """Concatenate multiple audio segments.

        Args:
            segments: List of AudioSegment objects.

        Returns:
            Combined AudioSegment.
        """
        if not segments:
            return AudioSegment.empty()

        result = segments[0]
        for segment in segments[1:]:
            result += segment

        return result

    @staticmethod
    def add_silence(duration_ms: int) -> AudioSegment:
        """Create a silent audio segment.

        Args:
            duration_ms: Duration in milliseconds.

        Returns:
            Silent AudioSegment.
        """
        return AudioSegment.silent(duration=duration_ms)

    @staticmethod
    def insert_silence_between(
        segments: list[AudioSegment], silence_ms: int = 500
    ) -> AudioSegment:
        """Concatenate segments with silence between them.

        Args:
            segments: List of AudioSegment objects.
            silence_ms: Silence duration between segments in milliseconds.

        Returns:
            Combined AudioSegment with silence between parts.
        """
        if not segments:
            return AudioSegment.empty()

        silence = AudioSegment.silent(duration=silence_ms)
        result = segments[0]

        for segment in segments[1:]:
            result += silence + segment

        return result

    @staticmethod
    def fade_in(audio: AudioSegment, duration_ms: int = 100) -> AudioSegment:
        """Apply fade in effect.

        Args:
            audio: AudioSegment to process.
            duration_ms: Fade duration in milliseconds.

        Returns:
            Processed AudioSegment.
        """
        return audio.fade_in(duration_ms)

    @staticmethod
    def fade_out(audio: AudioSegment, duration_ms: int = 100) -> AudioSegment:
        """Apply fade out effect.

        Args:
            audio: AudioSegment to process.
            duration_ms: Fade duration in milliseconds.

        Returns:
            Processed AudioSegment.
        """
        return audio.fade_out(duration_ms)

    @staticmethod
    def normalize(audio: AudioSegment, target_dBFS: float = -20.0) -> AudioSegment:
        """Normalize audio volume.

        Args:
            audio: AudioSegment to normalize.
            target_dBFS: Target volume in dBFS.

        Returns:
            Normalized AudioSegment.
        """
        change_in_dBFS = target_dBFS - audio.dBFS
        return audio.apply_gain(change_in_dBFS)

    @staticmethod
    def overlay(
        base: AudioSegment, overlay: AudioSegment, position_ms: int = 0, gain_dB: float = 0
    ) -> AudioSegment:
        """Overlay one audio on top of another.

        Args:
            base: Base audio segment.
            overlay: Audio to overlay.
            position_ms: Position to start overlay in milliseconds.
            gain_dB: Volume adjustment for overlay in dB.

        Returns:
            Combined AudioSegment.
        """
        if gain_dB != 0:
            overlay = overlay.apply_gain(gain_dB)

        return base.overlay(overlay, position=position_ms)

    @staticmethod
    def get_duration_ms(audio: AudioSegment) -> int:
        """Get audio duration in milliseconds.

        Args:
            audio: AudioSegment.

        Returns:
            Duration in milliseconds.
        """
        return len(audio)
