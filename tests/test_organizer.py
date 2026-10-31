import os
from datetime import datetime
from pathlib import Path

import pytest
from PIL import Image

from shotsort import organizer


def make_image(path: Path, when: datetime | None = None) -> None:
    Image.new("RGB", (40, 30), (100, 120, 140)).save(path)
    if when is not None:
        ts = when.timestamp()
        os.utime(path, (ts, ts))


def test_detects_screenshots_by_name(tmp_path):
    make_image(tmp_path / "Screenshot_2026-10-01.png")
    make_image(tmp_path / "Ekran Goruntusu.png")
    make_image(tmp_path / "holiday.png")

    # OCR off so the test is about selection + naming, not recognition.
    moves = organizer.plan(tmp_path, use_ocr=False)
    sources = {Path(m.source).name for m in moves}

    assert "Screenshot_2026-10-01.png" in sources
    assert "Ekran Goruntusu.png" in sources
    assert "holiday.png" not in sources  # not a screenshot by name


def test_all_images_flag_includes_everything(tmp_path):
    make_image(tmp_path / "holiday.png")
    moves = organizer.plan(tmp_path, use_ocr=False, only_screenshots=False)
    assert len(moves) == 1


def test_date_only_name_without_ocr(tmp_path):
    make_image(tmp_path / "Screenshot_1.png", when=datetime(2026, 5, 20))
    moves = organizer.plan(tmp_path, use_ocr=False)
    assert Path(moves[0].destination).name.startswith("2026-05-20_screenshot")


def test_by_month_files_into_folders(tmp_path):
    make_image(tmp_path / "Screenshot_1.png", when=datetime(2026, 5, 20))
    moves = organizer.plan(tmp_path, use_ocr=False, by_month=True)
    assert Path(moves[0].destination).parent.name == "2026-05"


def test_apply_and_undo_round_trip(tmp_path):
    original = tmp_path / "Screenshot_1.png"
    make_image(original, when=datetime(2026, 5, 20))

    moves = organizer.plan(tmp_path, use_ocr=False)
    done = organizer.apply(moves)
    assert not original.exists()
    assert Path(done[0].destination).exists()

    organizer.undo(done)
    assert original.exists()


def test_running_twice_is_safe(tmp_path):
    make_image(tmp_path / "Screenshot_1.png", when=datetime(2026, 5, 20))
    organizer.apply(organizer.plan(tmp_path, use_ocr=False))
    # The renamed file no longer looks like a screenshot by name, so a second
    # pass finds nothing to do.
    second = organizer.plan(tmp_path, use_ocr=False)
    assert second == []


def test_name_collisions_get_distinct_targets(tmp_path):
    # Two screenshots from the same day with no text → same base name.
    make_image(tmp_path / "Screenshot_a.png", when=datetime(2026, 5, 20))
    make_image(tmp_path / "Screenshot_b.png", when=datetime(2026, 5, 20))
    moves = organizer.plan(tmp_path, use_ocr=False)
    targets = {m.destination for m in moves}
    assert len(targets) == 2  # no two files mapped to the same name


def test_missing_directory_raises(tmp_path):
    with pytest.raises(NotADirectoryError):
        organizer.plan(tmp_path / "nope")


def test_non_images_are_ignored(tmp_path):
    (tmp_path / "Screenshot_notes.txt").write_text("hi")
    assert organizer.plan(tmp_path, use_ocr=False) == []
