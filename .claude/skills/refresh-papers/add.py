#!/usr/bin/env python3
# Adds papers to the running Zotero desktop app through its local connector.
import argparse, json, re, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

ZOTERO = "http://127.0.0.1:23119/connector/"
ATOM = {"a": "http://www.w3.org/2005/Atom"}
TYPES = {"proceedings-article": "conferencePaper", "book-chapter": "bookSection",
         "posted-content": "preprint", "dissertation": "thesis"}


def post(path, payload):
    req = urllib.request.Request(ZOTERO + path, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.status, res.read()


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "paper-refresh/1.0"})
    return urllib.request.urlopen(req, timeout=60).read()


def collections(root):
    targets = json.loads(post("getSelectedCollection", {})[1])["targets"]
    found, depth = {}, None
    for t in targets:
        level = t.get("level", 0)
        if depth is not None and level <= depth:
            break
        if depth is not None:
            found[t["name"].lower()] = t["id"]
        elif t["name"] == root:
            depth = level
    return found


def from_arxiv(aid):
    feed = ET.fromstring(get("https://export.arxiv.org/api/query?id_list=" + aid))
    e = feed.find("a:entry", ATOM)
    creators = []
    for a in e.findall("a:author", ATOM):
        first, _, last = a.find("a:name", ATOM).text.rpartition(" ")
        creators.append({"creatorType": "author", "firstName": first, "lastName": last})
    time.sleep(3.1)
    return {"itemType": "preprint", "title": " ".join(e.find("a:title", ATOM).text.split()),
            "abstractNote": " ".join(e.find("a:summary", ATOM).text.split()),
            "date": e.find("a:published", ATOM).text[:10], "creators": creators,
            "repository": "arXiv", "archiveID": "arXiv:" + aid, "url": "http://arxiv.org/abs/" + aid}


def from_doi(doi):
    m = json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(doi)))["message"]
    creators = [{"creatorType": "author", "firstName": a.get("given", ""), "lastName": a.get("family", a.get("name", ""))}
                for a in m.get("author", [])]
    kind = TYPES.get(m.get("type"), "journalArticle")
    venue = (m.get("container-title") or [""])[0]
    venue_field = {"conferencePaper": "proceedingsTitle", "bookSection": "bookTitle"}.get(kind, "publicationTitle")
    item = {"itemType": kind, "title": re.sub(r"<[^>]+>", "", " ".join(m["title"][0].split())),
            "date": "-".join(f"{p:02d}" for p in m["issued"]["date-parts"][0] if p), "creators": creators,
            "DOI": m["DOI"], "url": "https://doi.org/" + m["DOI"]}
    if venue and kind not in ("preprint", "thesis"):
        item[venue_field] = venue
    time.sleep(1)
    return item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="TSV: collection name, then arXiv id or DOI")
    ap.add_argument("--root", default="boardgame-research")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = [l.rstrip("\n").split("\t")[:2] for l in open(args.file) if l.strip() and not l.startswith("#")]
    known = collections(args.root)
    missing = sorted({name for name, _ in rows if name.lower() not in known})
    if missing and not args.dry_run:
        sys.exit("Create these collections under %s first: %s" % (args.root, ", ".join(missing)))

    for n, (name, key) in enumerate(rows):
        try:
            item = from_arxiv(key) if re.fullmatch(r"\d{4}\.\d{4,5}", key) else from_doi(key)
        except (urllib.error.URLError, KeyError, IndexError, AttributeError) as err:
            print(f"FAILED\t{name}\t{key}\t{err}", flush=True)
            continue
        if not args.dry_run:
            session = f"refresh-{int(time.time())}-{n}"
            post("saveItems", {"sessionID": session, "uri": item["url"], "items": [item]})
            post("updateSession", {"sessionID": session, "target": known[name.lower()], "tags": ""})
        print(f"{'dry' if args.dry_run else 'added'}\t{name}\t{item['itemType']}\t{item['date'][:4]}\t{item['title'][:90]}", flush=True)


if __name__ == "__main__":
    main()
