"""Document readers module."""

from .word import read_word_file
from .google_docs import read_google_doc
from .script_parser import parse_dialogue_script, parse_narration_script

__all__ = ["read_word_file", "read_google_doc", "parse_dialogue_script", "parse_narration_script"]
