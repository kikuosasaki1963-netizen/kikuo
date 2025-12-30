"""Voice Generation Agent core."""
from __future__ import annotations

import tempfile
from pathlib import Path
from pydub import AudioSegment

from .readers import read_word_file, read_google_doc, parse_dialogue_script, parse_narration_script
from .readers.script_parser import DialogueScript
from .tts import GoogleTTS, VoiceManager
from .audio import AudioProcessor, TrackBuilder
from .utils.config import Config


class VoiceAgent:
    """Voice generation agent for document-to-speech conversion."""

    def __init__(self, config: Config | None = None):
        """Initialize the voice agent.

        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or Config.load()
        self.tts = GoogleTTS(self.config)
        self.voice_manager = VoiceManager(self.config.default_language)
        self.processor = AudioProcessor()

    def convert_document(
        self,
        input_path: str | Path,
        output_path: str | Path,
        voice_name: str | None = None,
        language_code: str | None = None,
        speaking_rate: float | None = None,
    ) -> Path:
        """Convert a document (Word or text) to speech.

        Args:
            input_path: Path to the input document.
            output_path: Path for the output audio file.
            voice_name: Voice to use.
            language_code: Language code.
            speaking_rate: Speaking rate.

        Returns:
            Path to the generated audio file.
        """
        input_path = Path(input_path)

        if input_path.suffix.lower() == ".docx":
            text = read_word_file(input_path)
        else:
            text = input_path.read_text(encoding="utf-8")

        return self.tts.synthesize(
            text=text,
            output_path=output_path,
            voice_name=voice_name,
            language_code=language_code,
            speaking_rate=speaking_rate,
        )

    def convert_google_doc(
        self,
        document_id: str,
        output_path: str | Path,
        voice_name: str | None = None,
        language_code: str | None = None,
        speaking_rate: float | None = None,
    ) -> Path:
        """Convert a Google Doc to speech.

        Args:
            document_id: Google Docs document ID.
            output_path: Path for the output audio file.
            voice_name: Voice to use.
            language_code: Language code.
            speaking_rate: Speaking rate.

        Returns:
            Path to the generated audio file.
        """
        text = read_google_doc(document_id, self.config)

        return self.tts.synthesize(
            text=text,
            output_path=output_path,
            voice_name=voice_name,
            language_code=language_code,
            speaking_rate=speaking_rate,
        )

    def generate_dialogue(
        self,
        script_path: str | Path,
        output_path: str | Path,
        silence_between_ms: int = 500,
    ) -> Path:
        """Generate dialogue audio from a script file.

        Args:
            script_path: Path to the dialogue script.
            output_path: Path for the output audio file.
            silence_between_ms: Silence between lines in milliseconds.

        Returns:
            Path to the generated audio file.
        """
        script_path = Path(script_path)
        output_path = Path(output_path)

        script = parse_dialogue_script(script_path)
        self.voice_manager.assign_voices_for_dialogue(script.speakers)

        audio_segments = []

        with tempfile.TemporaryDirectory() as temp_dir:
            for i, line in enumerate(script.lines):
                voice_config = self.voice_manager.get_voice(line.speaker)
                temp_file = Path(temp_dir) / f"line_{i:04d}.mp3"

                self.tts.synthesize(
                    text=line.text,
                    output_path=temp_file,
                    voice_name=voice_config.name,
                    language_code=voice_config.language_code,
                    speaking_rate=voice_config.speaking_rate,
                )

                audio_segments.append(self.processor.load(temp_file))

            combined = self.processor.insert_silence_between(
                audio_segments, silence_between_ms
            )
            return self.processor.save(combined, output_path)

    def generate_narration(
        self,
        input_path: str | Path,
        output_path: str | Path,
        voice_name: str | None = None,
        section_silence_ms: int = 1000,
        split_chapters: bool = False,
    ) -> list[Path]:
        """Generate narration audio from a markdown/text file.

        Args:
            input_path: Path to the input file.
            output_path: Path for the output audio file.
            voice_name: Voice to use.
            section_silence_ms: Silence between sections in milliseconds.
            split_chapters: If True, generate separate files for each section.

        Returns:
            List of paths to generated audio files.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        sections = parse_narration_script(input_path)
        voice = voice_name or self.voice_manager.get_preset("narrator")

        if voice and hasattr(voice, "name"):
            voice_name = voice.name

        output_files = []

        with tempfile.TemporaryDirectory() as temp_dir:
            section_audios = []

            for i, (title, text) in enumerate(sections):
                temp_file = Path(temp_dir) / f"section_{i:04d}.mp3"

                self.tts.synthesize(
                    text=text,
                    output_path=temp_file,
                    voice_name=voice_name,
                )

                audio = self.processor.load(temp_file)
                section_audios.append((title, audio))

            if split_chapters:
                for i, (title, audio) in enumerate(section_audios):
                    safe_title = "".join(
                        c for c in title if c.isalnum() or c in " -_"
                    ).strip()
                    chapter_path = output_path.parent / f"{output_path.stem}_{i:02d}_{safe_title}{output_path.suffix}"
                    self.processor.save(audio, chapter_path)
                    output_files.append(chapter_path)
            else:
                audios = [audio for _, audio in section_audios]
                combined = self.processor.insert_silence_between(
                    audios, section_silence_ms
                )
                self.processor.save(combined, output_path)
                output_files.append(output_path)

        return output_files

    def build_audio_track(
        self,
        script_path: str | Path,
        output_path: str | Path,
        bgm_path: str | Path | None = None,
        bgm_volume_db: float = -15.0,
    ) -> Path:
        """Build an audio track for video production.

        Args:
            script_path: Path to the dialogue/narration script.
            output_path: Path for the output audio file.
            bgm_path: Optional path to background music.
            bgm_volume_db: Volume adjustment for BGM.

        Returns:
            Path to the generated audio file.
        """
        script_path = Path(script_path)
        output_path = Path(output_path)

        script = parse_dialogue_script(script_path)
        self.voice_manager.assign_voices_for_dialogue(script.speakers)

        builder = TrackBuilder()

        with tempfile.TemporaryDirectory() as temp_dir:
            current_position = 0

            for i, line in enumerate(script.lines):
                voice_config = self.voice_manager.get_voice(line.speaker)
                temp_file = Path(temp_dir) / f"line_{i:04d}.mp3"

                self.tts.synthesize(
                    text=line.text,
                    output_path=temp_file,
                    voice_name=voice_config.name,
                    language_code=voice_config.language_code,
                    speaking_rate=voice_config.speaking_rate,
                )

                audio = self.processor.load(temp_file)
                builder.add_clip(audio, start_ms=current_position, label=line.speaker)
                current_position += len(audio) + 300

            if bgm_path:
                audio = builder.build_with_bgm(
                    bgm_path, bgm_volume_db=bgm_volume_db
                )
                self.processor.save(audio, output_path)
            else:
                builder.save(output_path)

        return output_path

    def list_voices(self, language_code: str | None = None) -> list[dict]:
        """List available TTS voices.

        Args:
            language_code: Filter by language code.

        Returns:
            List of voice information.
        """
        return self.tts.list_voices(language_code)
