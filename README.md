zk — ultra-minimal CLI Zettelkasten
===================================

A single-file, zero-dependency CLI to create, link, search, and traverse Markdown/text notes identified by timestamp-based IDs. Designed for speed, simplicity, and portability on Linux and Windows.

## At a glance

- Single file, zero dependencies; works on Linux and Windows.  
- Flat folder of `.md`/`.txt` files; no database or hidden state (only `.bak` on edits).  
- Timestamp IDs (`YYYY_MMDD_HHMM`) with kebab-case slugs; headers carry metadata.  
- Fast backlinks/graph via precompiled regex and in-process caching.  
- Optional Vim integration for smart link following and insertion.  
- Templates, tags, aliases, link style choice (Markdown or wiki).

## Quick start

```bash
# Install: put ./zk in your PATH and make it executable
chmod +x zk
export ZK_DIR=~/Zettel            # required
export EDITOR=vim                 # optional (defaults: vim on Linux, notepad on Windows)

zk new "First note"
zk jot "Idea: inverse outline of Chapter 2 [[2025_0910_2124]]"
zk find outline
zk link outline                   # -> [Outline](./2025_0910_2124_outline.md)
zk backlinks 2025_0910_2124
```

## Environment

- `ZK_DIR` (required) — absolute path to the notes folder.  
- `EDITOR` (optional) — editor command; defaults to vim/notepad.  
- `ZK_EXT` (optional) — `.md` (default) or `.txt`.  
- `ZK_TIMEZONE` (optional) — `UTC` (default) or `LOCAL` for ID/timestamps.  
- `ZK_TEMPLATE_DIR` (optional) — folder with `*.md` templates for `zk new -t NAME`.

## Data model

- **ID:** `YYYY_MMDD_HHMM` (UTC or local).  
- **Filename:** `ID_slug.md` (slug is kebab-case of title).  
- **Header block** (plain text, first lines):
  ```
  id: <ID>
  title: <string>
  created: <ISO8601>
  updated: <ISO8601>
  aliases: <;-separated list, optional>
  tags: <;-separated list, optional>
  ```
- **Body:** Markdown or plain text. Links: `[[ID]]` or `[[ID Title]]`.  
- **Tags/Aliases:** semicolon-separated; case-insensitive.

## Core commands

- `zk id` — print a fresh ID.  
- `zk new [TITLE…] [-t TEMPLATE] [--no-open]` — create a note, print ID, optionally open.  
- `zk jot "TEXT…"` — quick-capture a one-liner note.  
- `zk open ID|alias|slug-fragment` — fuzzy-resolve and open.  
- `zk path QUERY` — print `./ID_slug.md` (for editors/scripts).  
- `zk link [--style md|wiki] QUERY` — format `[Title](./ID_slug.md)` or `[[ID Title]]`.  
- `zk ls [--sort created|updated|title] [--rev] [--limit N] [--grep PATTERN]` — list notes.  
- `zk find QUERY` — search headers (id, title, aliases, tags).  
- `zk grep REGEX [--body]` — regex search headers; `--body` scans full text.  
- `zk tag ID "t1; t2; …"` — append tag(s).  
- `zk taglist` — list tags with counts.  
- `zk rename-tag OLD NEW` — batch-rename a tag.  
- `zk links ID` — list outgoing links.  
- `zk backlinks ID` — list notes linking to the ID.  
- `zk follow ID [N] [--open]` — follow the Nth outgoing link (optionally open).  
- `zk rename ID "New Title"` — update title, slug, and inbound links.  
- `zk alias ID "Alt Name"` — append an alias.  
- `zk audit [--orphans] [--dead] [--dups]` — detect orphans, dead links, or duplicates.  
- `zk graph --center ID [--depth N]` — ASCII graph of connections.  
- `zk doctor` — validate environment and print stats.

## Vim integration

Smart link handling without plugins:

- `gx` on `[Title](./ID_slug.md)` or `[[ID Title]]` opens in a new Vim tab; URLs/images open via `xdg-open`/`gio`.  
- `<leader>[[` inserts a Markdown link after prompting for a title/ID; Visual mode wraps selection.  
- `<leader>zl` uses `fzf` if installed for picking targets.  
- Minimal setup (`~/.vim/autoload/zklink.vim` + Markdown `ftplugin`):

```vim
let g:zk_dir = expand('~/Zettel')
let g:zk_link_style = 'md'   " or 'wiki'
```

## Templates

- Place files in `$ZK_TEMPLATE_DIR/*.md` and refer by name: `zk new -t research`.  
- Placeholders: `{ID}`, `{TITLE}`, `{CREATED}`, `{UPDATED}`.

## Examples

```bash
export ZK_DIR=~/Zettel_Jamie

# Create and tag a note
zk new "Rapid note-taking process"
zk tag 2025_1009_1952 "workflow; zettelkasten"

# Generate Markdown or wiki links
zk link rapid
zk link --style wiki rapid

# Traverse and clean-up
zk backlinks 2025_1009_1952
zk audit --dead
zk graph --center 2025_1009_1952 --depth 2

# Quick Vim flow
# - gx follows Markdown/wiki links in a new tab
# - <leader>[[ inserts a link; <leader>zl uses fzf if available
```

## Performance and behaviour

- Flat folder of `.md`/`.txt`; no DB.  
- Lazy scans plus in-process caching for directory listing and headers.  
- Backlinks/link extraction use precompiled regex fast paths.  
- All writes are atomic (temp + replace); `.bak` is created on edits/renames.  
- No hidden files beyond `.bak` backups.

## Testing

Run the smoke/perf suite:

```bash
python tests/run_tests.py
```

The tests spin up a temp repo, verify creation/open/search/links/backlinks/rename/audit/graph, and generate a 10k-note set to time `ls/find/backlinks`. Standard library only; set `ZK_DIR` via the script.
