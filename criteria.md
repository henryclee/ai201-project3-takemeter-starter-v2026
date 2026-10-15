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
The smallest label will have fewer training examples, so its F1 will be noisier. The largest label should perform more strongly
because it has trained on more training examples.

---

## 3.

<!-- Your criterion. -->
No single label makes up more than 50% of labels.csv. Every label has at least 30 rows.


**Why this target:**
This is a dataset criterion. A model trained on a lopsided file will learn to guess the majority label. 
50% caps the largest label at 2× an even split, so no label can carry the accuracy by itself. In order to be testable, 
every label needs enough rows to appear in the test split at least a few times.


---

## 4.

<!-- Your criterion. -->
The trained accuracy on the held-out set exceeds the zero-shot baseline's accuracy by at least 0.05.

**Why this target:**

In order for the trained model to have any value, it must improve the classification on the dataset over the untrained model.
At least a 0.05 accuracy gap suggests that the training represents a real improvement.


---

## 5.

<!-- Your criterion. -->
When the model’s top predicted probability is at least 0.80, it is correct at least 75% of the time on the held-out set.


**Why this target:**
Confident predictions should be more accurate than the overall .65 target, otherwise the probability score isn't meaningful.


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
