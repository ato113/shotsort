# shotsort

*[Türkçe](README.tr.md) · English*

**Rename and organize your screenshots by what's actually in them.**

[![CI](https://github.com/ato113/shotsort/actions/workflows/ci.yml/badge.svg)](https://github.com/ato113/shotsort/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Your screenshots folder is a wall of `Screenshot_20261014_184412.png`. You can't
find anything in it, because the names say nothing. `shotsort` reads the text
inside each screenshot with OCR and renames it after what it shows.

```console
$ shotsort suggest ~/Pictures/Screenshots

3 screenshot(s) would be renamed:

  Screenshot_2026-10-01.png  ->  2026-10-01_quarterly-revenue-report.png
  Screenshot_2026-10-02.png  ->  2026-10-02_install-python-on-windows.png
  Ekran Goruntusu 3.png      ->  2026-10-03_toplanti-notlari.png

This was a preview. Run 'shotsort apply' to do it.
```

The date comes from the file; the rest comes from the heading `shotsort` read
inside the image. Suddenly the folder is searchable.

## Install

Needs [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html) for
the OCR (without it, shotsort still organizes by date — it just can't read the
text):

```bash
# Tesseract: apt install tesseract-ocr  /  brew install tesseract  /  choco install tesseract
pip install shotsort
```

Or from source:

```bash
git clone https://github.com/ato113/shotsort
cd shotsort
pip install -e .
shotsort --version
```

## Usage

```bash
shotsort suggest ~/Pictures/Screenshots      # preview the renames (nothing moves)
shotsort apply   ~/Pictures/Screenshots      # do it (asks first)
shotsort undo                                # reverse the last run
```

Useful flags:

| Flag | Meaning |
|------|---------|
| `-m`, `--by-month` | File results into `YYYY-MM/` folders |
| `-r`, `--recursive` | Include subfolders |
| `-a`, `--all-images` | Not just files that look like screenshots |
| `-l`, `--lang` | OCR languages, `+`-joined (default `tur+eng`) |
| `--no-ocr` | Date-only names, skip OCR |
| `-y`, `--yes` | Skip the confirmation on `apply` |

## How the name is chosen

1. **Date** — from the file's modification time, as `YYYY-MM-DD`.
2. **Title** — OCR returns the text top-to-bottom, so the first substantial line
   after the UI chrome (the clock, the battery, menu bars) is almost always the
   heading. shotsort filters out that noise and takes the first real line.
3. **Slug** — lowercased, Turkish characters folded to ASCII (`Toplantı` →
   `toplanti`) so the name is safe on every filesystem, trimmed to a few words.

No usable text? The file still gets a clean `YYYY-MM-DD_screenshot.png` name.

## Safe by design

- `suggest` changes nothing; you always see the plan first.
- `apply` records every move, and `undo` puts them all back.
- Running twice is safe: a file already in shotsort's `date_title` shape is left
  alone.
- Name collisions never overwrite — a second file gets `-1`, `-2`, and so on.

## Languages

OCR quality depends on the Tesseract language packs you have installed. The
default is `tur+eng`; shotsort automatically drops any language that isn't
installed so it never errors, falling back to English. Install more with your
package manager (e.g. `tesseract-ocr-tur`).

## Development

```bash
pip install -e ".[dev]"
pytest            # 23 tests
ruff check src tests
```

The naming logic is tested on its own (no OCR needed), and a separate set of
tests generates real images with text, runs them through Tesseract, and checks
the resulting names — those skip automatically when Tesseract isn't installed.

## Contributing

The interesting, OCR-free core is `naming.py` — improving how the title is
chosen is the most valuable contribution. Issues and PRs welcome.

AI-assisted contributions are fine as long as you say so in the pull request
and can explain what you're submitting.

## License

MIT — see [LICENSE](LICENSE).
