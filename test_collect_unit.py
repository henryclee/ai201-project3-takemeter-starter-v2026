#!/usr/bin/env python3
"""The collector's keep/drop rule, checked against collect_plan.md §5.

Run it any time you touch unit() in collect_localllama.py:

    .venv/bin/python test_collect_unit.py

Exit code is 0 when every case agrees with the plan. These are the rules that
decide what a "post" even is, and two of them are the reason 500 units is
reachable at all: a link/image post with no body is kept as its title, and the
URL filter runs on the text that was actually kept.

    .venv/bin/python test_collect_unit.py -v     # list every case
"""

import sys

import collect_localllama as m

MIN_TITLE, MIN_BODY = 40, 120          # the floors the plan settles on

LONG_BODY = ("Here are the numbers and my take on them, which is that the 70B "
             "still needs two GPUs at Q5 and that is the whole story.")


def e(title="", body="", nsfw=False):
    """A feed entry as collect.feed_entries() hands one over."""
    return {"title": title, "body": body, "nsfw": nsfw, "id": "x", "url": "u"}


# (what it proves, the entry, keep it or the reason for dropping it)
CASES = [
    # The rule the starter script gets wrong: no selftext is not no content.
    ("link post kept as title",
     e("Anthropic: we have identified industrial-scale distillation attacks", ""),
     "kept"),
    ("selftext kept whole", e("Llama 4 weights released today with benchmarks", LONG_BODY),
     "kept"),
    ("empty title, long body kept",
     e("", "A body with no title at all but plenty of prose in it, enough to clear the "
           "one hundred and twenty character floor this rule sets for selftext posts."),
     "kept"),
    # Floors: a caption whose payload is the picture carries no label.
    ("meme title dropped", e("Bro whaaaat?", ""), "short-title"),
    ("title 39 chars dropped", e("x" * 39, ""), "short-title"),
    ("title 40 chars kept", e("x" * 40, ""), "kept"),
    ("short selftext dropped", e("Quick q", "how do I quantize"), "short"),
    # Media stubs are not somewhere a claim was made.
    ("bare-url title dropped",
     e("https://example.com/some/long/model-card-path-that-goes-on-for-a-while", ""),
     "media-title"),
    ("[image] title dropped",
     e("[image] my llama standing in the garden looking very pleased with itself", ""),
     "media-title"),
    ("short url title -> length first", e("https://foo.com/bar", ""), "short-title"),
    # Moderation blocks, whichever field the placeholder turns up in.
    ("removed body blocks", e("A real claim about quantization and VRAM", "[removed]"),
     "removed"),
    ("removed in title blocks", e("[deleted]", LONG_BODY), "removed"),
    ("nsfw blocks", e("Some long enough title about llama.cpp builds", LONG_BODY,
                      nsfw=True), "nsfw"),
    # The starter's quoted-opener rule, kept.
    ("quoted opener dropped",
     e('> "LLMs are all the same"', "and here is a long enough reply about it"), "quoted"),
    # URL filter on the KEPT text: a title-only link post is not punished for
    # where its body pointed, while a link that IS the post still goes.
    ("link-heavy selftext dropped",
     e("Check this out",
       "https://example.com/a/very/long/path/with/lots/of/segments/here "
       "https://another.example.org/also/very/long/indeed/my/model"), "link-heavy"),
    ("url with prose kept",
     e("I benchmarked llama.cpp on two M3 Ultra Macs with 512GB RAM",
       "Full repro commands at https://example.com/gist/abc and the short version is "
       "that mmap costs us dearly on the first token"), "kept"),
]


def main():
    verbose = "-v" in sys.argv
    failures = 0
    for name, row, want in CASES:
        text, why = m.unit(row, MIN_TITLE, MIN_BODY)
        got = "kept" if text is not None else why
        if got != want:
            failures += 1
            print(f"[FAIL] {name}: want {want!r}, got {got!r}")
        elif verbose:
            print(f"[ ok ] {name} -> {want}")

    # Verbatim means verbatim: the paragraph breaks of a selftext post survive.
    text = m.unit(e("T", "para one\n\npara two"), MIN_TITLE, 0)[0]
    if text != "T\n\npara one\n\npara two":
        failures += 1
        print(f"[FAIL] selftext not verbatim: {text!r}")
    elif verbose:
        print("[ ok ] selftext kept verbatim, newlines intact")

    # Windows are read in rank order, and a missing page count defaults to 5.
    checks = [
        (m.parse_windows("top:all,top:year,top:month"),
         [("top", "all", 5), ("top", "year", 5), ("top", "month", 5)]),
        (m.parse_windows("top:all:5"), [("top", "all", 5)]),
        (m.parse_windows("new"), [("new", None, 5)]),
        (m.window_label("top", "all"), "top/all"),
        (m.window_label("hot", None), "hot"),
    ]
    for got, want in checks:
        if got != want:
            failures += 1
            print(f"[FAIL] window parsing: want {want!r}, got {got!r}")
        elif verbose:
            print(f"[ ok ] window parsing -> {got}")

    total = len(CASES) + len(checks) + 1
    print(f"{'-' * 52}")
    if failures:
        print(f"{failures} of {total} checks FAILED - the unit rule drifted "
              f"from collect_plan.md §5")
        return 1
    print(f"{total} of {total} checks passed - unit rule matches the plan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
