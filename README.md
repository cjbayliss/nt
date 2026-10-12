# nt

**NOTE:** This project is created using an LLM (mostly GLM 5.3 Flash)

`nt` converts Unicode text so it reads well in a terminal: curly quotes, en/em
dashes, ellipses, styled "fake font" letters (𝐛𝐨𝐥𝐝, 𝔤𝔬𝔱𝔥𝔦𝔠, ＡＢＣ), ligatures,
accents, arrows, box-drawing lines, and more are mapped to clean ASCII
equivalents — while everything else is left untouched.


## Installation

Requires [uv](https://docs.astral.sh/uv/):

```sh
uv tool install git+https://github.com/cjbayliss/nt
```

Or run it ad hoc without installing:

```sh
uv run nt --help
```

## Requirements

- Python **3.15+**
- No runtime dependencies

## Usage

Read from stdin, write to stdout:

```sh
$ echo '“Hello” — café… 𝐛𝐨𝐥𝐝 ＡＢＣ 🙂' | nt
"Hello" - café... bold ABC 🙂
```

Convert one or more files:

```sh
nt notes.txt chapter.md
cat paste.txt | nt
```

Conversion happens at one of three levels, selected with `-l`/`--level`:

```sh
# Level 0 (default) — normalize: fix quotes, dashes, ellipsis,
# styled fonts, fullwidth letters; keep everything else as-is.
$ echo 'café — “x”… ﬁn' | nt
café - "x"... fin

# Level 1 — fold: additionally strip accents and fold ligatures,
# fractions, numerals, symbols, box-drawing lines, and shapes towards ASCII.
$ echo 'café — “x”… ﬁn' | nt -l 1
cafe - "x"... fin

# Level 2 — strict: output is pure ASCII; anything unmapped is dropped.
$ echo 'café — “x”… 🙂' | nt -l 2
cafe - "x"... 
```

At level 2, replace unmapped characters instead of dropping them:

```sh
$ echo 'café 🙂' | nt -l 2 -r '?'
cafe ?
```

Keep emoji runs verbatim (emoji are never rewritten; at level 2 they are kept
instead of dropped):

```sh
$ echo 'café 🙂' | nt -l 2 --keep-emoji
cafe 🙂
```

All options:

```text
-h, --help            show help and exit
-l, --level {0,1,2}   conversion level (default: 0)
-r, --replace TEXT    level 2 only: replacement for unmapped non-ASCII
                      characters (default: drop them)
--keep-emoji          keep emoji runs verbatim
--version             show version and exit
```

Exit status is `0` on success and `1` if an input file cannot be read.


## Development

Run the test suite (unit tests plus Hypothesis property-based tests; coverage
is enforced at ≥ 99%):

```sh
uv run pytest -q
```

Lint, format check, and type check:

```sh
uv run ruff check
uv run mypy --strict
uv format --preview-features format-command
```
