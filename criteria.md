# Acceptance criteria — TakeMeter

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

## 1.

<!-- Your criterion. It must name a number. -->
The model achieves an overall accuracy of at least 0.65

**Why this target:**
With 4 labels, accuracy of 0.25 would be expected by random chance. A target of 0.65 is substantially higher than this baseline,
and also higher than the 0.50 that would be possible if the model just learns to guess the largest label (0.50 -- see criterion 3)

---

## 2.

<!-- Your criterion. -->
Every label has an F1 of at least 0.55 on the held-out set, and the most frequent label has an F1 of at least 0.70.


**Why this target:**

My smallest label, news/discussion, is 43 of 200 posts — 30 in train and only 6 in my test split. On 6 rows a single swapped post 
moves F1 by roughly 0.1–0.2; 0.55 is the level I can defend as real. showcase, my largest label (65 of 200; 45 train, 10 test), 
should clear 0.70.

---

## 3.

<!-- Your criterion. -->
No single label makes up more than 50% of labels.csv. Every label has at least 30 rows.


**Why this target:**

My counts are announcement 48 (24%), showcase 65 (32.5%), advice 44 (22%), news/discussion 43 (21.5%) — a near-even 
partition of r/localllama. The 50% cap is a guardrail my distribution passes with 17.5 points of margin; the 30-row floor 
means that at a 70/15/15 split a label of exactly 30 rows puts only ~4-5 posts in test, below which a per-label F1 isn't 
meaningful.

---

## 4.

<!-- Your criterion. -->
The trained accuracy on the held-out set exceeds the zero-shot baseline's accuracy by at least 0.05.

**Why this target:**

Every post in r/localllama is about local LLMs, so they all share one surface vocabulary — tok/s, GGUF, VRAM, MoE. My labels 
aren't separable by keywords, and the distinction that matters most (announcement vs showcase) turns on my rig-evidence rule, 
which no zero-shot model knows. That leaves the baseline's best strategy as guessing the largest label (showcase, 32.5% of my 
200). Training on my 139 labelled rows is what teaches the rule, so anything less than a 0.05 accuracy gain means the fine-tune 
added nothing over majority-guessing.


---

## 5.

<!-- Your criterion. -->
When the model’s top predicted probability is at least 0.80, it is correct at least 75% of the time on the held-out set.


**Why this target:**
Confident predictions should be more accurate than the overall .65 target, otherwise the probability score isn't meaningful.

My taxonomy predicts where high confidence should live: advice posts literally ask a question, so those should dominate the 
p ≥ 0.80 set, while the genuinely hard announcement-vs-showcase boundary should sit below it. If confident predictions were 
right no more often than my 0.65 overall bar, the probability column would carry no information about my labels. 0.75 is that 
separation, stated as a number.

> **Revised in unit 6**: 
> (revised) Accuracy on the most-confident third of posts must be at least 0.30 higher than accuracy on the least-confident third.
> 
> **Why this target:**
> (revised) If the confidence is to be meaningful, then it should be more accurate when it is confident, and less accurate 
> when it is not confident. With a test split of 30 posts each confidence third holds 10 posts. That makes the gap coarse: 
> accuracies move in steps of 0.10, and a 0.30 gap means three more correct posts out of ten. A gap of 0.10 or 0.20 would be
> one or two posts, inside what a single flipped prediction could produce.

> **Why revised**: The results.json does not include information about this, so it cannot be measured.
---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 6 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Every label performs acceptably

         The model performs well on all labels.

         **Why this target:** ...

         > **Revised in unit 6:** Every label has an F1 of at least 0.60 on
         > the held-out set.
         >
         > **Why revised:** "performs well" gave me nothing to check. I
         > couldn't produce a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "Overall accuracy of at least 0.65" → "at least 0.55", because
            0.65 turned out to be optimistic for 200 examples.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
