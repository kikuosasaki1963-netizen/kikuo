"""Google Docs reader."""
from __future__ import annotations

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from ..utils.config import Config


def get_credentials(config: Config) -> Credentials:
    """Get Google API credentials from config."""
    if not config.validate_google_docs():
        raise ValueError(
            "Google Docs API credentials not configured. "
            "Please set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REFRESH_TOKEN."
        )

    return Credentials(
        token=None,
        refresh_token=config.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.google_client_id,
        client_secret=config.google_client_secret,
    )


def extract_text_from_document(document: dict) -> str:
    """Extract text content from a Google Docs document structure."""
    content = document.get("body", {}).get("content", [])
    text_parts = []

    for element in content:
        if "paragraph" in element:
            para_text = extract_text_from_paragraph(element["paragraph"])
            if para_text:
                text_parts.append(para_text)
        elif "table" in element:
            table_text = extract_text_from_table(element["table"])
            if table_text:
                text_parts.append(table_text)

    return "\n".join(text_parts)


def extract_text_from_paragraph(paragraph: dict) -> str:
    """Extract text from a paragraph element."""
    elements = paragraph.get("elements", [])
    text_parts = []

    for element in elements:
        if "textRun" in element:
            content = element["textRun"].get("content", "")
            text_parts.append(content)

    return "".join(text_parts).strip()


def extract_text_from_table(table: dict) -> str:
    """Extract text from a table element."""
    rows = table.get("tableRows", [])
    row_texts = []

    for row in rows:
        cells = row.get("tableCells", [])
        cell_texts = []

        for cell in cells:
            cell_content = cell.get("content", [])
            cell_text_parts = []

            for element in cell_content:
                if "paragraph" in element:
                    text = extract_text_from_paragraph(element["paragraph"])
                    if text:
                        cell_text_parts.append(text)

            cell_texts.append(" ".join(cell_text_parts))

        row_texts.append("\t".join(cell_texts))

    return "\n".join(row_texts)


def read_google_doc(document_id: str, config: Config | None = None) -> str:
    """Read text content from a Google Docs document.

    Args:
        document_id: The Google Docs document ID (from URL).
        config: Configuration object. If None, loads from environment.

    Returns:
        Extracted text content with title.

    Raises:
        ValueError: If credentials are not configured.
    """
    if config is None:
        config = Config.load()

    credentials = get_credentials(config)
    service = build("docs", "v1", credentials=credentials)

    document = service.documents().get(documentId=document_id).execute()

    title = document.get("title", "Untitled")
    text = extract_text_from_document(document)

    return f"Title: {title}\n\n{text}"
