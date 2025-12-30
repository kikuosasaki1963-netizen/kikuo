"""Audio track builder for video production."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from pydub import AudioSegment

from .processor import AudioProcessor


@dataclass
class AudioClip:
    """An audio clip with timing information."""

    audio: AudioSegment
    start_ms: int = 0
    label: str = ""


class TrackBuilder:
    """Build audio tracks for video production."""

    def __init__(self):
        """Initialize track builder."""
        self.clips: list[AudioClip] = []
        self.processor = AudioProcessor()

    def add_clip(
        self,
        audio: AudioSegment | str | Path,
        start_ms: int = 0,
        label: str = "",
    ) -> "TrackBuilder":
        """Add an audio clip to the track.

        Args:
            audio: AudioSegment or path to audio file.
            start_ms: Start position in milliseconds.
            label: Optional label for the clip.

        Returns:
            Self for chaining.
        """
        if isinstance(audio, (str, Path)):
            audio = self.processor.load(audio)

        self.clips.append(AudioClip(audio=audio, start_ms=start_ms, label=label))
        return self

    def add_sequential(
        self,
        audio_files: list[str | Path],
        gap_ms: int = 0,
        start_ms: int = 0,
    ) -> "TrackBuilder":
        """Add multiple audio files sequentially.

        Args:
            audio_files: List of paths to audio files.
            gap_ms: Gap between clips in milliseconds.
            start_ms: Start position for first clip.

        Returns:
            Self for chaining.
        """
        current_position = start_ms

        for file_path in audio_files:
            audio = self.processor.load(file_path)
            self.clips.append(
                AudioClip(audio=audio, start_ms=current_position, label=str(file_path))
            )
            current_position += len(audio) + gap_ms

        return self

    def build(self, normalize: bool = True) -> AudioSegment:
        """Build the final audio track.

        Args:
            normalize: Whether to normalize the final audio.

        Returns:
            Combined AudioSegment.
        """
        if not self.clips:
            return AudioSegment.empty()

        max_end = max(clip.start_ms + len(clip.audio) for clip in self.clips)
        result = AudioSegment.silent(duration=max_end)

        for clip in sorted(self.clips, key=lambda c: c.start_ms):
            result = result.overlay(clip.audio, position=clip.start_ms)

        if normalize:
            result = self.processor.normalize(result)

        return result

    def build_with_bgm(
        self,
        bgm_path: str | Path,
        bgm_volume_db: float = -10.0,
        fade_in_ms: int = 2000,
        fade_out_ms: int = 2000,
    ) -> AudioSegment:
        """Build track with background music.

        Args:
            bgm_path: Path to background music file.
            bgm_volume_db: Volume adjustment for BGM in dB.
            fade_in_ms: BGM fade in duration.
            fade_out_ms: BGM fade out duration.

        Returns:
            Combined AudioSegment with BGM.
        """
        voice_track = self.build(normalize=True)
        track_duration = len(voice_track)

        bgm = self.processor.load(bgm_path)

        if len(bgm) < track_duration:
            loops_needed = (track_duration // len(bgm)) + 1
            bgm = bgm * loops_needed

        bgm = bgm[:track_duration]

        bgm = bgm.apply_gain(bgm_volume_db)
        bgm = self.processor.fade_in(bgm, fade_in_ms)
        bgm = self.processor.fade_out(bgm, fade_out_ms)

        return bgm.overlay(voice_track)

    def save(
        self,
        output_path: str | Path,
        format: str = "mp3",
        normalize: bool = True,
    ) -> Path:
        """Build and save the track.

        Args:
            output_path: Output file path.
            format: Audio format.
            normalize: Whether to normalize.

        Returns:
            Path to saved file.
        """
        audio = self.build(normalize=normalize)
        return self.processor.save(audio, output_path, format=format)

    def get_duration_ms(self) -> int:
        """Get total track duration in milliseconds.

        Returns:
            Duration in milliseconds.
        """
        if not self.clips:
            return 0
        return max(clip.start_ms + len(clip.audio) for clip in self.clips)

    def clear(self) -> None:
        """Clear all clips from the track."""
        self.clips.clear()
