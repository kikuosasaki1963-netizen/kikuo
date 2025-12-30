"""CLI entry point for Voice Generation Agent."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .agent import VoiceAgent
from .utils.config import Config

app = typer.Typer(
    name="voice-agent",
    help="Voice Generation Agent - Generate speech from documents and scripts",
)
console = Console()


def get_agent() -> VoiceAgent:
    """Get configured VoiceAgent instance."""
    config = Config.load()
    return VoiceAgent(config)


@app.command()
def convert(
    input_path: Path = typer.Argument(..., help="Input document path (.docx, .txt, .md)"),
    output: Path = typer.Option(None, "-o", "--output", help="Output audio file path"),
    voice: Optional[str] = typer.Option(None, "--voice", help="Voice name to use"),
    lang: str = typer.Option("ja-JP", "--lang", help="Language code"),
    speed: float = typer.Option(1.0, "--speed", help="Speaking rate (0.5-2.0)"),
) -> None:
    """Convert a document to speech."""
    if output is None:
        output = input_path.with_suffix(".mp3")

    console.print(f"[blue]Converting:[/blue] {input_path}")

    agent = get_agent()
    result = agent.convert_document(
        input_path=input_path,
        output_path=output,
        voice_name=voice,
        language_code=lang,
        speaking_rate=speed,
    )

    console.print(f"[green]Saved:[/green] {result}")


@app.command()
def google_doc(
    document_id: str = typer.Argument(..., help="Google Docs document ID"),
    output: Path = typer.Option(..., "-o", "--output", help="Output audio file path"),
    voice: Optional[str] = typer.Option(None, "--voice", help="Voice name to use"),
    lang: str = typer.Option("ja-JP", "--lang", help="Language code"),
    speed: float = typer.Option(1.0, "--speed", help="Speaking rate (0.5-2.0)"),
) -> None:
    """Convert a Google Doc to speech."""
    console.print(f"[blue]Fetching Google Doc:[/blue] {document_id}")

    agent = get_agent()
    result = agent.convert_google_doc(
        document_id=document_id,
        output_path=output,
        voice_name=voice,
        language_code=lang,
        speaking_rate=speed,
    )

    console.print(f"[green]Saved:[/green] {result}")


@app.command()
def dialogue(
    script: Path = typer.Argument(..., help="Dialogue script file path"),
    output: Path = typer.Option(None, "-o", "--output", help="Output audio file path"),
    silence: int = typer.Option(500, "--silence", help="Silence between lines (ms)"),
) -> None:
    """Generate dialogue audio from a script.

    Script format:
    [Speaker A]: Hello!
    [Speaker B]: How are you?
    """
    if output is None:
        output = script.with_suffix(".mp3")

    console.print(f"[blue]Processing dialogue:[/blue] {script}")

    agent = get_agent()
    result = agent.generate_dialogue(
        script_path=script,
        output_path=output,
        silence_between_ms=silence,
    )

    console.print(f"[green]Saved:[/green] {result}")


@app.command()
def narrate(
    input_path: Path = typer.Argument(..., help="Input file path (.txt, .md)"),
    output: Path = typer.Option(None, "-o", "--output", help="Output audio file path"),
    voice: Optional[str] = typer.Option(None, "--voice", help="Voice name to use"),
    silence: int = typer.Option(1000, "--silence", help="Silence between sections (ms)"),
    split_chapters: bool = typer.Option(
        False, "--split-chapters", help="Generate separate files per section"
    ),
) -> None:
    """Generate narration audio from a text/markdown file."""
    if output is None:
        output = input_path.with_suffix(".mp3")

    console.print(f"[blue]Generating narration:[/blue] {input_path}")

    agent = get_agent()
    results = agent.generate_narration(
        input_path=input_path,
        output_path=output,
        voice_name=voice,
        section_silence_ms=silence,
        split_chapters=split_chapters,
    )

    for result in results:
        console.print(f"[green]Saved:[/green] {result}")


@app.command()
def track(
    script: Path = typer.Argument(..., help="Script file path"),
    output: Path = typer.Option(None, "-o", "--output", help="Output audio file path"),
    bgm: Optional[Path] = typer.Option(None, "--bgm", help="Background music file"),
    bgm_volume: float = typer.Option(-15.0, "--bgm-volume", help="BGM volume (dB)"),
) -> None:
    """Build an audio track for video production."""
    if output is None:
        output = script.with_suffix(".mp3")

    console.print(f"[blue]Building audio track:[/blue] {script}")

    agent = get_agent()
    result = agent.build_audio_track(
        script_path=script,
        output_path=output,
        bgm_path=bgm,
        bgm_volume_db=bgm_volume,
    )

    console.print(f"[green]Saved:[/green] {result}")


@app.command()
def voices(
    lang: Optional[str] = typer.Option(None, "--lang", help="Filter by language code"),
) -> None:
    """List available TTS voices."""
    agent = get_agent()
    voice_list = agent.list_voices(lang)

    table = Table(title="Available Voices")
    table.add_column("Name", style="cyan")
    table.add_column("Languages", style="green")
    table.add_column("Gender", style="magenta")
    table.add_column("Sample Rate", style="yellow")

    for voice in voice_list:
        table.add_row(
            voice["name"],
            ", ".join(voice["language_codes"]),
            voice["ssml_gender"],
            str(voice["natural_sample_rate_hertz"]),
        )

    console.print(table)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    console.print(f"Voice Generation Agent v{__version__}")


if __name__ == "__main__":
    app()
