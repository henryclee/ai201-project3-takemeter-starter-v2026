#!/usr/bin/env python3
"""
Collect the top ~500 posts of r/localllama into labels.csv — no key, no comments.

This is a thin driver over collect.py (collect_plan.md §4, Option A): the starter
script's transport and parsing are reused as-is — feed_url / fetch_page /
feed_entries / dedupe / add_scores / log — and this file adds only the three
things the brief needs that collect.py's defaults get wrong (plan §2):

  1. Link and image posts are KEPT as their title. collect.py discards them twice
     (SKIP_TEXTS holds "", and post_text() returns None for an empty body). Here
     only the real removal placeholders block a post, and an empty body falls back
     to the title. ~42% of r/localllama has no selftext (plan §3), so without this
     fallback 500 units is unreachable.
  2. Two length floors instead of one: 120 chars for title+selftext (collect.py's
     default), and --min-title-chars (40) for title-only units, which is also the
     threshold link_heavy() uses for surviving prose — one rule, not two. The URL
     filter runs on the text actually kept, not on a discarded body.
  3. One listing caps at ~500 items (page 6 of top/all comes back empty), so
     --limit 500 on a single window cannot yield 500. This walks several rankings
     in rank order — top/all, then top/year, top/month in reserve — deduping by
     post id as it goes, and stops the moment the target is met.

Rows are collected in rank order (row 1 is the all-time #1) but written shuffled
with a fixed seed, because rank correlates with era and topic and a best-to-worst
reading order would bias the cold labels (plan §7). The rank survives in the
sidecar. Comments are never fetched, and no author names are stored anywhere.

Nothing here guesses a label: label and note are written as empty strings, for the
labelling pass to fill in.

    .venv/bin/python collect_localllama.py --limit 500 \
        --windows top:all:5,top:year:5,top:month:3 \
        --min-title-chars 40 --min-chars 120 \
        --sleep 1.0 --shuffle --seed 42 \
        --out labels.csv --meta labels_meta.csv
"""

import argparse
import asyncio
import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import collect as c          # feed_url, fetch_page, feed_entries, link_heavy, dedupe, add_scores, log

try:
    from reddrix import Reddrix
except ImportError:         # pragma: no cover - surfaced as a message in main()
    Reddrix = None

SUB = "localllama"

# The real removal placeholders only. Note what is NOT here: "" — an empty body is
# a link/image post, which this collector keeps as its title.
REMOVED = {"[removed]", "[deleted]", "[removed by author or community]"}

# A title that is nothing but a media stub is not somewhere a claim was made.
MEDIA_PREFIXES = ("[image]", "[gif]", "[video]", "https://", "http://")

DEFAULT_WINDOWS = "top:all:5,top:year:5,top:month:3"


def parse_windows(spec):
    """`top:all:5,top:year` -> [(sort, time_range, max_pages)]; later = lower rank."""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        bits = part.split(":")
        sort = bits[0].strip()
        time_range = (bits[1].strip() or None) if len(bits) > 1 else None
        pages = int(bits[2]) if len(bits) > 2 else 5
        out.append((sort, time_range, pages))
    if not out:
        raise SystemExit("--windows listed nothing usable")
    return out


def window_label(sort, time_range):
    """`top` + `all` -> `top/all`, the string that names a ranking in the sidecar."""
    return f"{sort}/{time_range}" if time_range else sort


def unit(row, min_title_chars, min_chars):
    """The plan §5 rule: one whole post per feed entry, else the reason it dropped.

    Returns (text, None) to keep, or (None, reason) to drop. Text is verbatim —
    no truncation, no cleanup beyond what collect.feed_body() already did.
    """
    title, body = row["title"].strip(), row["body"].strip()

    if row["nsfw"]:
        return None, "nsfw"
    if body.lower() in REMOVED or title.lower() in REMOVED:
        return None, "removed"

    if body:                                    # selftext post -> the whole post
        text = f"{title}\n\n{body}" if title else body
        if text.startswith(">"):              # opens by quoting someone else
            return None, "quoted"
        if len(text) < min_chars:
            return None, "short"
    else:                                     # link/image post -> the title IS the post
        text = title
        if len(text) < min_title_chars:       # meme captions carry no label
            return None, "short-title"
        if text.lower().startswith(MEDIA_PREFIXES):
            return None, "media-title"

    # Run the URL filter on the text we actually kept: a link post's title holds
    # no URL, so it is not punished for where its body pointed.
    if ("http://" in text or "https://" in text) and c.link_heavy(text):
        return None, "link-heavy"
    return text, None


async def walk(rx, sort, time_range, pages, want, sleep_s,
               min_title_chars, min_chars, seen_ids, reasons):
    """One ranking's .rss pages, oldest-last cursor, until `want` fresh units are kept.

    Returns (kept_items, posts_seen). The id tally and drop reasons accumulate in
    the dicts handed in, so the run prints one total across all windows. `rank` is
    the position within this window's own ranking, which is what "top" means here.
    """
    label = window_label(sort, time_range)
    kept, after, seen, rank = [], None, 0, 0
    for _ in range(pages):
        url = c.feed_url(SUB, sort, time_range, after, 100)
        rows = [e for e in c.feed_entries(await c.fetch_page(rx, url, sleep_s))
                if e["kind"] == "t3"]
        if not rows:
            break                             # the ~500-item cap, or the window ran out
        for row in rows:
            seen += 1
            rank += 1
            if row["id"] in seen_ids:
                reasons["id"] = reasons.get("id", 0) + 1
                continue
            seen_ids.add(row["id"])
            text, why = unit(row, min_title_chars, min_chars)
            if text is None:
                reasons[why] = reasons.get(why, 0) + 1
                continue
            kept.append((text, {"source": f"r/{SUB}", "url": row["url"], "id": row["id"],
                               "score": None, "kind": "post", "window": label,
                               "rank": rank}))
            if len(kept) >= want:
                break
        after = rows[-1]["raw_id"]
        if len(kept) >= want:
            break
    return kept, seen


async def run(args):
    sleep_s = max(args.sleep, 0.5)
    target = args.limit + args.slack   # overshoot slightly so the
    # --scores pass's moderation drops can't land us under --limit
    seen_ids, reasons, items, total_seen = set(), {}, [], 0

    c.log(f"Starting reddrix (http_client={args.http_client}) and warming Reddit cookies...")
    async with Reddrix(http_client=args.http_client, verbose=args.verbose) as rx:
        for sort, time_range, pages in parse_windows(args.windows):
            want = target - len(items)
            if want <= 0:
                break
            kept, seen = await walk(rx, sort, time_range, pages, want, sleep_s,
                                   args.min_title_chars, args.min_chars, seen_ids, reasons)
            items += kept
            total_seen += seen
            stop = "   -> limit reached, stopping" if len(items) >= target else ""
            c.log(f"  {window_label(sort, time_range)}: {seen} posts seen | "
                 f"{len(items)} kept so far{stop}")

        if args.scores and items:
            c.log(f"  score pass over the kept {len(items)} unit(s), not all "
                 f"{total_seen} seen; also re-checks removal/stickied/NSFW the feed hides")
            items = await c.add_scores(rx, items, sleep_s)

    before = len(items)
    items = c.dedupe(items)
    c.log(f"  dropped {reasons.get('id', 0)} by id (overlap between windows) | "
          f"{before - len(items)} by identical text")
    drops = ", ".join(f"{k} {v}" for k, v in sorted(reasons.items()) if k != "id")
    if drops:
        c.log(f"  unit rule dropped: {drops}")

    if len(items) > args.limit:
        c.log(f"  trimmed {len(items) - args.limit} surplus unit(s) down to --limit "
              f"(the lowest-ranked tail of the batch)")
        items = items[:args.limit]
    if args.shuffle:
        random.Random(args.seed).shuffle(items)   # rank survives in the sidecar

    if not items:
        c.log("\nNothing collected. Loosen --min-title-chars/--min-chars, add a "
              "window, or wait 10-15 minutes if Reddit rate-limited the run.")
        sys.exit(1)

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_ALL)
        writer.writerow(["text", "label", "note"])
        for text, _meta in items:
            writer.writerow([text, "", ""])   # the labelling is yours, not the script's

    if args.meta:
        with open(args.meta, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, quoting=csv.QUOTE_ALL)
            writer.writerow(["text", "source", "url", "id", "score", "kind", "window",
                            "rank"])
            for text, meta in items:
                score = meta["score"]
                writer.writerow([text, meta["source"], meta["url"], meta["id"],
                               "" if score is None else score, meta["kind"],
                               meta["window"], meta["rank"]])

    c.log(f"\nkept {len(items)} units")
    c.log(f"Wrote {args.out} (text,label,note - label and note blank for you to "
          f"fill; the first 20 you read get note 'cold').")
    if args.meta:
        scored = sum(1 for _t, m in items if m["score"] is not None)
        tail = (f"; {scored} unit(s) scored." if args.scores
                else "; scores blank - re-run with --scores.")
        c.log(f"Wrote {args.meta} (url/id/kind/window/rank for your README{tail})")
    c.log("Commit labels.csv when it's labelled - not before.")


def main():
    parser = argparse.ArgumentParser(
        description="Collect the top posts of r/localllama into a labels.csv "
                    "skeleton (label left blank - you fill it).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--limit", type=int, default=500,
                       help="rows to write (default 500)")
    parser.add_argument("--windows", default=DEFAULT_WINDOWS,
                       metavar="sort[:time[:pages]]",
                       help=f"comma-separated rankings, in rank order "
                          f"(default {DEFAULT_WINDOWS}). One listing caps at ~500 "
                          f"items, so unioning windows is how 500 is reached")
    parser.add_argument("--min-chars", type=int, default=120,
                       help="floor for title+selftext units (collect.py's default)")
    parser.add_argument("--min-title-chars", type=int, default=40,
                       help="floor for title-only (link/image) units; also the prose "
                            "threshold link_heavy() uses")
    parser.add_argument("--slack", type=int, default=20,
                       help="collect this many extra units so that moderation drops "
                            "in the --scores pass can't leave you short of --limit")
    parser.add_argument("--scores", dest="scores", action="store_true", default=False,
                       help="open each kept post's page for its score and for the "
                            "removed/stickied/NSFW verdict the feed omits - ~1 request "
                            "per row, so ~9-13 min at --sleep 1.0")
    parser.add_argument("--no-scores", dest="scores", action="store_false",
                       help="skip the page pass; the sidecar's score column stays blank")
    parser.add_argument("--shuffle", action="store_true", default=True,
                       help="shuffle the written rows with --seed, so rank order "
                            "(and with it era and topic) doesn't bias the reading")
    parser.add_argument("--no-shuffle", dest="shuffle", action="store_false",
                       help="write in rank order instead")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="labels.csv",
                       help="text,label,note skeleton (label blank)")
    parser.add_argument("--meta", default="labels_meta.csv",
                       help="provenance sidecar for the README; '' to skip")
    parser.add_argument("--http-client", default="curl_cffi",
                       choices=["curl_cffi", "camoufox"],
                       help="how reddrix reaches Reddit; camoufox needs `reddrix "
                          "install` first")
    parser.add_argument("--verbose", action="store_true",
                       help="show reddrix's own timestamped logs (cookie renewal, retries)")
    parser.add_argument("--sleep", type=float, default=1.0,
                       help="seconds between requests, jittered upwards; keep >= 0.5")
    args = parser.parse_args()

    if Reddrix is None:
        c.log(c.MISSING_DEPS)
        sys.exit(1)
    try:
        asyncio.run(run(args))
    except RuntimeError as err:      # Reddit blocked / junk response: message, not traceback
        c.log(f"\n{err}")
        sys.exit(1)


if __name__ == "__main__":
    main()

