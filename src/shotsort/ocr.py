"""Optional OCR via Tesseract.

OCR is isolated here so the rest of shotsort works — and tests run — whether or
not Tesseract is installed. When it's missing, screenshots are still organized
by date; they just don't get descriptive names.
"""

from __future__ import annotations

import functools
from pathlib import Path


@functools.lru_cache(maxsize=1)
def available() -> bool:
    """Return True when both pytesseract and the tesseract binary are usable."""
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401

        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


@functools.lru_cache(maxsize=1)
def languages() -> tuple[str, ...]:
    """Tesseract language codes installed on this machine."""
    if not available():
        return ()
    try:
        import pytesseract

        return tuple(pytesseract.get_languages(config=""))
    except Exception:
        return ()


def best_lang(preferred: str) -> str:
    """Pick the preferred languages that are actually installed, else English.

    ``preferred`` is a '+'-joined list such as "tur+eng"; codes that aren't
    installed are dropped so Tesseract doesn't error.
    """
    installed = set(languages())
    wanted = [code for code in preferred.split("+") if code in installed]
    if wanted:
        return "+".join(wanted)
    return "eng" if "eng" in installed else (next(iter(installed), "eng"))


def extract_text(path: Path, lang: str = "eng") -> str:
    """Run OCR on an image, returning the recognised text (empty on failure)."""
    if not available():
        return ""
    try:
        import pytesseract
        from PIL import Image

        with Image.open(path) as image:
            return pytesseract.image_to_string(image, lang=best_lang(lang))
    except Exception:
        return ""
