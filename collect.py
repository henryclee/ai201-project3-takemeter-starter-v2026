#!/usr/bin/env python3
"""
Collect Reddit posts into a labels.csv skeleton — no app, no key, no .env.

Reddit closed unauthenticated .json access in 2026, and app approval is now slow
enough to stall an evening of work. So this script goes through the doors Reddit
still leaves open: the **Atom feeds** — every listing has a .rss twin, same sort,
same time window, full post bodies — and the **HTML pages**, which carry the one
thing feeds never did: scores, moderation verdicts, and comment structure.
reddrix (https://github.com/Coding-Doctor-Omar/reddrix) handles the transport:
it imitates a browser's TLS handshake (curl_cffi), warms Reddit's own session
cookies, and renews them with backoff when Reddit pushes back. There is nothing
to register and nothing to keep secret.

    python -m pip install -r requirements-collect.txt   # once, into your .venv

    python collect.py --sub running --sort top --time year --limit 250
    python collect.py --sub running --mode both --limit 150
    python collect.py --sub running --limit 80 --shuffle --seed 7
    python collect.py --sub running --no-scores --limit 250   # feed only, fastest
    python collect.py --from-file feed1.xml feed2.xml          # saved-page fallback

What the two sources are each good at: the feed returns 100 posts a page with
their full text and paginates cleanly (after=t3_...); the page HTML returns only
a handful of posts but knows their score and whether a moderator removed them.
Joining the two on the post id is what gets you 250 posts, with provenance, in a
couple of minutes of patient requests. --no-scores skips the second half.

What it keeps:    whole posts, verbatim — text lands in the CSV exactly as
                  Reddit serves it, the way labels_template.csv asks ("keep the
                  whole post, don't trim it to fit"). Units are dropped WHOLE,
                  never cut: picture/link posts (no prose to classify), units
                  under 120 chars, removed/deleted, mostly links, openers that
                  quote someone else, or duplicates. No length ceiling by
                  default; --max-chars exists if you want one.
Heads-up:        bart-large-mnli reads only the first ~1024 tokens (~700
                  words), so a 5,000-char essay is judged on its opening. Keep
                  such posts if you like — just say so in your README.
What it never does: fill in a label, trim a post, or hammer Reddit — one
                  request at a time, paused and jittered, with reddrix renewing
                  cookies and retrying the rest.

Where the posts came from — say so in your README: the public subreddit(s) you
passed to --sub, the --sort and --time window, the date you ran it, and that the
posts came off public feeds and pages via the reddrix scraper rather than Reddit's
API. Public subreddits only, text only, and a nudge to keep the pace slow.

Blocked anyway? --from-file parses saved feeds (.rss/.xml — open the feed URL in
any browser and save it) and old listing .json dumps. Otherwise the honest
fallback is copying ~200 posts by hand: an evening's work, and the labelling was
always the graded part.
"""


import argparse
import asyncio
import csv
import json
import random
import re
import sys
import urllib.parse
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

try:                      # the scraping extras are optional: --from-file works without them
    from reddrix import Reddrix
    from reddrix.exceptions import FatalAntiBotBlockError
except ImportError:       # pragma: no cover - the friendly error is raised where it matters
    Reddrix = None

    class FatalAntiBotBlockError(Exception):
        """Stand-in so this module still imports when reddrix isn't installed."""

MISSING_DEPS = (
    "Scraping needs the collector extras, which aren't installed yet:\n"
    "    python -m pip install -r requirements-collect.txt\n"
    "  (or skip fetching altogether: python collect.py --from-file feed.xml)"
)

BASE = "https://www.reddit.com"

# Reddit's own removal placeholders, plus the empty string.
SKIP_TEXTS = {
    "",
    "[removed]",
    "[deleted]",
    "[removed by author or community]",
}


def log(msg):
    print(msg, file=sys.stderr)


def link_heavy(text):
    """True when, stripped of URLs, too little actual prose is left."""
    stripped = re.sub(r"https?://\S+", "", text).strip()
    return len(stripped) < 40


def acceptable(text, min_chars, max_chars):
    """One-author, self-contained, label-carrying unit of prose — or reject it."""
    text = text.strip()
    if text.lower() in SKIP_TEXTS:
        return False
    if text.startswith(">"):          # opens by quoting someone else
        return False
    if len(text) < min_chars:
        return False
    if max_chars and len(text) > max_chars:   # 0 = no ceiling: whole post stays whole
        return False
    if link_heavy(text):
        return False
    return True


def post_text(title, body):
    """Title + body for a text post, or None when there is no prose to classify.

    A photo/video/link post's body is empty - the picture may be lovely, but
    bart-large-mnli reads text, and a human can't gold-label a JPEG's feelings.
    Title-only "posts" are rejected too: a 40-word title rarely carries the
    signal the task is about, and one rule for both paths beats two.
    """
    body = (body or "").strip()
    title = (title or "").strip()
    if not body:
        return None
    return f"{title}\n\n{body}" if title else body


def feed_url(sub, sort, time_range, after, limit):
    """The .rss twin of a listing: same sort, same window, up to 100 posts a page."""
    params = {"limit": min(limit, 100)}
    if sort == "top" and time_range:
        params["t"] = time_range
    if after:
        params["after"] = after
    return f"{BASE}/r/{sub}/{sort}/.rss?{urllib.parse.urlencode(params)}"


# ------------------------------------------------------------------ HTML signals
# Reddit's page markup puts the useful facts in attributes: score, moderation
# verdict, whether a comment is a reply. Only the attributes are read, so a
# markup tweak costs us a filter, not the run.

class PostCard(HTMLParser):
    """<shreddit-post>: the score, flags and ids the Atom feed leaves out."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards, self.cur = [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "shreddit-post":
            self.cur = {
                "id": (a.get("id") or "").replace("t3_", ""),
                "permalink": a.get("permalink") or "",
                "title": a.get("post-title") or "",
                "score": int(a.get("score") or 0),
                "num_comments": int(a.get("comment-count") or 0),
                "created": a.get("created-timestamp") or "",
                "removed": bool(a.get("moderation-verdict")),
                "stickied": False,
                "nsfw": False,
            }
        elif self.cur is not None:
            # Reddit ships the stickied/NSFW icon on every post and hides the ones
            # that don't apply ("class=\"hidden stickied-status\""), so merely being
            # present is not the signal - being present and unhidden is. Read it the
            # other way and the whole subreddit comes back as stickied.
            classes = (a.get("class") or "").split()
            if "hidden" in classes or "hidden" in a:
                return
            label = (a.get("aria-label") or "").lower()
            if "stickied post" in label or "stickied-status" in classes:
                self.cur["stickied"] = True
            if "nsfw" in label or "not safe for work" in label:
                self.cur["nsfw"] = True

    def handle_endtag(self, tag):
        if tag == "shreddit-post" and self.cur is not None:
            self.cards.append(self.cur)
            self.cur = None


class CommentCard(HTMLParser):
    """<shreddit-comment>, nesting and all - a stack keeps parents and replies.

    Reddit marks replies with parentid=t1_... and top-level comments with the post
    itself (parentid=t3_...), which is a far surer read of "top level" than the
    depth attribute, whose numbering has been known to shift between pages.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.cards = [], []

    def handle_starttag(self, tag, attrs):
        if tag != "shreddit-comment":
            return
        a = dict(attrs)
        self.stack.append({
            "id": (a.get("thingid") or a.get("id") or "").replace("t1_", ""),
            "score": int(a.get("score") or 0),
            "author": a.get("author") or "",
            "url": BASE + (a.get("permalink") or ""),
            "depth": a.get("depth") or "",
            "top": (a.get("parentid") or "").startswith("t3_"),
        })

    def handle_endtag(self, tag):
        if tag == "shreddit-comment" and self.stack:
            self.cards.append(self.stack.pop())


def parse_cards(page):
    parser = PostCard()
    parser.feed(page or "")
    parser.close()
    return parser.cards


def parse_comments(page):
    parser = CommentCard()
    parser.feed(page or "")
    parser.close()
    cards = parser.cards
    if cards and not any(c["top"] for c in cards):
        # No parentid to lean on (older markup): shallowest depth = top level.
        depths = [int(c["depth"]) for c in cards if str(c["depth"]).isdigit()]
        if depths:
            shallowest = str(min(depths))
            for c in cards:
                c["top"] = c["depth"] == shallowest
    return cards


# ------------------------------------------------------------------ feed signals

def _field(block, tag):
    match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", block, re.S)
    return match.group(1).strip() if match else ""


def feed_body(fragment):
    """An Atom <content type="html"> is escaped twice; undo both, keep paragraphs."""
    text = unescape(unescape(fragment or ""))
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</p>", "\n\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s*submitted by\s*/u/\S+\s*", " ", text)   # feed's own footer
    text = re.sub(r"\[link\]|\[comments\]", " ", text)
    return re.sub(r"[ \t]+", " ", text).strip()


def feed_entries(xml):
    """Every <entry> in an Atom feed, posts (t3) and comments (t1) alike."""
    out = []
    for block in re.findall(r"<entry>(.*?)</entry>", xml or "", re.S):
        raw_id = _field(block, "id")
        kind, _, short_id = raw_id.rpartition("_")
        title = _field(block, "title")
        out.append({
            "raw_id": raw_id,                       # t3_1qo0vmv / t1_o219uy0
            "kind": kind or "?",
            "id": short_id,
            "title": unescape(title),
            "body": feed_body(_field(block, "content")),
            "author": _field(block, "name").lstrip("/") or "unknown",
            "created": _field(block, "updated"),
            "url": (re.search(r'<link[^>]*href="([^"]+)"', block) or [None, ""])[1],
            "nsfw": title.strip().lower().startswith("[nsfw]"),
        })
    return out


async def fetch_page(rx, url, sleep_s):
    """GET url through reddrix as text — an Atom feed, or a page of HTML.

    reddrix owns the hard parts: a curl_cffi session holding Reddit's own cookies,
    retries with backoff, cookie renewal when they go stale. It does NOT pace plain
    get() calls, so the politeness stays ours — one request at a time, jittered.
    """
    await asyncio.sleep(random.uniform(sleep_s, sleep_s * 1.5))
    try:
        page = await rx.get(url, expected_data_type="HTML/XML")
    except FatalAntiBotBlockError as err:
        raise RuntimeError(
            f"Reddit blocked us at: {url}\n"
            "reddrix already retried and renewed its cookies, so this is a rate limit\n"
            "on this IP rather than a bug. Fixes, cheapest first:\n"
            "  1. wait 10-15 minutes and re-run the same command;\n"
            "  2. raise --sleep (e.g. 2.0), lower --limit, or split the run across a\n"
            "     couple of sittings — nothing is lost, the CSV is written at the end;\n"
            "  3. try --http-client camoufox: a stealth browser gets through where a\n"
            "     plain TLS client doesn't (run `reddrix install` once, first);\n"
            "  4. or save a feed your browser CAN load — open the .rss version of this\n"
            "     listing, save the file, and re-run with --from-file feed.xml;\n"
            "  5. or collect by hand into labels.csv — the labelling is the graded part."
        ) from err
    except Exception as err:            # network oddities reddrix surfaces raw
        raise RuntimeError(f"Couldn't fetch {url}: {err}") from err
    if not page:
        return ""                     # some quiet 403s arrive empty: treat as no more data
    return page if isinstance(page, str) else str(page)


async def collect_posts(rx, sub, sort, time_range, limit, sleep_s, min_chars, max_chars,
                        want_scores=True):
    """Walk the .rss listing — 100 posts a page — and keep the labelable prose."""
    kept, after, pages = [], None, 0
    seen = no_text = blocked = quality = 0
    while len(kept) < limit:
        url = feed_url(sub, sort, time_range, after, 100)
        log(f"  fetching {url}")
        rows = [e for e in feed_entries(await fetch_page(rx, url, sleep_s)) if e["kind"] == "t3"]
        if not rows:
            break
        pages += 1
        for row in rows:
            seen += 1
            if row["nsfw"] or row["body"].strip().lower() in SKIP_TEXTS:
                blocked += 1
                continue
            text = post_text(row["title"], row["body"])
            if text is None:
                no_text += 1                # picture/link/video: nothing to judge
            elif acceptable(text, min_chars, max_chars):
                kept.append((text, {"source": f"r/{sub}", "url": row["url"], "id": row["id"],
                                   "score": None, "kind": "post"}))
                if len(kept) >= limit:
                    break
            else:
                quality += 1
        after = rows[-1]["raw_id"]
        if len(kept) >= limit:
            break
    log(f"  {pages} feed page(s), {seen} posts seen:")
    log(f"    kept {len(kept)} text posts | picture/link (no text) {no_text} | "
        f"nsfw/removed {blocked} | short/quoted/link-heavy {quality}")
    if want_scores and kept:
        kept = await add_scores(rx, kept, sleep_s)
    return kept


async def add_scores(rx, items, sleep_s):
    """Open each post's own page for the score feeds omit — and catch what they hide.

    A feed will hand over a post a moderator has since removed and never mention it;
    the page knows. Costs one request per unit, and it is the only way --min-upvotes
    can mean anything, so asking for a floor implies asking for scores. --no-scores
    skips the whole pass and leaves the score column blank.
    """
    log(f"  opening {len(items)} post page(s) for scores and moderation flags...")
    out, missing, flagged = [], 0, 0
    for done, (text, meta) in enumerate(items, 1):
        cards = {c["id"]: c for c in parse_cards(await fetch_page(rx, meta["url"], sleep_s))}
        card = cards.get(meta["id"])
        if card is None:
            missing += 1                    # leave the score blank rather than invent one
        elif card["removed"] or card["stickied"] or card["nsfw"]:
            flagged += 1
            continue
        else:
            meta["score"] = card["score"]
        out.append((text, meta))
        if done % 25 == 0:
            log(f"    {done}/{len(items)} scored")
    if missing:
        log(f"    {missing} unit(s) had no card on the page — score left blank")
    if flagged:
        log(f"    dropped {flagged} removed/stickied/NSFW once the page was open")
    return out


async def collect_comments(rx, sub, sort, time_range, limit, sleep_s, min_chars, max_chars,
                           max_posts=25):
    """Top-level comments off the same listing. One comment = one post-sized unit.

    The page HTML knows which comments are replies and what they scored; the thread's
    own .rss has the bodies. Fetch both, join on the comment id, keep the top-level
    ones — a reply threaded three deep has lost the question it was answering.
    """
    kept, after, posts_read, top_seen = [], None, 0, 0
    while posts_read < max_posts and len(kept) < limit:
        url = feed_url(sub, sort, time_range, after, 25)
        log(f"  fetching candidate posts from {url}")
        rows = [e for e in feed_entries(await fetch_page(rx, url, sleep_s)) if e["kind"] == "t3"]
        if not rows:
            break
        for row in rows:
            if posts_read >= max_posts or len(kept) >= limit:
                break
            if row["nsfw"] or row["body"].strip().lower() in SKIP_TEXTS:
                continue
            posts_read += 1
            thread = row["url"] if row["url"].startswith("http") else BASE + row["url"]
            cards = [c for c in parse_comments(await fetch_page(rx, thread + "?limit=100", sleep_s))
                     if c["top"]]
            if not cards:
                continue
            feed = await fetch_page(rx, thread.rstrip("/") + "/.rss?limit=100", sleep_s)
            bodies = {e["id"]: e["body"] for e in feed_entries(feed)}
            log(f"    {len(cards)} top-level comment(s) on {thread[-46:]}")
            for card in sorted(cards, key=lambda c: -c["score"]):
                top_seen += 1
                text = bodies.get(card["id"], "").strip()
                if acceptable(text, min_chars, max_chars):
                    kept.append((text, {"source": f"r/{sub} (comment)",
                                      "url": card["url"] or thread,
                                      "id": card["id"],
                                      "score": card["score"],
                                      "kind": "comment"}))
                    if len(kept) >= limit:
                        break
        after = rows[-1]["raw_id"]
    log(f"  read {posts_read} thread(s): {top_seen} top-level comments seen, "
        f"{len(kept)} passed")
    return kept


def _units_from_feed(raw, min_chars, max_chars):
    """A saved Atom feed, the same way the live collector reads one."""
    sub = (re.search(r'<category[^>]*label="(r/[^"]+)"', raw)
           or re.search(r"reddit\.com/r/([A-Za-z0-9_]+)", raw)
           or [None, "?"])[1]
    if not sub.startswith("r/"):
        sub = f"r/{sub}"
    out = []
    for entry in feed_entries(raw):
        if entry["kind"] == "t3":
            text, kind = post_text(entry["title"], entry["body"]), "post"
        elif entry["kind"] == "t1":
            text, kind = entry["body"].strip(), "comment"
        else:
            continue
        if text is None or entry["nsfw"] or not acceptable(text, min_chars, max_chars):
            continue
        out.append((text, {"source": sub, "url": entry["url"], "id": entry["id"],
                           "score": None, "kind": kind}))
    return out


def _units_from_json(raw, min_chars, max_chars):
    """A pre-lockdown listing/post .json dump, if that's what you have on disk."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    layers = [layer for layer in (data if isinstance(data, list) else [data])
              if isinstance(layer, dict)]
    out = []
    for layer in layers:
        for child in layer.get("data", {}).get("children", []):
            d = child.get("data", {})
            if d.get("over_18") or d.get("removed_by_category") or d.get("stickied"):
                continue
            if child.get("kind") == "t3":
                text, kind = post_text(d.get("title", ""), d.get("selftext", "")), "post"
            elif child.get("kind") == "t1" and d.get("depth", 1) == 1:
                text, kind = (d.get("body") or "").strip(), "comment"
            else:
                continue
            if text is None or not acceptable(text, min_chars, max_chars):
                continue
            out.append((text, {"source": f"r/{d.get('subreddit', '?')}",
                              "url": f"{BASE}{d.get('permalink', '')}",
                              "id": d.get("id", ""),
                              "score": d.get("ups", 0),
                              "kind": kind}))
    return out


def items_from_files(paths, min_chars, max_chars):
    """Parse browser-saved pages into items — Atom feeds, or old listing JSON."""
    kept = []
    for path in paths:
        raw = Path(path).read_text(encoding="utf-8", errors="replace")
        if "<entry" in raw:
            units = _units_from_feed(raw, min_chars, max_chars)
        elif "<shreddit-post" in raw:
            log(f"  {path}: saved HTML carries titles and scores but not post bodies. "
                f"Save the FEED instead: open the listing's .rss address "
                f"(reddit.com/r/<sub>/<sort>/.rss?t=year), save it, pass that here.")
            continue
        else:
            units = _units_from_json(raw, min_chars, max_chars)
            if units is None:
                log(f"  {path}: neither an Atom feed nor Reddit listing JSON, skipped")
                continue
        kept += units
        log(f"  {path}: {len(units)} unit(s); {len(kept)} kept so far")
    return kept


def dedupe(items):
    seen, out = set(), []
    for text, meta in items:
        key = " ".join(text.lower().split())
        if key in seen:
            continue
        seen.add(key)
        out.append((text, meta))
    return out


async def collect_all(args, sleep_s):
    """One reddrix session for the whole run: cookies warmed once, reused throughout."""
    log(f"Starting reddrix (http_client={args.http_client}) and warming Reddit cookies...")
    want_scores = not args.no_scores
    if args.min_upvotes > 0 and not want_scores:
        log("  --min-upvotes needs scores, so --no-scores is ignored this run.")
        want_scores = True

    async with Reddrix(http_client=args.http_client, verbose=args.verbose) as rx:
        log("  cookies warmed once, then reused - one session for the whole run.")

        items = []
        if args.mode in ("posts", "both"):
            n = args.limit if args.mode == "posts" else args.limit // 2 + 1
            items += await collect_posts(rx, args.sub, args.sort, args.time, n,
                                        sleep_s, args.min_chars, args.max_chars, want_scores)
        if args.mode in ("comments", "both"):
            n = args.limit if args.mode == "comments" else args.limit // 2
            items += await collect_comments(rx, args.sub, args.sort, args.time, n,
                                           sleep_s, args.min_chars, args.max_chars)
    return items


def main():
    parser = argparse.ArgumentParser(
        description="Collect Reddit post bodies into a labels.csv skeleton "
                    "(label left blank — you fill it).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--sub", help="subreddit name without the r/, e.g. running")
    parser.add_argument("--sort", default="top", choices=["top", "hot", "new", "rising"])
    parser.add_argument("--time", default="year",
                       choices=["hour", "day", "week", "month", "year", "all"],
                       help="window for --sort top (ignored by other sorts)")
    parser.add_argument("--limit", type=int, default=250,
                       help="keep at most this many units (aim ~250 to land on 200)")
    parser.add_argument("--mode", default="posts", choices=["posts", "comments", "both"],
                       help="post bodies, top-level comments, or both")
    parser.add_argument("--min-chars", type=int, default=120,
                       help="shorter units rarely carry a label signal")
    parser.add_argument("--max-chars", type=int, default=0,
                       help="0 = no ceiling; keep whole posts whatever their length "
                            "(the template's rule). Set e.g. 3000 only if you "
                            "deliberately want to skip long essays")
    parser.add_argument("--min-upvotes", type=int, default=0,
                       help="e.g. 20 for top-quality takes; 0 keeps all. Needs "
                            "scores, so it overrides --no-scores")
    parser.add_argument("--no-scores", action="store_true",
                       help="skip the per-post page fetches: quicker and gentler on "
                            "Reddit, but the score column stays blank and you lose "
                            "the removed/stickied/NSFW re-check the page gives")
    parser.add_argument("--shuffle", action="store_true",
                       help="shuffle before writing so listing order doesn't bias "
                            "your labelling session")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="collected_raw.csv",
                       help="text,label,note skeleton (label blank)")
    parser.add_argument("--meta", default="collected_meta.csv",
                       help="sidecar with url/score per row for your README's "
                            "provenance; '' to skip")
    parser.add_argument("--from-file", nargs="+", metavar="PAGE.rss",
                       help="parse saved feeds (.rss/.xml) or old listing .json "
                            "instead of fetching")
    parser.add_argument("--http-client", default="curl_cffi",
                       choices=["curl_cffi", "camoufox"],
                       help="how reddrix reaches Reddit: curl_cffi is quick and light "
                            "(and gets through today); camoufox drives a stealth "
                            "browser - run `reddrix install` once before using it")
    parser.add_argument("--verbose", action="store_true",
                       help="show reddrix's own timestamped logs (cookie renewal, retries)")
    parser.add_argument("--sleep", type=float, default=1.0,
                       help="seconds between requests, jittered upwards; keep >= 0.5")
    args = parser.parse_args()

    if args.from_file:
        items = items_from_files(args.from_file, args.min_chars, args.max_chars)
    else:
        if not args.sub:
            parser.error("--sub is required unless using --from-file")
        if Reddrix is None:
            raise RuntimeError(MISSING_DEPS)
        sleep_s = max(args.sleep, 0.5)
        window = f", top of {args.time}" if args.sort == "top" else ""
        log(f"Fetching r/{args.sub} through reddrix - sort={args.sort}{window}, "
            f"target {args.limit} unit(s).")
        items = asyncio.run(collect_all(args, sleep_s))

    before = len(items)
    items = dedupe(items)
    if args.min_upvotes > 0:
        items = [it for it in items if (it[1]["score"] or 0) >= args.min_upvotes]
    if args.shuffle:
        random.Random(args.seed).shuffle(items)

    if not items:
        log("\nNothing collected. Loosen --min-chars, change --sort/--time, or check the sub.")
        sys.exit(1)

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_ALL)
        writer.writerow(["text", "label", "note"])
        for text, _meta in items:
            writer.writerow([text, "", ""])       # the labelling is yours, not the script's

    if args.meta:
        with open(args.meta, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, quoting=csv.QUOTE_ALL)
            writer.writerow(["text", "source", "url", "score", "kind"])
            for text, meta in items:
                score = meta["score"]
                writer.writerow([text, meta["source"], meta["url"],
                               "" if score is None else score, meta["kind"]])

    log(f"\ndropped {before - len(items)} via dedupe/upvotes; kept {len(items)} units")
    log(f"Wrote {args.out} (label column blank — fill it by hand; first 20 unaided "
        f"get note 'cold').")
    if args.meta:
        log(f"Wrote {args.meta} (urls + scores for your README's provenance section).")
    log("Collect ~250 to have 200 after pruning. Commit labels.csv when it's "
        "labelled — not before.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as err:      # Reddit blocked / junk response: message, not traceback
        log(f"\n{err}")
        sys.exit(1)

