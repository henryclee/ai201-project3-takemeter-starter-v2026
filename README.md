# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Your community, and what your classifier sorts posts into. Three or four
     sentences. -->

This will be looking at posts from the subreddit localllama (www.reddit.com/r/localllama).

The candidate distinctions I have identified are :
1. The post announces a new piece of hardware, LLM model, agent harness, or other technology being released
2. The post for advice or guidance about what to purchase, or tech support.
3. The post is about current events in the AI/ML space.
4. The post is showcasing a particular tech stack, often with a guide for how to replicate and benchmarks

---

## Label Taxonomy

<!-- Each label: a one-sentence definition and two real examples from your
     reading. Then your decision rule for the hardest boundary.

     The decision rule is worth a point on its own and it's the thing most
     people leave out. Every taxonomy has a hardest boundary. Name yours. -->

### `announcement`

**Definition:**
Announces a new piece of hardware, LLM model, agent harness, or other technology being released.

**Example 1:**
>

**Example 2:**
>

### `advice`

**Definition:**
Asks for advice or guidance about what to purchase, or tech support.

**Example 1:**
>

**Example 2:**
>

### `news/discussion`

**Definition:**
Current events in the AI/ML space, memes, humor.

**Example 1:**
>

**Example 2:**
>

### `showcase`

**Definition:**
The post showcases a particular hardware or tech stack, often with benchmarks, and a
guide for how to replicate

**Example 1:**
>

**Example 2:**
>

### The hardest boundary

**Which two labels:**

**The decision rule I used every time:**
<!-- e.g. "If the post names a specific checkable fact, it's `analysis`, even
     if the tone is heated." -->



---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:**

500 posts from **r/localllama**, ranked by *hot*, collected **2026-10-14** with
`collect_localllama.py` — a thin driver over the starter's `collect.py`. It goes
through Reddit's public **Atom feed** (`reddit.com/r/localllama/hot/.rss`) using the
`reddrix` scraper, so there is no app, no API key and no `.env`. Comments were never
fetched, and no usernames are stored anywhere.

*hot* has no time window of its own — it is whatever the front page is showing — and a
single crawl reaches Reddit's ~500-item cap by itself: **540 posts seen, 520 kept after
the unit rule, trimmed to 500**. The 20 that went were 8 titles under 40 characters and
12 selftext posts under 120. The driver can fall back to `top/day`, `top/week` and
`top/month` to fill a run that comes up short; this one never needed them, so every row
of the sidecar carries `window=hot`.

Currency is then checkable per row rather than asserted: the sidecar keeps each post's
own creation timestamp, and the crawl spans **0 to 9 days old (median 5)**, with 404 of
the 500 inside a week.

Popularity is checkable too, with one honest asterisk. A second pass opened all 500 post
pages: **403 disclose a score — minimum 1, median 26, 90th percentile 301, maximum
5,234**. The other **97 are left blank, not zeroed**. Reddit omits the `score`
attribute on posts whose tally it declines to disclose, and `int(a.get("score") or 0)`
turns that absence into a 0 — so a naive sidecar would claim 97 posts sit at nil
upvotes when Reddit never said so. The driver re-opens those rows and blanks the score
(`blank_hidden_scores()`). The same pass re-checks the moderation flags the feed omits,
and found no removed, stickied or NSFW posts among the 500.

Units are whole posts, verbatim, untrimmed: **title + selftext** where the post has
selftext, and **the title alone** where it doesn't — **26 of the 500 (5%)** are
link/image posts kept as their title. That is far fewer than the all-time version of this
crawl produced (29%), because *hot* rewards text discussion while the all-time list is
heavy with image posts. The written file is shuffled (`--shuffle --seed 42`) so the
reading order isn't the ranking — with *hot* the two would otherwise be near-identical,
and rank correlates with both topic and recency. URL, id, window, rank, score and posted
date survive in the `labels_meta.csv` sidecar.

Hygiene scan of the finished 500: **no megathreads**, no ad or sponsored markers, zero
duplicate text, zero duplicate post ids, no HTML remnants, no feed footers, no bare-URL
rows. Two rows contain a `utm_` parameter inside a link the poster wrote and six mention
a `u/username` in the body — both are things posters typed, not metadata this collector
added. The exact command that produced these files is recorded at the top of
`collect_localllama.py`.

This dataset carries four caveats:

- **Hot is a snapshot.** The ranking moves continuously, so re-running the same command
  tomorrow yields a different 500. The *command* is reproducible; the *selection* is
  not, and that is the price of choosing currency over a distilled best-of. What stays
  reproducible is the artefact: `labels_meta.csv` pins all 500 post ids, so the corpus
  behind any number in this report is fixed and linkable.
- **Currency costs the score floor.** The all-time variant of this crawl (same
  collector, `--windows top:all:5,top:year:5`, kept alongside as `labels_top.csv`) has
  a minimum disclosed score of 750 and a median of 1,182. This one has a median of 26,
  and 113 of the 403 disclosed scores sit between 1 and 9 upvotes. That is the trade
  being made deliberately: the front page as it actually reads today, including posts the
  community barely touched, rather than the sub's consensus best. The two sets share
  only **12 posts**.
- **26 units (5%) are titles only.** Some carry a full claim (*"Anthropic Executive
  Says Open-Source AI Models Are Higher Risk"*), some carry much less. Expect those rows
  to be the classifier's worst — a finding about link-bait titles, not a flaw in the
  split.
- **`bart-large-mnli` reads only the first ~1,024 tokens (~700 words)**, so the longest
  posts are judged on their opening. 61 rows exceed 3,000 characters and the longest is
  18,827. They are kept whole because the template asks for it ("Keep the whole post —
  don't trim it to fit"), and the number is disclosed here rather than hidden by
  trimming.

**How I labelled them:** <!-- Cold first? Pre-labelled with AI and corrected?
Say so plainly — the disclosure is required, not penalised. -->

**Counts per label:**

| Label | Count | Share |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |
| **Total** |  | 100% |

**Three hard cases**

<!-- Any post that made you pause: what it was, which two labels it could have
     been, and what you chose. These are worth more than the easy 190. -->

**1.**
> *The post:*
>
> *Could have been:*
>
> *I chose, because:*

**2.**
> *The post:*
>
> *Could have been:*
>
> *I chose, because:*

**3.**
> *The post:*
>
> *Could have been:*
>
> *I chose, because:*

---

## The Training Run

<!-- Your starting model, your settings, and anything you changed and why. -->

**Base model:**

**Settings:** <!-- epochs, learning rate, batch size, seed -->

**Anything I changed from the defaults, and why:**

**Split sizes:** <!-- train / val / test, and per-label counts in the test
split. If a label had fewer than about 8 in test, say so — it explains a lot
of next unit's variance. -->



---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the
     problem. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Pre-labelling disclosure:**

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
