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
"Sipeed announces MaixStation, comparable to Strix Halo and DGX Spark"

**Example 2:**
"Qwen-Image-2.1-Turbo released!

Qwen-Image-2.1-Turbo, create and edit images in just 8 denoising steps! Open weights now available!

 Built on Qwen-Image-2.1, Turbo is an accelerated checkpoint on the same 7B visual generation architecture. 

 Fewer steps does not mean lower quality: it still generates strong 2K images from text, and supports continued creation through natural-language edits, from adding accessories to changing a scene.

 Start directly with Diffusers: load QwenImage21Pipeline and the checkpoint’s recommended 8-step sampling schedule is ready to go. 

 Hugging Face: https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo"

### `advice`

**Definition:**
Asks for advice or guidance about what to purchase, or tech support.

**Example 1:**
"Title: Thinking about running Ling-3.1-flash on 4× DGX Spark — how practical is this?

Ant Ling posted this demo of Ling-3.1-flash turning rough briefs into UIs and interactive prototypes. The weights are on HF now, and I'm thinking about running it across 4 DGX Sparks.

 The model card lists 560B total parameters with 25B active per token. Their deployment examples use 8× H200 or 4× GB300, so I'm trying to figure out what a realistic Spark setup would look like.

 I'd be using it for coding and iterative UI work. Generate something, review it, ask for changes, repeat. Single-user latency matters more to me than batch throughput.

 What quantization would you start with, leaving enough memory for context and runtime overhead? And which serving stack would you use to split it across four Sparks?

 my bigger question is whether this would feel usable once it starts making tool calls and reading longer contexts. fitting the weights is one thing, waiting forever between edits is another

 Would appreciate advice from anyone running large MoEs across Sparks, especially measured prefill/decode speeds or things you wish you'd known before setting it up."

**Example 2:**
"Please recommend Qwen3.8-Flash-Next llama parameters

I like tinkering with stuff and I think that now I understand at least on surface-level how a dense model like 27B works and what needs to be finetuned for a specific configuration.

 Then, like everyone else, I discovered Strata and running a large moe locally became possible.

 The problem is that I cannot get anywhere close to Strata's speeds with vanilla llama server. I have no idea what most of the moe-specific flags actually do to my machine and it all feels like a huge black box without feedback. It bothers me to not understand what's happening inside and what I need to improve or upgrade to make it better. 

 I'm trying to run an IQ3_XXS on vanilla llama.cpp for which Strata gives about 35 tps on thinking and 50 tps code.

 My best run so far on llama is 15 tps.

 Hardware: 2 x RTX3060 12GB + RAM 64GB.

 I cannot find the specific 800MB mtp q2_0 drafter used by Strata on HF. The only one I found is the mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf, which is 3.5x the size. It makes decode considerably slower. For now I'm testing without mtp at all.

 Tensor split works with dense models, doesn't work with Flash Next (allocating 23087.12 MiB on device 0: cudaMalloc failed). It feels like llama treats it like a 24GB vram card, not 2x12. Anything I should adjust here? 

 Is anyone running on a similar setup? If you could share your working llama recipe for it, I would appreciate it. 

 Thank you"

### `news/discussion`

**Definition:**
Current events in the AI/ML space, memes, humor.

**Example 1:**
"Long Horizon Agents (Surviving Compaction)

I struggled w/ context windows and compaction limits for a while. Post compaction stupidity and loss of context would have agents hallucinating wildly after about the third compaction.

 Pi's context plugin helps, but adding a small proxy in front of my agents that let's them edit their system prompt has nearly stopped hallucination while adding a source of truth that the agent sees each turn.

 To clarify: they don't directly edit their system prompt. They edit a file that the proxy appends to the system prompt. They see this text every turn as if it is their system prompt and it's cache stable between edits. They can swap these files in and out, add more than one, etc.

 I don't claim to have solved the memory issue - my agents still forget things and have to figure them out all over again when they forget to take notes. But they are staying sane. They've been able to maintain state and continue working on the same project indefinitely.

 The first agent to use the proxy as working memory has compacted 62 times on a budget of 128k. It's seen about 232M input tokens and generated 3.8M (i have nfc how this maths). It started out as a coder building a harness. It is now the project manager for the harnessed agents and managing a couple of production jobs. The code it wrote is the asset I wanted; the agent behind the code is the asset I need to protect.

 How are you keeping your agents sane for the next decade?"

**Example 2:**
"Y'all this is a sexy paper; context language models

Paper linky - Context Language Models

 The central idea of the paper is incredibly simple. Give a model the ability to edit its context on-the-go like a file has major benefits on task performance, context management (memory) and even computational efficiency (both wall clock and total flops). Their paper shows mostly benefits and relatively small downsides.

 You can try it out as a plugin for pi!

 In short, pros and cons Pros:

 Improves outcomes on long running tasks Coding and deep research tasks Open discovery problems (long horizon research tasks, /goal loops etc) Inference can become more compute-efficient and wall-clock efficient Note, this depends on a caching optimization in the inference engine Much less context bloat, meaning it's more (V)RAM efficient No more slow and unreliable compacts Cons:

 The cache optimization only exists for SGLang Prompt injections (including hallucinated instructions) are much less likely to be forgotten, increasing risks Requires harness customizations (authors supply a pi plugin) Some more context The approach works by modifying the harness to allow access to the context as a file. A model is allowed to edit the context as it would any other file.

 They've tested the approach on models as small as qwen3.6 9b, as well as on qwen3.8 27b and claude sonnet 4.6.

 Out-of-the-box, meaning just a small addition to the system prompt and tools to edit the context as a file, task performance, context management and efficiency measures remain approximately the same or improve by a little bit. The smaller qwen3.6 9b model in particular lost a little bit of efficiency, suggesting it works better on larger (smarter) models.

 Performance can be massively improved with RL training, which the authors also did.

 Wanna try it out? You can try it out right now if you use pi

 Install the plugin https://github.com/lolipopshock/pi-clm, this comes from the authors directly After installation, adjust settings with /clm settings: Set steering to house-brief.md (modifies the system prompt, I suppose this should be left disabled for RL'd models only, of which there are none right now) Enable ""One tool per turn""; this one is important for performance Enable ""Size trailer""; this one appends context usage after every tool result. Without it, models are much less inclined to modify context on-the-go for large tool calls Fin Let me know how it goes!

 Last, I also consulted this video by ""Prompt Engineering"" on YouTube in addition to the paper: https://www.youtube.com/watch?v=Bgtr1Ue40Jo"

### `showcase`

**Definition:**
The post showcases a particular hardware or tech stack, often with benchmarks, and a
guide for how to replicate

**Example 1:**
"Now you can grow Bonsai on your potato

No more excuses for GPU-poor folks not to start LLMing!

 Full 27B-class reasoning in ternary transformer weights, for llama.cpp (CUDA, Metal, CPU)

 ~9.3x smaller than FP16 (ideal) | 98.2% of FP16 intelligence retained | ~47 tok/s on an Apple M5 Max laptop

 Highlights ~5.9 GB language model (down from ~54 GB FP16) — full 27B-class reasoning on a standard laptop or a single GPU 98.2% of FP16 intelligence retained: 84.78 average across 14 thinking-mode benchmarks — far above the conventional IQ2_XXS build (72.59) at about 82% of its footprint, and within 0.4 points of UD-Q4_K_XL at three times the footprint Retains thinking, reasoning, and agentic behavior deep in the sub-4-bit regime, where conventional low-bit representations collapse: math within half a point of full precision (96.57), coding level with the baseline (89.42), agentic tool calling at 74.92 End-to-end ternary language weights across embeddings, attention projections, MLP projections, and LM head, at a true 1.72 bits per weight — no high-precision escape hatches behind a low-bit label; the vision tower ships as a separate Q8_0 mmproj pack 262K-token context on-device, kept practical by the Qwen3.8-27B hybrid-attention backbone (~75% linear attention) Two GGUF packings with custom ternary hybrid-attention kernels for llama.cpp (CUDA, Metal) — PTQ1_0 packs trits densely (1.75 bits/weight, 5.95 GB), PQ2_0 stores each trit in a 2-bit slot (2.13 bits/weight, 7.21 GB); packed weights are consumed directly, never expanded back to FP16"

**Example 2:**
"Oh-My-Pocket mobile harness (iOS + Android)

Fork of Pi-Pocket that I’m working on, really enjoying coding from my phone 

 Custom router editor
 Better context baseline
 Agent definitions
 Prune before summarizing
 Remote support

 REPO: https://github.com/T-Crypt/oh-my-pocket"

### The hardest boundary

**Which two labels:**
Announcement and Showcase are often difficult to distinguish between, because there are a lot of posts 
where the poster is showcasing a new inference engine, or finetuned model, which also sort of fits into
the announcement category.

**The decision rule I used every time:**
<!-- e.g. "If the post names a specific checkable fact, it's `analysis`, even
     if the tone is heated." -->
If the post is from a user announcing a project that they have been working on, then it is a showcase. If 
it is a new model, or from an established lab, then it is an announcement.

---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:**

200 posts from www.reddit.com/r/localllama, ranked by hot, collected 2026-10-14 with
`collect_localllama.py` — a thin driver over `collect.py`. It goes through Reddit's 
public Atom feed (`reddit.com/r/localllama/hot/.rss`) using the `reddrix` scraper.

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
