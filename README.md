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
1. Announcement: Announces that a new model / hardware now exists or is available
2. Showcase: Shows what the poster achieved, measured, or configured
3. Advice: The post is asking for advice from the community
4. News/Discussion: Commentary on industry news or drama

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

### `showcase`

**Definition:**
The post showcases a particular hardware or tech stack, often with benchmarks, and a
guide for how to replicate

**Example 1:**
"SonicBoom: 52 tok/s decode on a laptop RTX 3050 (llama.cpp: 45) with the same quantized kernels, the difference is a graph compiler. No Python.

I’ve been building SonicBoom, a native tensor runtime written in C++/CUDA with a C ABI and no Python anywhere in the stack. I just tagged v0.0.1, and the first target is local LLM inference on consumer GPUs.

 Numbers (Gemma 4 E4B-it Q3_K_M on a laptop RTX 3050 8 GB, both runtimes using the same GGUF on the same machine, llama.cpp at commit 43fe9c64281):

 SonicBoom llama.cpp Decode (tg64) 51.65 tok/s 45.20 tok/s Decode @ depth 2048 47.13 tok/s 45.21 tok/s Prefill 4100 tokens 1051 tok/s ~1944 tok/s TTFT, 4000-token prefix + 100 new 503 ms (prefix reuse) Why it matters: the quantized matmul kernels (MMVQ/MMQ) are ported from ggml, so the kernels are the same ones llama.cpp uses. The 14% decode lead comes entirely from the layer above them. A graph planner rewrites the model before it runs: activations are quantized once and reused, norm and activation are fused with quantization, dead computation is removed, and each decode step is captured and replayed as a single CUDA Graph. Code derived from ggml is about 8% of the core. The rest is the runtime.

 Prefix reuse is exact: a continuation is token-for-token identical to a full prefill, which makes multi-turn chat and coding-assistant workloads cheap.

 What it can’t do yet:

 Prefill is about half of llama.cpp. It is a real batched path (int8 tensor-core plus cuBLAS), but there’s more to close. One verified model: Gemma 4 E4B. The quant formats are Q3_K, Q4_K and Q5_K only, so most Q4_K_M files from Hugging Face won’t load yet because they mix in Q6_K and Q8_0. Those formats are next, along with Qwen. It has only been tested on sm_86 (RTX 30-series), and sampling is greedy only. It’s not a drop-in llama.cpp replacement yet. The point of v0.0.1 is to show that the architecture works: once a graph compiler sits on top of the same kernels, the remaining gains come from the compiler instead of more hand-written kernels. Next on the roadmap are MLIR GPU codegen, speculative decoding, and more formats.

 GPL-3.0. Benchmark conditions, reproduce commands and the model sha256 are in the README:
 https://github.com/hardenedlinux/SonicBoom"

**Example 2:**
"omni-d1 600M by Liquid AI running in the browser using WebGPU

Liquid just dropped d1-omni-600M and it's a decision model!

 I ported it to runntime, the WebGPU inference library I'm currently working on. It's plain TypeScript on top of TypeGPU with no WASM and virtually no export step. The model is written directly from our core ops (matmul, attention, norms, a few elementwise bits), and the weights load straight from the HF safetensors.

 The demo in the video is a fake comment feed being moderated live. Each comment gets 4 questions: toxic? spam? asking something? overall tone? Toxic and spam ones get removed.

 ~180 ms per comment for all 4 questions, ~45 ms per question - the performance will most likely be way better once we spend some time tuning the engine for this model

 I also tried making it play snake, but It did not go well lol. 

 The d1 port isn't in the npm release yet. The rest of runntime is (detection, segmentation, speech-to-text, embeddings and more). Docs and live demos: https://docs.swmansion.com/runntime

 Happy to answer questions about the port or WebGPU stuff in general."
 
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


### The hardest boundary

**Which two labels:**
Announcement and Showcase are often difficult to distinguish between, because there are a lot of posts 
where the poster is showcasing a new inference engine, or finetuned model, which also sort of fits into
the announcement category.

**The decision rule I used every time:**
<!-- e.g. "If the post names a specific checkable fact, it's `analysis`, even
     if the tone is heated." -->
If the post contains the poster's own measured runs — their hardware, their configs, reproduction 
steps — it's showcase. This decides even when the post is also announcing a release; rig evidence is decisive. 
Otherwise, if the post's payload is "X is now available — link here," it's announcement. Numbers in an 
announcement are claims about the thing (leaderboard placements, "beats X"), not bench measurements.
Being the author of the thing does not make a post showcase. "I built X — link here" is announcement. 
"I built X — here are my runs" is showcase.

**When two labels both fit — the ladder:**

`advice` > `showcase` > `announcement` > `news/discussion`. When two labels each
independently qualify, the post takes the higher rung: a release post reporting its own runs
is showcase, not announcement; a question carrying a full rig is advice, not showcase.

The ladder only breaks ties between labels that qualify on their own. It never promotes a
post that fails a definition.

---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:**

200 posts from www.reddit.com/r/localllama, ranked by hot, collected 2026-10-14 with
`collect_localllama.py` — a thin driver over `collect.py`. It goes through Reddit's 
public Atom feed (`reddit.com/r/localllama/hot/.rss`) using the `reddrix` scraper.

**How I labelled them:** <!-- Cold first? Pre-labelled with AI and corrected?

20 labelled manually (note is "cold"), and the remainder were labelled by AI, and reviewed.

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| announcement | 48 | 24% |
| showcase | 65 | 32.5% |
| advice | 44 | 22% |
| news/discussion | 43 | 21.5% |
| **Total** |  | 100% |

**Three hard cases**

<!-- Any post that made you pause: what it was, which two labels it could have
     been, and what you chose. These are worth more than the easy 190. -->

**1.**
> *The post:*
"I made a Chrome extension that filters your YouTube feed with a small local model running in the browser (WebGPU, no server)

EDIT (Oct 10): It's now on the Chrome Web Store, so no zip or Developer mode needed: https://chromewebstore.google.com/detail/opendecider-focus/npjgckljljojppjgikkiiaifoojkoebj

 If you installed the zip earlier, remove that copy at chrome://extensions (it won't auto-update) and add the store one. You'll need to download the model once more.
 -----
 My YouTube feed was mostly songs, pranks and celebrity clips, so I built a filter that judges each video title with a small decision model running inside Chrome. Nothing is sent anywhere: no server, no API key, no account, and after one download it works offline.

 What it does

 - Hides the kinds of video you choose (11 kinds: music, gaming, comedy, vlogs, news, how-tos, and so on), or follows a rule you write: ""Hide videos about crypto"", ""Show only videos about cooking""

 - Hides Shorts with one switch

 - Bonus: select any text, right-click, and check it for prompt injection with the same model

 How it runs

 - The model is opendecider-nano (ONNX), loaded through ONNX Runtime Web in an offscreen document

 - fp16 on WebGPU (755 MiB download), q8 on WASM without a GPU (569 MiB)

 - 40 video titles: 1.1 s on WebGPU, about 15 s on CPU (M4 Max). About 3 GiB of RAM while loaded; it unloads after 10 idle minutes

 - The weights are pinned by revision and SHA-256. The only network requests are to Hugging Face for those files

 How well it works

 - On 400 YouTube videos, with the creator's category as the label, rules like ""hide music"", ""hide gaming"" and ""only news"" score 0.934 balanced accuracy on average

 - Sorting videos into the 11 kinds is harder: 0.780. Expect a few comedy and talk-show clips to get through the Focus preset

 - Only evaluated on English titles. If you watch in other languages, I'd really like to know how it does

 Try it (Web Store version is in review):

 Download opendecider-focus-0.8.1.zip from https://github.com/manjunathshiva/opendecider/releases/latest and unzip it chrome://extensions → Developer mode → Load unpacked → pick the folder Click the icon → Download the model Apache-2.0. Benchmarks, code and limits: https://manjunathshiva.github.io/opendecider/guides/chrome-extension/

 The idea comes from Quietly, which does this with a cloud API; I wanted the same thing running on-device. Feedback welcome, especially what it gets wrong."
> *Could have been:*
announcement or showcase
> *I chose, because:*
Showcase. This post actually cleanly fits into both, since it announces a new chrome extension, but also discusses 
the performance on the specific hardware the poster is using (M4 Max). A rule needed to be created to 
handle this overlap so we could have a clean partition. And by the rule, showcase > announcement.

**2.**
> *The post:*
"Now you can grow Bonsai on your potato

No more excuses for GPU-poor folks not to start LLMing!

 Full 27B-class reasoning in ternary transformer weights, for llama.cpp (CUDA, Metal, CPU)

 ~9.3x smaller than FP16 (ideal) | 98.2% of FP16 intelligence retained | ~47 tok/s on an Apple M5 Max laptop

 Highlights ~5.9 GB language model (down from ~54 GB FP16) — full 27B-class reasoning on a standard laptop or a single GPU 98.2% of FP16 intelligence retained: 84.78 average across 14 thinking-mode benchmarks — far above the conventional IQ2_XXS build (72.59) at about 82% of its footprint, and within 0.4 points of UD-Q4_K_XL at three times the footprint Retains thinking, reasoning, and agentic behavior deep in the sub-4-bit regime, where conventional low-bit representations collapse: math within half a point of full precision (96.57), coding level with the baseline (89.42), agentic tool calling at 74.92 End-to-end ternary language weights across embeddings, attention projections, MLP projections, and LM head, at a true 1.72 bits per weight — no high-precision escape hatches behind a low-bit label; the vision tower ships as a separate Q8_0 mmproj pack 262K-token context on-device, kept practical by the Qwen3.8-27B hybrid-attention backbone (~75% linear attention) Two GGUF packings with custom ternary hybrid-attention kernels for llama.cpp (CUDA, Metal) — PTQ1_0 packs trits densely (1.75 bits/weight, 5.95 GB), PQ2_0 stores each trit in a 2-bit slot (2.13 bits/weight, 7.21 GB); packed weights are consumed directly, never expanded back to FP16"
> *Could have been:*
announcement or showcase
> *I chose, because:*
Announcement. Although this post does have benchmarks (47 tok/sec on M5 Max), they are attributed to the model card,
not the poster's own hardware.

**3.**
> *The post:*
"How to get more performance from dual A100 80GB?

Dual A100X PCIe (link at Gen4 x8, weird DPU cards) in a 2U EPYC 7402P box, 256GB DDR4.

 Proxmox with the GPU's passed through to debian 13, 610.43.02 drivers.

 llama.cpp, qwen3.8 flash next UD-Q4_K_XL, Q8_0 MTP head, draft max 2, mmproj enabled. 

 -sm layer -fa on --parallel 7 --ctx-size 1835008 -ub 2048 --cache-ram 32768

 (7 slots x 262k), q8_0 K/V

 Real world single user performance sits around 50-70tk/s. When bumping things up to 2-3 users/sessions, generation drops like a rock, 10-15tk/s. Seeking advice on how to better serve my team at work. We need models worth running and performance that doesn't have us waiting around.

 I'm very partial towards MoE models, so no 27B. Should we swap over to vLLM, or run an instance of qwen3.6-35b-a3b on each card?

 Use case is long session agentic 'coding' (more running linux commands, probing hardware devices). I'm frustrated and not sure how to squeeze more performance out of these. Thanks in advance!"
> *Could have been:*
advice or showcase
> *I chose, because:*
This post asks specifically for advice, but also describes their specific hardware with benchmarks. Again, in the case
where a post meets more than one criteria, the rule above describes order of precedence. advice > showcase.

---

## The Training Run

<!-- Your starting model, your settings, and anything you changed and why. -->

**Base model:**

"distilbert-base-uncased"

**Settings:** <!-- epochs, learning rate, batch size, seed -->

EPOCHS = 3
LEARNING_RATE = 2e-5
BATCH_SIZE = 16
MAX_LENGTH = 512
SEED = 42
**Anything I changed from the defaults, and why:**

Changed MAX_LENGTH from 128 to 512, because my posts are substantially larger

**Split sizes:** 
<!-- train / val / test, and per-label counts in the test
split. If a label had fewer than about 8 in test, say so — it explains a lot
of next unit's variance. -->

train 139  ·  val 31  ·  test 30

                 train  val  test
label                            
announcement        34    7     7
showcase            45   10    10
advice              30    7     7
news/discussion     30    7     6

Test has <8 rows for announcement, advice, and news/discussion

---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the
     problem. -->

**Moment 1**

- *What I asked for:*
I asked AI to scrape my chosen subreddit community for hot posts
- *What came back:*
AI generated labels.csv for me
- *What I changed:*
It initially scraped from "best" but since this isn't timely, I asked it
to rerun the script, but select from "hot" to get a snapshot of what's hot
on a given date (10/14/2026)

**Moment 2**

- *What I asked for:*
I asked AI to review the labels, and automatically label the posts, as well as
to find any problematic posts that would break my label taxonomy partition
- *What came back:*
It found several instances where my initial labels were ambiguous enough that
it could not unequivocally partition the posts into different labels, as well
as suggestions to resolve the problem.
- *What I changed:*
I made the rules for decision between problematic posts more explicit, and 
eventually had to make an order of precedence for when a post met more than
one label's definitions.

**Pre-labelling disclosure:**

I labelled a batch of the labels in labels.csv manually (note = "cold"). The
remainder of the labels were pre-labelled by AI, and reviewed/corrected.

## Stretch Feature 1 - A fourth label

My taxonomy has four labels: announcement, showcase, and advice, plus news/discussion, 
which I added. The first three each pin the poster to a specific artifact. An announcement 
says "this now exists." A showcase says "here are my own measured runs of something." advice 
says "tell me what to buy or how to fix this." All three are about doing or asking things 
with an artifact. 

What none of them captures is the rest of the community's traffic: posts where 
the poster is a commentator — paper walkthroughs, industry news and drama, memes, and open-ended 
experience threads, where the payload is the story and an invitation to discuss.

## Stretch Feature 2 - A second training run

Increased Epochs from 3 to 5. With additional training epochs, the
training and validation loss continued to decrease. Accuracy and F1 Macro
improved through epoch 4 and then plateaued at epoch 5.

Epoch	Training Loss	Validation Loss	Accuracy	F1 Macro
1	     No log	     1.318051	          0.354839	0.183761
2	     1.355900	     1.260350	          0.419355	0.271499
3	     1.273100	     1.192407	          0.516129	0.439699
4	     1.190300	     1.160001	          0.580645	0.512426
5	     1.112100	     1.140679	          0.580645	0.512426

Interestingly, compared to the original run (committed), the even in epochs 2 and 3
we see a difference:

Epoch	Training Loss	Validation Loss	Accuracy	F1 Macro
1	     No log	     1.322101	          0.354839	0.183761
2	     1.356800	     1.275427	          0.387097	0.231579
3	     1.286700  	1.259132	          0.419355	0.263889

This is likely due to the learning rate being related to the total number of epochs, 
so even at epoch 2 and 3, the results diverge between the two runs.


<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

advice           F1 0.000   (n=7)
announcement     F1 0.222   (n=7)
news/discussion  F1 0.400   (n=6)
showcase         F1 0.556   (n=10)

**Baseline**
| Measure | Baseline |
|---|---|
| Overall accuracy | 0.433 |
| Macro F1 | 0.306 |
| F1 — `advice` | 0.444 |
| F1 — `announcement` | 0.222 |
| F1 — `news/discussion` | 0.000 |
| F1 — `showcase` | 0.556 |

**Trained**
| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy | 0.433 | 0.400 | -0.033 |
| Macro F1 | 0.306 | 0.271 | -0.034 |
| F1 — `advice` | 0.444 | 0.000 | -0.444 |
| F1 — `announcement` | 0.222 | 0.615 | +0.393 |
| F1 — `news/discussion` | 0.000 | 0.000 | +0.000 |
| F1 — `showcase` | 0.556 | 0.471 | -0.085 |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->
I predict that the trained model will outperform the baseline model. There are some
edge case rules that are necessary to fully partition the data, that are not derivable
only from the definitions.

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->
The trained model did not beat the baseline. Overall accuracy went from 0.433 to 0.400, and 
macro F1 went from 0.306 to 0.271. On thirty held-out posts, one flip is 0.033, so that gap 
is a single post, so probably not significant.

More notably, announcement's F1 rose from 0.222 to 0.615, while advice fell from 0.444 to 0.
An F1 of exactly zero on a label with 7 true samples means the label stopped predicting advicd
altogether.

---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Measure | Seed 42 | Seed 7 | Seed 2024 | Spread |
|---|---|---|---|---|
| Overall accuracy | 0.400 | 0.333 | 0.367 | 0.067 |
| Macro F1 | 0.271 | 0.125 | 0.187 | 0.146 |
| F1 — `announcement` | 0.615 | 0.000 | 0.000 | 0.615 |
| F1 — `showcase` | 0.471 | 0.500 | 0.526 | 0.056 |
| F1 — `advice` | 0.000 | 0.000 | 0.222 | 0.222 |
| F1 — `news/discussion` | 0.000 | 0.000 | 0.000 | 0.000 |

Accuracy moved 0.067 across seeds. Enough that a criterion landing within that band can't really be called either way.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. overall accuracy of at least 0.65 | 0.65 | 0.400 | 0.333 | 0.367  | MISSED  |
| 2. all F1 >= 0.55, most frequent label F1 >= 0.70 |  |  |  |  |  |
| 3. max label 50%, smallest label >= 30 rows |  |  |  |  |  |
| 4. trained accuracy improvement over baseline >= 0.05 |  |  |  |  |  |
| 5. predicted probability of >= 0.80 is >= 0.75 accurate |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted | announcement | showcase | advice | news/discussion |
|---|---|---|---|---|
| **announcement**       | 4 | 3 | 0 | 0 |
| **showcase**           | 2 | 8 | 0 | 0 |
| **advice**             | 0 | 7 | 0 | 0 |
| **news/discussion**    | 0 | 6 | 0 | 0 |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->
Biggest confusion: 7/7 of the advice posts where misclassified as showcase.

Notably, the second biggest confusion was for news/discussion, where 6/6 of the 
posts wer also misclassified as showcase.

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
