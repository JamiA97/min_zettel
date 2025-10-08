zk — ultra-minimal CLI Zettelkasten

A single-file, zero-dependency CLI to create, link, search, and traverse Markdown/text notes identified by timestamp-based IDs. Designed for speed, simplicity, and portability on Linux and Windows.

Quick start

- Put the `zk` script in your PATH and make it executable.
- Create a notes folder and point `ZK_DIR` to it.
- Optionally set `EDITOR` (defaults: vim on Linux, notepad on Windows).

Environment

- `ZK_DIR` (required) — absolute path to the notes folder.
- `EDITOR` (optional) — editor command. Defaults to vim (Linux) or notepad (Windows).
- `ZK_EXT` (optional) — `.md` (default) or `.txt`.
- `ZK_TIMEZONE` (optional) — `UTC` (default) or `LOCAL` for ID generation and timestamps.
- `ZK_TEMPLATE_DIR` (optional) — folder with `*.md` templates enabling `zk new -t NAME`.

Data model

- ID: `YYYY_MMDD_HHMM` (UTC or local).
- Filename: `ID_slug.md` (slug is kebab-case of title).
- Header block (first lines, plain text):
  id: <ID>
  title: <string>
  created: <ISO8601>
  updated: <ISO8601>
  aliases: <;-separated list, optional>

- Body: Markdown or plain text. Links: `[[ID]]` or `[[ID Title]]`. Tags as `#tag`.

Commands

- `zk id` — print a fresh ID.
- `zk new [TITLE…] [-t TEMPLATE] [--no-open]` — create a new note, print ID, optionally open in `$EDITOR` (default: open).
- `zk jot "TEXT…"` — create a one-liner note with a `## Jot` section prefilled; prints ID.
- `zk open ID|alias|slug-fragment` — fuzzy-resolve (prefers exact ID, then exact alias, then unique slug/filename substring) and open.
- `zk ls [--sort created|updated|title] [--rev] [--limit N] [--grep PATTERN]` — list notes with columns: ID, title, updated.
- `zk find QUERY` — case-insensitive search over header (id, title, aliases, timestamps).
- `zk grep REGEX [--body]` — regex search; header-only by default; `--body` scans full text.
- `zk links ID` — print outgoing link IDs from the note.
- `zk backlinks ID` — print notes that link to the ID (scans for `[[ID]]` or `[[ID Title]]`).
- `zk follow ID [N] [--open]` — print the Nth outgoing link’s ID (default 1); with `--open`, open it.
- `zk rename ID "New Title"` — update title, filename slug, and update inbound links of the form `[[ID Old Title]]` to `[[ID New Title]]` (plain `[[ID]]` unchanged). Atomic writes with `.bak`.
- `zk alias ID "Alt Name"` — append alias to header (de-duplicated).
- `zk audit [--orphans] [--dead] [--dups]` — report orphans (no in/out links), dead links, and duplicate titles/aliases. With no flags, runs all.
- `zk graph --center ID [--depth N]` — ASCII adjacency; depth-limited BFS from center.
- `zk doctor` — validate environment, print counts, test write permissions.

Performance

- Flat folder of `.md`/`.txt` files; no database.
- Uses lazy scans and in-process caching for directory listing and headers.
- Fast path for backlinks and link extraction via precompiled regex.

Templates

- Put files in `$ZK_TEMPLATE_DIR/*.md` and refer by name: `zk new -t research`.
- Template placeholders: `{ID}`, `{TITLE}`, `{CREATED}`, `{UPDATED}`.

Examples

```
export ZK_DIR=~/Zettel

# Quick capture
zk jot "Idea: inverse outline of Chapter 2 [[2025_0910_2124]] #structure"

# New note
zk new "Greitzer parameter intuition"

# Find references
zk find greitzer

# Traverse
zk open 2025_0910_2124
zk backlinks 2025_0910_2124
zk follow 2025_0910_2124 --open

# Refactor
zk rename 2025_0910_2124 "Compressor Surge: Greitzer Intuition"
zk audit --dead --orphans
zk graph --center 2025_0910_2124 --depth 2

# Health
zk doctor
```

Testing

- Run `python tests/run_tests.py` to execute a smoke/perf suite that:
  - Creates a temp repo with sample notes.
  - Verifies new, open-resolve, find, grep, links, backlinks, rename (with link updates), audit, and graph.
  - Generates 10k stub notes and measures timings for ls/find/backlinks.
- The tests use only the Python standard library and run on Linux/Windows. Set `ZK_DIR` via the script.

Notes

- All writes are atomic (temp file + replace). `.bak` files are created on edits/renames.
- Backlinks use ID scanning for speed (alias-only links are not considered backlinks).
- No hidden files are written except `.bak` backups on edits.

Example:
export ZK_DIR=~/Zettel
:
# Quick capture
zk jot "Idea: inverse outline of Chapter 2 [[2025_0910_2124]] #structure"

# New note
zk new "Greitzer parameter intuition"

# Insert link with completion (shell completion later; initially: print candidates)
zk find greitzer        # shows IDs; copy/paste ID into [[ID]]

# Traverse
zk open 2025_0910_2124  # open by ID
zk backlinks 2025_0910_2124
zk follow 2025_0910_2124 --open

# Refactor
zk rename 2025_0910_2124 "Compressor Surge: Greitzer Intuition"
zk audit --dead --orphans
zk graph --center 2025_0910_2124 --depth 2


