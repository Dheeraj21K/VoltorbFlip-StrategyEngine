# Guarantees, Limitations, and Edge Cases

## 1. Purpose of This Document

This document explicitly states:

* What the solver **guarantees**
* What it **does not guarantee**
* Known limitations inherent to the problem itself

The goal is transparency.
No behavior described here is accidental or hidden.

---

## 2. What the Solver Guarantees

### 2.1 Logical Correctness

When the solver labels a move as **guaranteed safe**, it means:

* The tile is provably non-Voltorb
* No valid board configuration contains a Voltorb at that position
* The recommendation is correct regardless of probability or policy

Similarly, when a tile is marked as a **certain Voltorb**, it is logically unavoidable.

These guarantees are enforced by the **Constraint Satisfaction (CSP) engine**.

---

### 2.2 Constraint Consistency

The solver guarantees that:

* All considered board states satisfy row and column constraints
* No logically impossible configuration is ever sampled or evaluated
* User actions that create contradictions are detected early

---

### 2.3 Explicit Risk Disclosure

When a move is not logically guaranteed:

* The solver reports an explicit Voltorb probability
* Risk is never understated
* Decisions are clearly labeled as probabilistic

The solver never presents probabilistic moves as “safe”.

---

### 2.4 Objective Alignment

Recommendations always respect the selected objective:

* Level Maximization
* Profit Maximization
* Quit Recommendation

The solver does not silently switch objectives or mix policies.

---

## 3. What the Solver Does NOT Guarantee

### 3.1 Guaranteed Success in Ambiguous Boards

Some Voltorb Flip boards are **inherently ambiguous**.

In these cases:

* No tile can be proven safe
* Any continuation involves risk
* Losses may occur even with optimal play

The solver cannot eliminate uncertainty where none can be resolved logically.

---

### 3.2 Optimal Play Under All Conditions

The solver optimizes based on:

* Available information
* Selected policy
* Estimated probabilities

It does **not** guarantee:

* Maximum possible coins
* Level advancement in every run
* Zero losses

These outcomes depend on inherent randomness.

---

### 3.3 Exact Probability Values

Probabilities are estimated using Monte Carlo sampling.

As a result:

* Values are approximate
* Minor variance exists
* Estimates improve with more samples

The solver does not claim exact probabilities unless logically forced (e.g., probability = 0).

---

## 4. Inherent Game Limitations

The following limitations arise from Voltorb Flip itself:

* Some boards require guessing
* Risk cannot always be avoided
* High-reward tiles often correlate with higher risk
* Level progression sometimes forces unfavorable tradeoffs

These are properties of the game, not solver deficiencies.

---

## 5. User-Controlled Risk

The solver:

* Provides recommendations
* Explains consequences
* Offers alternatives

The final decision always remains with the user.

The solver never:

* Forces a move
* Auto-plays without confirmation
* Hides risk to encourage continuation

---

## 6. Known Edge Cases

### 6.1 Contradictory User Input

If the user:

* Marks a tile incorrectly
* Enters incorrect revealed values

The solver may detect:

* An impossible state
* Zero valid board configurations

In such cases, the solver reports a contradiction and halts further recommendations.

---

### 6.2 Low-Sample Confidence

If the probability engine has insufficient samples:

* Estimates may be noisy
* Conservative policies may be preferred
* Quit recommendations may appear earlier

This behavior is intentional.

---

## 7. Design Tradeoffs

The solver prioritizes:

* Correctness over speed
* Explainability over heuristics
* Transparency over aggressive play

This may result in:

* Slower suggestions compared to heuristic solvers
* More conservative behavior in survival mode

These tradeoffs are deliberate.

---

## 8. Non-Goals (Explicit)

This project does not aim to:

* Beat the game with certainty
* Exploit internal game mechanics
* Use hidden or leaked information
* Replace player judgment

It aims to **support informed decision-making**, not remove agency.

---

## 9. Summary

This solver provides strong logical guarantees where possible and honest risk estimates where certainty is impossible.

Losses may still occur — but they will never occur without:

* Clear warning
* Quantified risk
* Explained reasoning

That transparency is the core promise of this project.

---

End of document.
