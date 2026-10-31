from datetime import datetime

from shotsort.naming import build_name, pick_title, slugify


def test_pick_title_prefers_the_first_real_heading():
    ocr = "12:45\n\nQuarterly Revenue Report\n\nTotal revenue grew by twelve percent across all lines"
    assert pick_title(ocr) == "Quarterly Revenue Report"


def test_pick_title_skips_clock_and_chrome():
    ocr = "9:41\n100%\n<>\nInstall Python on Windows\nDownload the installer"
    assert pick_title(ocr) == "Install Python on Windows"


def test_pick_title_empty_when_no_text():
    assert pick_title("") == ""
    assert pick_title("12:45\n100%\n:::") == ""


def test_pick_title_falls_back_to_longest_when_no_heading():
    # No single line clears the heading bar, so the longest wins.
    ocr = "abc\nde\nfg hi"
    assert pick_title(ocr) == "fg hi"


def test_slugify_handles_turkish_characters():
    assert slugify("Toplantı Notları") == "toplanti-notlari"
    assert slugify("Şirket Güncellemesi İçin") == "sirket-guncellemesi-icin"


def test_slugify_strips_punctuation_and_lowercases():
    assert slugify("Revenue: +12% (Q4)!") == "revenue-12-q4"


def test_slugify_caps_word_count():
    long = "one two three four five six seven eight nine ten"
    assert slugify(long) == "one-two-three-four-five-six-seven"


def test_slugify_caps_length():
    assert len(slugify("a" * 80)) <= 50


def test_build_name_uses_date_and_slug():
    when = datetime(2026, 10, 15, 14, 30)
    assert build_name("Quarterly Revenue Report", when, ".png") == "2026-10-15_quarterly-revenue-report.png"


def test_build_name_falls_back_without_text():
    when = datetime(2026, 10, 15)
    assert build_name("", when, ".png") == "2026-10-15_screenshot.png"
    assert build_name("", when, ".png", fallback_index=3) == "2026-10-15_screenshot-3.png"


def test_build_name_normalises_extension():
    when = datetime(2026, 1, 2)
    assert build_name("Hi there", when, "jpg").endswith(".jpg")
