"""Plan and apply the renaming and filing of screenshots."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from . import ocr
from .journal import Move
from .naming import build_name

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}

# Filenames that a screenshot tends to have, in several languages.
SCREENSHOT_HINTS = ("screenshot", "screen shot", "ekran", "captura", "capture", "snip", "bildschirm")


def looks_like_screenshot(path: Path) -> bool:
    """Heuristic: does this image look like a screenshot by its name?"""
    name = path.name.lower()
    return any(hint in name for hint in SCREENSHOT_HINTS)


def _taken_at(path: Path) -> datetime:
    """When the screenshot was taken, from the file's modification time."""
    return datetime.fromtimestamp(path.stat().st_mtime)


def _unique(destination: Path) -> Path:
    if not destination.exists():
        return destination
    stem, suffix = destination.stem, destination.suffix
    counter = 1
    while True:
        candidate = destination.with_name(f"{stem}-{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def plan(
    source: Path,
    *,
    lang: str = "eng",
    recursive: bool = False,
    by_month: bool = False,
    only_screenshots: bool = True,
    use_ocr: bool = True,
) -> list[Move]:
    """Work out the new name and location for each screenshot.

    Nothing is moved here; the result is a list of intended moves that the
    caller can preview or apply. Files already named in shotsort's own
    ``date_slug`` shape are left alone, so running twice is safe.
    """
    if not source.is_dir():
        raise NotADirectoryError(f"Not a directory: {source}")

    images = source.rglob("*") if recursive else source.iterdir()
    moves: list[Move] = []
    taken_targets: set[Path] = set()

    for index, path in enumerate(sorted(p for p in images if p.is_file())):
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        if only_screenshots and not looks_like_screenshot(path):
            continue

        when = _taken_at(path)
        text = ocr.extract_text(path, lang) if use_ocr else ""
        new_name = build_name(text, when, path.suffix, fallback_index=index)

        target_dir = source
        if by_month:
            target_dir = source / when.strftime("%Y-%m")
        destination = target_dir / new_name

        # Skip files that are already where this plan would put them.
        if destination == path:
            continue

        destination = _unique_against(destination, taken_targets)
        taken_targets.add(destination)
        moves.append(Move(str(path), str(destination)))

    return moves


def _unique_against(destination: Path, reserved: set[Path]) -> Path:
    candidate = _unique(destination)
    while candidate in reserved:
        stem, suffix = candidate.stem, candidate.suffix
        candidate = _unique(candidate.with_name(f"{stem}x{suffix}"))
    return candidate


def apply(moves: list[Move]) -> list[Move]:
    """Carry out the planned moves, creating folders as needed."""
    done: list[Move] = []
    for move in moves:
        source = Path(move.source)
        destination = Path(move.destination)
        if not source.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        final = _unique(destination)
        shutil.move(str(source), str(final))
        done.append(Move(str(source), str(final)))
    return done


def undo(moves: list[Move]) -> list[Move]:
    """Move files back to their original names and places."""
    restored: list[Move] = []
    for move in reversed(moves):
        current = Path(move.destination)
        original = Path(move.source)
        if not current.exists():
            continue
        original.parent.mkdir(parents=True, exist_ok=True)
        final = _unique(original)
        shutil.move(str(current), str(final))
        restored.append(Move(str(current), str(final)))
    return restored
