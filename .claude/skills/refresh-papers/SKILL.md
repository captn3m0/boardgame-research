---
name: refresh-papers
description: Find new board game research on arXiv and Semantic Scholar that this list does not have yet, add the accepted papers to Zotero and regenerate README.md. Use when asked to refresh, update or look for new papers for the boardgame-research list.
---

# Refresh the paper list

Zotero is the source of truth. `boardgame-research.rdf` is a Zotero RDF export of
collection `8S9AI4TI` (one sub-collection per game) and `make` turns it into `README.md`.
Never hand-edit `README.md`.

## 1. Search

```bash
uv run --no-project python .claude/skills/refresh-papers/search.py --since 2021 > "$TMPDIR/candidates.tsv"
```

- Queries both the arXiv API and the Semantic Scholar bulk search for every name in `games.txt`.
- Prints `source, date, id, title, url` under a `## Game` heading, and skips anything already
  in `README.md` (by arXiv id, DOI or title) or in `ignored.txt`.
- A full run takes about 15 minutes because of rate limits (3s per arXiv call). Run it in the
  background, or in slices with `--only "Catan,Hanabi"`. Use `--source arxiv` or `--source s2`
  to query one side. `(a source failed)` on a heading means rerun that game.
- For a routine refresh set `--since` to the year of the last refresh commit.

Before searching, check whether new mainstream games are missing from `games.txt`
(BoardGameGeek top 100 and hotness, Spiel des Jahres winners and nominees of the last five
years). Prefix a name with `~` when it is a common word.

## 2. Triage

In scope: playing, solving, learning, complexity or design analysis of a specific modern,
mainstream board or card game, and benchmarks built on one.

Out of scope: chess, go, poker and abstract or purely theoretical games; papers that only
mention a game in passing or use it as one of many benchmarks; education, language-learning,
marketing and health studies; name collisions.

Semantic Scholar returns a lot of out-of-scope material, arXiv much less. Read the abstract
when the title is not enough. Ask the user about the doubtful ones, grouped by game, instead
of guessing.

Append every rejected id (first column is the id, the rest is a free-text note) to
`ignored.txt` so it is not proposed again.

## 3. Add to Zotero

Write the accepted papers to a TSV, one per line: collection name, tab, arXiv id or DOI.

```bash
uv run --no-project python .claude/skills/refresh-papers/add.py --dry-run "$TMPDIR/accepted.tsv"
uv run --no-project python .claude/skills/refresh-papers/add.py "$TMPDIR/accepted.tsv"
```

- `add.py` talks to the Zotero desktop app on `127.0.0.1:23119`, so Zotero must be running
  and the command must run outside the sandbox. It never touches `zotero.sqlite`.
- Metadata comes from the arXiv API (saved as `preprint`) or Crossref (type from the DOI).
  Papers with neither an arXiv id nor a Crossref DOI have to be added by hand.
- Collection names must match a sub-collection of `boardgame-research`. The connector
  cannot create collections: the script stops and lists the missing ones, ask the user to
  create them in Zotero and run it again.
- It is not idempotent. Never rerun a file that already went through, split it instead.

## 4. Regenerate

Ask the user to export the `boardgame-research` collection from Zotero (right click, Export
Collection, format Zotero RDF, no files or notes) over `boardgame-research.rdf`, then:

```bash
make
```

`make` needs `xsltproc` and `doctoc`. Check `git diff README.md` shows only the additions,
and leave committing to the user.
