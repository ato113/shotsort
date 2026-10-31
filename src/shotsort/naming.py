"""Turn the text found in a screenshot into a sensible filename.

This is the heart of shotsort and is deliberately independent of OCR: given
some text and a date, it produces a clean, safe, descriptive name. That keeps
it fast to test and easy to reason about.
"""

from __future__ import annotations

import re
from datetime import datetime

# Turkish letters mapped to ASCII, so filenames stay portable across systems.
_TURKISH = str.maketrans({
    "ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g",
    "ç": "c", "Ç": "c", "ö": "o", "Ö": "o", "ü": "u", "Ü": "u",
})

# Lines that look like clock times or dates carry no useful title.
_TIME = re.compile(r"^\s*\d{1,2}[:.]\d{2}(\s*[AaPp][Mm])?\s*$")
_DATEISH = re.compile(r"^\s*\d{1,4}[./-]\d{1,2}([./-]\d{1,4})?\s*$")

MAX_SLUG_LENGTH = 50
MAX_WORDS = 7


def _letters(text: str) -> int:
    return sum(ch.isalpha() for ch in text)


def _is_noise(line: str) -> bool:
    """A line is noise when it carries no title-worthy text."""
    stripped = line.strip()
    if len(stripped) < 3:
        return True
    if _TIME.match(stripped) or _DATEISH.match(stripped):
        return True
    # Mostly symbols or digits (menu bars, battery %, counts).
    if _letters(stripped) < 3:
        return True
    return _letters(stripped) / len(stripped) < 0.4


# A line needs this many letters to stand on its own as a title.
MIN_TITLE_LETTERS = 8


def pick_title(ocr_text: str, max_lines: int = 20) -> str:
    """Choose the most title-worthy line from OCR output.

    Screenshots put their heading near the top and OCR preserves that order, so
    the first substantial line after the UI chrome is almost always the title.
    This returns the first non-noise line with enough letters to be a real
    heading; if none qualifies, it falls back to the line with the most letters.
    """
    candidates = []
    for line in ocr_text.splitlines():
        if len(candidates) >= max_lines:
            break
        if _is_noise(line):
            continue
        candidates.append(line.strip())

    if not candidates:
        return ""
    for line in candidates:
        if _letters(line) >= MIN_TITLE_LETTERS:
            return line
    return max(candidates, key=_letters)


def slugify(text: str) -> str:
    """Make a filename-safe slug: ASCII, lowercase, dash-separated."""
    text = text.translate(_TURKISH)
    # Keep letters, digits and spaces; drop everything else.
    text = re.sub(r"[^A-Za-z0-9\s]+", " ", text)
    words = text.lower().split()
    words = words[:MAX_WORDS]
    slug = "-".join(words)
    slug = slug[:MAX_SLUG_LENGTH].rstrip("-")
    return slug


def build_name(ocr_text: str, when: datetime, extension: str, fallback_index: int = 0) -> str:
    """Build a filename from a screenshot's text and date.

    The shape is ``YYYY-MM-DD_slug.ext``. When no usable text is found it falls
    back to ``YYYY-MM-DD_screenshot[-N].ext`` so a name is always produced.
    """
    date = when.strftime("%Y-%m-%d")
    slug = slugify(pick_title(ocr_text))
    extension = extension if extension.startswith(".") else "." + extension

    if not slug:
        suffix = f"-{fallback_index}" if fallback_index else ""
        return f"{date}_screenshot{suffix}{extension}"
    return f"{date}_{slug}{extension}"
