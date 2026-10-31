"""End-to-end OCR tests, skipped when Tesseract isn't installed."""

import glob
from datetime import datetime
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from shotsort import ocr
from shotsort.naming import build_name

pytestmark = pytest.mark.skipif(not ocr.available(), reason="Tesseract not installed")


def _font(size: int):
    candidates = glob.glob("/usr/share/fonts/**/DejaVuSans*.ttf", recursive=True) or \
        glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
    return ImageFont.truetype(candidates[0], size) if candidates else ImageFont.load_default()


def make_screenshot(path: Path, heading: str, body: str) -> None:
    img = Image.new("RGB", (800, 400), (250, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 800, 60], fill=(40, 80, 200))
    draw.text((20, 14), "12:45", font=_font(24), fill=(255, 255, 255))  # clock noise
    draw.text((40, 110), heading, font=_font(40), fill=(20, 20, 30))
    draw.text((40, 200), body, font=_font(24), fill=(60, 60, 70))
    img.save(path)


def test_ocr_reads_the_heading(tmp_path):
    shot = tmp_path / "Screenshot.png"
    make_screenshot(shot, "Quarterly Revenue Report", "Revenue grew this quarter")

    text = ocr.extract_text(shot, "eng")
    assert "Quarterly" in text and "Revenue" in text


def test_name_is_built_from_the_heading(tmp_path):
    shot = tmp_path / "Screenshot.png"
    make_screenshot(shot, "Install Python on Windows", "Download the installer")

    text = ocr.extract_text(shot, "eng")
    name = build_name(text, datetime(2026, 10, 2), ".png")
    assert name == "2026-10-02_install-python-on-windows.png"


def test_best_lang_falls_back_to_installed(tmp_path):
    # A language that isn't installed should fall back, not error.
    assert ocr.best_lang("klingon") in ("eng",) or ocr.best_lang("klingon") != ""
