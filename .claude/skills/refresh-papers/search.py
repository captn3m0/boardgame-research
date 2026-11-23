#!/usr/bin/env python3
# Finds papers on arXiv and Semantic Scholar that README.md does not list yet.
import argparse, json, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).parent
ATOM = {"a": "http://www.w3.org/2005/Atom"}
LOOSE = "(abs:game OR ti:game OR abs:games)"
STRICT = '(abs:"board game" OR abs:"card game" OR abs:"board games" OR abs:"card games" OR abs:boardgame)'
S2_URL = "https://api.semanticscholar.org/graph/v1/paper/search/bulk?"
S2_FIELDS = "title,year,publicationDate,externalIds,venue"


def norm(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


def fetch(url, pause):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "paper-refresh/1.0"})
            body = urllib.request.urlopen(req, timeout=60).read()
            time.sleep(pause)
            return body
        except (urllib.error.URLError, TimeoutError):
            time.sleep(10 * (attempt + 1))
    return None


def arxiv(name, strict, limit):
    field = f'all:"{name}"' if strict else f'(ti:"{name}" OR abs:"{name}")'
    query = {"search_query": f"{field} AND {STRICT if strict else LOOSE}", "max_results": limit,
             "sortBy": "submittedDate", "sortOrder": "descending"}
    body = fetch("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(query), 3.1)
    if body is None:
        return None
    rows = []
    for e in ET.fromstring(body).findall("a:entry", ATOM):
        aid = re.sub(r"v\d+$", "", e.find("a:id", ATOM).text.split("/abs/")[-1])
        title = " ".join(e.find("a:title", ATOM).text.split())
        rows.append({"key": aid, "date": e.find("a:published", ATOM).text[:7], "title": title,
                     "url": f"https://arxiv.org/abs/{aid}", "src": "arxiv"})
    return rows


def s2(name, strict, limit, since):
    context = '("board game" | "card game" | tabletop)' if strict else "(game | games)"
    query = {"query": f'"{name}" + {context}', "fields": S2_FIELDS, "sort": "publicationDate:desc",
             "fieldsOfStudy": "Computer Science,Mathematics"}
    if since:
        query["year"] = f"{since}-"
    body = fetch(S2_URL + urllib.parse.urlencode(query), 1.5)
    if body is None:
        return None
    rows = []
    for p in (json.loads(body).get("data") or [])[:limit]:
        ids = p.get("externalIds") or {}
        aid, doi = ids.get("ArXiv"), ids.get("DOI")
        if not aid and doi and doi.lower().startswith("10.48550/arxiv."):
            aid = doi[15:]
        url = f"https://arxiv.org/abs/{aid}" if aid else f"https://doi.org/{doi}" if doi else \
            f"https://www.semanticscholar.org/paper/{p['paperId']}"
        date = (p.get("publicationDate") or str(p.get("year") or ""))[:7]
        rows.append({"key": aid or (doi or p["paperId"]).lower(), "date": date, "title": p["title"],
                     "url": url, "src": "s2"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--games", default=str(HERE / "games.txt"))
    ap.add_argument("--ignored", default=str(HERE / "ignored.txt"))
    ap.add_argument("--source", choices=["arxiv", "s2", "both"], default="both")
    ap.add_argument("--since", type=int, help="drop results published before this year")
    ap.add_argument("--only", help="comma separated game names, overrides --games")
    ap.add_argument("--limit", type=int, default=25)
    args = ap.parse_args()

    readme = pathlib.Path(args.readme).read_text()
    known = set(re.findall(r"arxiv\.org/abs/(\d{4}\.\d{4,5})", readme))
    known |= {urllib.parse.unquote(d).lower() for d in re.findall(r"doi\.org/([^)\s]+)", readme)}
    known |= {norm(t) for t in re.findall(r"^- \[(.+?)\]\(", readme, re.M)}
    ignored = pathlib.Path(args.ignored)
    if ignored.exists():
        known |= {line.split()[0] for line in ignored.read_text().splitlines() if line.strip()}

    lines = args.only.split(",") if args.only else pathlib.Path(args.games).read_text().splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        strict, name = line.startswith("~"), line.lstrip("~").strip()
        found = []
        if args.source in ("arxiv", "both"):
            found.append(arxiv(name, strict, args.limit))
        if args.source in ("s2", "both"):
            found.append(s2(name, strict, args.limit, args.since))
        print(f"## {name}" + (" (a source failed)" if None in found else ""), flush=True)
        for row in [r for rows in found if rows for r in rows]:
            if row["key"] in known or norm(row["title"]) in known:
                continue
            if args.since and row["date"] and int(row["date"][:4]) < args.since:
                continue
            known |= {row["key"], norm(row["title"])}
            print("\t".join([row["src"], row["date"], row["key"], row["title"][:110], row["url"]]), flush=True)


if __name__ == "__main__":
    sys.exit(main())
