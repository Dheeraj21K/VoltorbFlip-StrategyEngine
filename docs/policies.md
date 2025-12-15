# Decision Policies & Optimization Objectives

## 1. Purpose of the Policy Layer

The policy layer determines **what action to recommend**, given:

* Logical constraints (CSP results)
* Probabilistic estimates
* Current game state (level, progress)

It does **not** modify:

* Constraints
* Probabilities
* Board feasibility

Policies operate strictly on **interpreted information**, not raw guesses.

---

## 2. Policy Separation Principle

The solver cleanly separates:

* **Feasibility** (CSP)
* **Uncertainty** (Probability Engine)
* **Objective** (Policy)

This ensures:

* Correctness is never sacrificed for reward
* Objectives can change without altering core logic

---

## 3. Supported Policies

The solver supports three primary policies:

1. **Level Maximization Policy**
2. **Profit Maximization Policy**
3. **Quit Recommendation Policy**

Policies are mutually exclusive in intent but may interact.

---

## 4. Level Maximization Policy (Survival-First)

### Objective

Maximize the probability of **retaining or advancing the current level**.

### Key Assumptions

* Losing the level is worse than missing potential reward
* Safe progress is prioritized over high-value tiles

### Strategy

1. Determine required number of safe flips to retain level
2. Identify all guaranteed-safe tiles
3. If sufficient safe tiles exist:

   * Recommend them in lowest-risk order
4. If insufficient:

   * Rank tiles by ascending Voltorb probability
5. Evaluate survival probability of required move sequence
6. If survival probability < threshold:

   * Trigger quit recommendation

### Output Characteristics

* Conservative suggestions
* Clear survival probability estimates
* Willingness to stop play early

---

## 5. Profit Maximization Policy (Reward-First)

### Objective

Maximize **expected coin gain**, accepting higher risk.

### Key Assumptions

* Player is willing to lose the level for higher reward
* Risk is acceptable if expected value is high

### Strategy

1. Ignore guaranteed-safe but low-value tiles (e.g., 1s), unless required
2. Rank tiles by expected value (EV)
3. Penalize EV by Voltorb probability (risk-adjusted EV)
4. Recommend tiles with best reward–risk tradeoff
5. Provide safer alternatives when available

### Output Characteristics

* Aggressive recommendations
* Transparent risk disclosure
* Multiple high-reward options

---

## 6. Quit Recommendation Policy

### Objective

Prevent unnecessary loss when continuation is irrational.

### Trigger Conditions

* Level Maximization Mode:

  * Survival probability falls below threshold
* Profit Maximization Mode:

  * Expected future reward < quitting reward
* Global:

  * No move improves expected utility

### Quit Justification

Quit recommendations must include:

* Quantitative reasoning
* Objective alignment
* Clear explanation that risk outweighs benefit

The solver **never forces quitting**.

---

## 7. Utility Modeling

Policies compare moves using **utility functions**.

### Level Utility

[
U_{level} = P(\text{survive remaining flips})
]

### Profit Utility

[
U_{profit} = \mathbb{E}[\text{coins gained}]
]

Policies optimize their respective utility exclusively.

---

## 8. Multi-Move Evaluation

Policies may consider **sequences of moves**, not just single flips:

* Especially for level retention
* Survival probability compounds multiplicatively

This prevents locally optimal but globally risky decisions.

---

## 9. Risk Thresholds

Risk thresholds are configurable:

* Conservative mode (default)
* Balanced mode
* Aggressive mode

Thresholds affect:

* Quit recommendations
* Tile ranking
* Alternative suggestions

---

## 10. Transparency & Explainability

Every policy output must include:

* Objective being optimized
* Risk estimate
* Expected outcome
* At least one alternative option

No recommendation is issued without explanation.

---

## 11. Extensibility

New policies can be added without modifying:

* CSP engine
* Probability engine

Examples:

* Hybrid policy
* User-defined risk tolerance
* Speedrun optimization

---

## 12. Summary

The policy layer transforms logical and probabilistic information into **goal-driven, explainable decisions**.
By separating objectives from feasibility, the solver remains correct, flexible, and user-centric.

---

End of document.
