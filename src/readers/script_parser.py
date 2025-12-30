"""Dialogue script parser."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DialogueLine:
    """A single line of dialogue."""

    speaker: str
    text: str
    line_number: int


@dataclass
class DialogueScript:
    """Parsed dialogue script."""

    lines: list[DialogueLine]
    speakers: set[str]

    def get_lines_by_speaker(self, speaker: str) -> list[DialogueLine]:
        """Get all lines for a specific speaker."""
        return [line for line in self.lines if line.speaker == speaker]


def parse_dialogue_script(content: str | Path) -> DialogueScript:
    """Parse a dialogue script into structured data.

    Supported formats:
    - [Speaker]: Text
    - Speaker: Text
    - 【Speaker】: Text

    Args:
        content: Script content as string or path to script file.

    Returns:
        Parsed DialogueScript object.
    """
    if isinstance(content, Path):
        content = content.read_text(encoding="utf-8")
    elif Path(content).exists():
        content = Path(content).read_text(encoding="utf-8")

    patterns = [
        r"^\[([^\]]+)\]\s*[:：]\s*(.+)$",
        r"^【([^】]+)】\s*[:：]\s*(.+)$",
        r"^([^:：\[\]【】]+)\s*[:：]\s*(.+)$",
    ]

    lines = []
    speakers = set()

    for line_number, line in enumerate(content.split("\n"), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                speaker = match.group(1).strip()
                text = match.group(2).strip()

                if speaker and text:
                    lines.append(
                        DialogueLine(speaker=speaker, text=text, line_number=line_number)
                    )
                    speakers.add(speaker)
                break

    return DialogueScript(lines=lines, speakers=speakers)


def parse_narration_script(content: str | Path) -> list[tuple[str, str]]:
    """Parse a narration script with section markers.

    Format:
    ## Section Title
    Narration text...

    Args:
        content: Script content as string or path to script file.

    Returns:
        List of (section_title, text) tuples.
    """
    if isinstance(content, Path):
        content = content.read_text(encoding="utf-8")
    elif Path(content).exists():
        content = Path(content).read_text(encoding="utf-8")

    sections = []
    current_section = "Introduction"
    current_text = []

    for line in content.split("\n"):
        line = line.strip()

        if line.startswith("##"):
            if current_text:
                sections.append((current_section, "\n".join(current_text).strip()))
                current_text = []
            current_section = line.lstrip("#").strip()
        elif line.startswith("#"):
            continue
        elif line:
            current_text.append(line)

    if current_text:
        sections.append((current_section, "\n".join(current_text).strip()))

    return sections
