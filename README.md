# nt

**NOTE:** This project is created using an LLM (mostly GLM 5.3 Flash)

Make text readable in terminals: clean up curly quotes, dashes, styled
Unicode fonts, and more — without mangling the rest of your text.

## Why this exists

Text copied from chat apps, word processors, and websites is full of
typographic Unicode (“smart quotes”, em-dashes, `Ｕｎｉｃｏｄｅ`
fullwidth letters, mathematical-alphabet fonts) that renders badly or
searches badly in terminals and logs. `nt` normalizes this noise while
leaving ordinary text untouched, and offers progressively stricter
levels — down to pure-ASCII output — so the same tool works for display
cleanup, slug/filename folding, and ASCII-only pipelines.

## Installation

Requires [uv](https://docs.astral.sh/uv/):

```sh
uv tool install  git+https://github.com/cjbayliss/nt
```

Or run it ad hoc without installing:

```sh
uv run nt --help
```

## Quick start

`nt` reads from stdin by default and writes to stdout:

```console
$ echo '“Smart quotes”, em—dash, café, ⅓, ﬁ, 😀 and ＡＢＣ' | nt
"Smart quotes", em-dash, café, ⅓, ﬁ, 😀 and ABC

$ echo '“Smart quotes”, em—dash, café, ⅓, ﬁ, 😀 and ＡＢＣ' | nt -l 1
"Smart quotes", em-dash, cafe, 1/3, fi, 😀 and ABC

$ echo '“Smart quotes”, em—dash, café, ⅓, ﬁ, 😀 and ＡＢＣ' | nt -l 2 -r '?'
"Smart quotes", em-dash, cafe, 1/3, fi, ? and ABC

$ echo 'café 😀' | nt -l 2 --keep-emoji
cafe 😀
```

It also accepts files (plus `-` for stdin), processed in argument order:

```sh
nt notes.txt - < raw_input.txt > clean.txt
```

## Conversion levels

| Level | Name      | What it does                                                                                                                                                           |
| ----- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `0`   | normalize | Fixes quotes, dashes, ellipsis, styled mathematical fonts, fullwidth letters/digits, Unicode spaces and invisible characters. Accents, fractions, symbols stay.        |
| `1`   | fold      | Everything from level 0, plus: strips accents, expands ligatures (`ﬁ` → `fi`) and fractions (`⅓` → `1/3`), folds circled numerals, currency and symbols towards ASCII. |
| `2`   | strict    | Everything from level 1, then drops any remaining non-ASCII character — or replaces it with `--replace` text. Output is guaranteed pure ASCII.                         |

## CLI reference

```
nt [FILE ...] [-l {0,1,2}] [-r TEXT] [--keep-emoji] [--version]
```

| Option            | Description                                                                  | Default   |
| ----------------- | ---------------------------------------------------------------------------- | --------- |
| `FILE ...`        | Input files; `-` means stdin. Reads stdin when no files are given.           | `-`       |
| `-l`, `--level`   | Conversion level: `0`, `1`, or `2` (see table above).                        | `0`       |
| `-r`, `--replace` | Level 2 only: replacement text for non-ASCII characters with no mapping.     | drop them |
| `--keep-emoji`    | Keep emoji runs verbatim (at level 2, keeps emoji instead of dropping them). | off       |
| `--version`       | Print version and exit.                                                      | —         |

Exit codes: `0` on success, `1` if an input file cannot be read
(conversion stops at the first unreadable file; earlier files are still
written).

## Requirements

- Python ≥ 3.14
- No runtime dependencies

## Project structure

```
src/nt/
├── __main__.py    # python -m nt entry point
├── cli.py         # argument parsing, stdin/file handling, exit codes
├── conversion.py  # convert(): level pipeline, emoji-run preservation
├── tables.py      # codepoint → replacement mapping tables
├── emoji.py       # emoji codepoint ranges and run-matching regex
└── types.py       # type aliases for the mapping tables
tests/             # pytest suite (65 tests)
```

## Testing

```sh
uv run pytest
```

Type checking:

```sh
uv run mypy src tests
```
