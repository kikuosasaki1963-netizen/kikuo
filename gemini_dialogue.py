#!/usr/bin/env python3
"""Gemini TTS dialogue generator - Simple script for converting scripts to natural speech."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.tts.gemini_tts import GeminiTTS


def parse_dialogue(content: str) -> list[dict]:
    """Parse dialogue script into segments."""
    segments = []

    # Support multiple formats: [話者1]:, Speaker 1:, 話者1:
    patterns = [
        r'\[(話者\d+|[^\]]+)\]:\s*(.+)',  # [話者1]: or [Name]:
        r'(Speaker\s*\d+):\s*(.+)',        # Speaker 1:
        r'(話者\d+):\s*(.+)',              # 話者1:
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content):
            speaker = match.group(1).strip()
            text = match.group(2).strip()
            if text:
                segments.append({"speaker": speaker, "text": text})

    return segments


def main():
    if len(sys.argv) < 2:
        print("使用方法: python gemini_dialogue.py <スクリプト.txt> [出力.mp3]")
        print("")
        print("スクリプト形式:")
        print("  [話者1]: セリフ")
        print("  [話者2]: セリフ")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"ファイルが見つかりません: {input_file}")
        sys.exit(1)

    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_suffix(".mp3")

    # Load and parse script
    content = input_file.read_text(encoding="utf-8")
    segments = parse_dialogue(content)

    if not segments:
        print("対話セグメントが見つかりませんでした。")
        print("形式: [話者1]: セリフ")
        sys.exit(1)

    print(f"セグメント数: {len(segments)}")

    # Identify speakers
    speakers = list(set(seg["speaker"] for seg in segments))
    print(f"話者: {', '.join(speakers)}")

    # Default voice assignments (alternating female/male)
    female_voices = ["Aoede", "Kore", "Leda", "Zephyr"]
    male_voices = ["Charon", "Puck", "Orus", "Fenrir"]

    speaker_voices = {}
    speaker_styles = {}

    for i, speaker in enumerate(sorted(speakers)):
        if i % 2 == 0:
            speaker_voices[speaker] = female_voices[i // 2 % len(female_voices)]
            speaker_styles[speaker] = "as an expressive young woman speaking Japanese"
        else:
            speaker_voices[speaker] = male_voices[i // 2 % len(male_voices)]
            speaker_styles[speaker] = "as a calm knowledgeable expert speaking Japanese"

    print("\n音声割り当て:")
    for speaker, voice in speaker_voices.items():
        print(f"  {speaker}: {voice}")

    # Generate audio
    print(f"\n音声生成中...")
    tts = GeminiTTS()
    result = tts.synthesize_dialogue(
        segments=segments,
        output_path=output_file,
        speaker_voices=speaker_voices,
        speaker_styles=speaker_styles,
    )

    print(f"\n完了: {result}")


if __name__ == "__main__":
    main()
