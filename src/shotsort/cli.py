"""Command line interface for shotsort."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, journal, ocr, organizer
from .journal import Move


def _print_plan(moves: list[Move]) -> None:
    width = max((len(Path(m.source).name) for m in moves), default=0)
    for move in moves:
        src = Path(move.source).name
        dst = Path(move.destination)
        print(f"  {src:<{width}}  ->  {dst.parent.name}/{dst.name}" if dst.parent.name else f"  {src:<{width}}  ->  {dst.name}")


def cmd_suggest(args: argparse.Namespace) -> int:
    moves = organizer.plan(
        Path(args.source).expanduser(),
        lang=args.lang,
        recursive=args.recursive,
        by_month=args.by_month,
        only_screenshots=not args.all_images,
        use_ocr=not args.no_ocr,
    )
    if not moves:
        print("Nothing to rename — every screenshot is already tidy.")
        return 0

    if not ocr.available() and not args.no_ocr:
        print("Note: Tesseract isn't installed, so names are date-only. "
              "Install it for descriptive names.\n")

    print(f"{len(moves)} screenshot(s) would be renamed:\n")
    _print_plan(moves)
    print("\nThis was a preview. Run 'shotsort apply' to do it.")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    moves = organizer.plan(
        Path(args.source).expanduser(),
        lang=args.lang,
        recursive=args.recursive,
        by_month=args.by_month,
        only_screenshots=not args.all_images,
        use_ocr=not args.no_ocr,
    )
    if not moves:
        print("Nothing to rename — every screenshot is already tidy.")
        return 0

    print(f"{len(moves)} screenshot(s) to rename:\n")
    _print_plan(moves)

    if not args.yes:
        answer = input(f"\nRename {len(moves)} file(s)? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Cancelled.")
            return 0

    done = organizer.apply(moves)
    journal.record(done)
    print(f"\nRenamed {len(done)} file(s). Run 'shotsort undo' to reverse this.")
    return 0


def cmd_undo(args: argparse.Namespace) -> int:
    batch = journal.last_batch()
    if batch is None:
        print("Nothing to undo.")
        return 0
    moves = [Move(**entry) for entry in batch["moves"]]
    restored = organizer.undo(moves)
    journal.drop_last()
    print(f"Restored {len(restored)} file(s).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shotsort", description="Rename and organize screenshots by what's in them."
    )
    parser.add_argument("--version", action="version", version=f"shotsort {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("source", nargs="?", default=".", help="folder of screenshots (default: here)")
        p.add_argument("-l", "--lang", default="tur+eng", help="OCR languages, '+'-joined (default: tur+eng)")
        p.add_argument("-r", "--recursive", action="store_true", help="include subfolders")
        p.add_argument("-m", "--by-month", action="store_true", help="file into YYYY-MM folders")
        p.add_argument("-a", "--all-images", action="store_true", help="not just files that look like screenshots")
        p.add_argument("--no-ocr", action="store_true", help="date-only names, skip OCR")

    suggest = sub.add_parser("suggest", help="preview the renames")
    add_common(suggest)
    suggest.set_defaults(func=cmd_suggest)

    apply_cmd = sub.add_parser("apply", help="rename the screenshots")
    add_common(apply_cmd)
    apply_cmd.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")
    apply_cmd.set_defaults(func=cmd_apply)

    undo = sub.add_parser("undo", help="reverse the most recent run")
    undo.set_defaults(func=cmd_undo)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except NotADirectoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
