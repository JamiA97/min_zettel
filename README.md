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
  tags: <;-separated list, optional>

- Body: Markdown or plain text. Links: `[[ID]]` or `[[ID Title]]`.
- Tags: use a header line `tags: alpha; beta; gamma` (semicolon-separated). Case-insensitive.

- Note: `aliases` and `tags` use semicolon separators (`;`) and are matched case-insensitively.

## Commands

- `zk id` — print a fresh ID.
- `zk new [TITLE…] [-t TEMPLATE] [--no-open]` — create a new note, print ID, optionally open in `$EDITOR`.
- `zk jot "TEXT…"` — quick-capture a one-liner note.
- `zk open ID|alias|slug-fragment` — fuzzy-resolve and open in `$EDITOR`.
- `zk path QUERY` — print the relative path `./ID_slug.md` for the selected note (used by editors and scripts).
- `zk link [--style md|wiki] QUERY` — print a formatted link:
  - `--style md` → `[Title](./ID_slug.md)` (default; Markdown renderer-friendly)
  - `--style wiki` → `[[ID Title]]` (legacy wiki link)
- `zk ls [--sort created|updated|title] [--rev] [--limit N] [--grep PATTERN]` — list notes.
- `zk find QUERY` — search headers (id, title, aliases, tags).
- `zk grep REGEX [--body]` — regex search; `--body` scans full text.
- `zk tag ID "t1; t2; …"` — append tag(s) to a note.
- `zk taglist` — list all tags with counts.
- `zk rename-tag OLD NEW` — batch-rename a tag across all notes.
- `zk links ID` — list outgoing links.
- `zk backlinks ID` — list notes linking to the ID.
- `zk follow ID [N] [--open]` — follow the Nth outgoing link; open with `--open`.
- `zk rename ID "New Title"` — update title, slug, and inbound links.
- `zk alias ID "Alt Name"` — append an alias to a note.
- `zk audit [--orphans] [--dead] [--dups]` — detect orphans, dead links, or duplicates.
- `zk graph --center ID [--depth N]` — ASCII graph of connections.
- `zk doctor` — validate environment and print stats.


Performance

- Flat folder of `.md`/`.txt` files; no database.
- Uses lazy scans and in-process caching for directory listing and headers.
- Fast path for backlinks and link extraction via precompiled regex.

## Vim Integration

A minimal Vim workflow is supported natively without plugins.

### Smart `gx` link following
- Inside Markdown notes, pressing `gx` on a link will:
  - Open `[Title](./ID_slug.md)` or `[[ID Title]]` in a **new Vim tab**.
  - Open `http(s)://` or image links with your system handler (`xdg-open`/`gio`).
- Implemented by a small Vim autoload script (`~/.vim/autoload/zklink.vim`) and an `ftplugin` for Markdown.

### Fast link insertion
- `<leader>[[` — prompt for a note title/ID, insert a `[Title](./ID_slug.md)` link (default Markdown style).
- `<leader>zl` — optional fzf-based picker if `fzf` is installed.
- Visual mode + `<leader>[[` — wrap selected text as link label, prompt for target.

### Configuration variables
Set these in your `.vimrc`:
```vim
let g:zk_dir = expand('~/Zettel_Jamie')
let g:zk_link_style = 'md'   " or 'wiki'



Templates

- Put files in `$ZK_TEMPLATE_DIR/*.md` and refer by name: `zk new -t research`.
- Template placeholders: `{ID}`, `{TITLE}`, `{CREATED}`, `{UPDATED}`.

Examples

```
export ZK_DIR=~/Zettel

# Quick capture
zk jot "Idea: inverse outline of Chapter 2 [[2025_0910_2124]]"
zk tag 2025_0910_2124 "structure; outline"

# New note
zk new "Greitzer parameter intuition"

# Find references
zk find greitzer
zk grep '^tags:\\s*entropy'          # header-regex; quotes needed for shell

# List all tags with counts
zk taglist
# entropy	3
# info-theory	2
# jot	1

# Traverse
zk open 2025_0910_2124
zk backlinks 2025_0910_2124
zk follow 2025_0910_2124 --open

# Refactor
zk rename 2025_0910_2124 "Compressor Surge: Greitzer Intuition"
zk rename-tag jot idea                 # batch-rename a tag (case-insensitive)
# Renamed tag 'jot' -> 'idea' in 1 notes.
zk audit --dead --orphans
zk graph --center 2025_0910_2124 --depth 2

# Health
zk doctor

## Examples

```bash
export ZK_DIR=~/Zettel_Jamie

# --- 1. Create and tag a new note ---
zk new "Rapid note-taking process"
# -> 2025_1009_1952_PN_rapid-note-taking.md

zk tag 2025_1009_1952 "workflow; zettelkasten"

# --- 2. Generate Markdown or wiki links ---
zk link rapid
# -> [Rapid Note Taking](./2025_1009_1952_PN_rapid-note-taking.md)

zk link --style wiki rapid
# -> [[2025_1009_1952 Rapid Note Taking]]

# These can be pasted directly into any note or used by Vim's link inserter (<leader>[[)

# --- 3. Follow a link in Vim ---
# Move the cursor over either:
#   [Rapid Note Taking](./2025_1009_1952_PN_rapid-note-taking.md)
#   [[2025_1009_1952 Rapid Note Taking]]
# Press `gx` → note opens in a new Vim tab.

# --- 4. Insert links quickly from Vim ---
# - Press <leader>[[   → prompts for a note title or ID and inserts a Markdown link.
# - Press <leader>zl   → (optional) fzf picker if installed.
# - In Visual mode, select text and press <leader>[[ → wraps selection as the link label.

# --- 5. Check connectivity and clean-up ---
zk backlinks 2025_1009_1952          # who links here
zk audit --dead                      # detect any broken links
zk graph --center 2025_1009_1952     # ASCII mini-graph of related notes



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
zk jot "Idea: inverse outline of Chapter 2 [[2025_0910_2124]]"
zk tag 2025_0910_2124 "structure; outline"

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
