# Probabilistic Reasoning & Risk Estimation

## 1. Purpose of the Probability Layer

The probability engine is invoked **only when the CSP engine cannot make further deterministic deductions**.

Its purpose is to:

* Quantify uncertainty
* Estimate risk of selecting a tile
* Enable informed decision-making under ambiguity

It does **not** replace logical reasoning and **never violates CSP constraints**.

---

## 2. Why Probability Is Necessary

Some Voltorb Flip boards are **inherently ambiguous**.

In such cases:

* Multiple board configurations satisfy all constraints
* No tile can be proven safe
* A decision must still be made to continue play

The probability layer provides a **principled fallback** instead of blind guessing.

---

## 3. Definition of the Sample Space

Let:

* Ω be the set of all **valid board configurations**
* Each configuration satisfies all CSP constraints

The probability engine operates exclusively over Ω.

Any configuration not satisfying the CSP constraints is **excluded by construction**.

---

## 4. Monte Carlo Sampling Approach

Exact enumeration of Ω may be expensive in rare cases.
Instead, the solver uses **Monte Carlo sampling**.

### Sampling Procedure

1. Randomly generate a complete board assignment
2. Reject assignments violating CSP constraints
3. Accept valid boards into the sample set
4. Repeat until sufficient samples are collected

This produces an **unbiased approximation** of Ω.

---

## 5. Per-Cell Voltorb Probability

For each cell ( X_{i,j} ):

[
P(X_{i,j} = 0) = \frac{\text{Number of sampled boards where } X_{i,j}=0}{\text{Total sampled boards}}
]

This value represents the **empirical Voltorb risk** of that cell.

---

## 6. Value Distribution Estimation

For each cell, the solver also estimates:

[
P(X_{i,j} = v) \quad \text{for } v \in {1,2,3}
]

These distributions are used to:

* Compute expected value
* Support profit-maximizing decisions

---

## 7. Expected Value (EV)

The expected value of flipping a cell is defined as:

[
EV(X_{i,j}) = \sum_{v=1}^{3} v \cdot P(X_{i,j} = v)
]

Voltorb outcomes (`v = 0`) contribute **zero reward** and are handled separately as risk.

---

## 8. Risk Classification

For interpretability, Voltorb probabilities are mapped to qualitative risk tiers:

* **Guaranteed Safe**: ( P = 0 )
* **Low Risk**: ( 0 < P \leq 0.15 )
* **Medium Risk**: ( 0.15 < P \leq 0.35 )
* **High Risk**: ( P > 0.35 )

Thresholds are configurable and policy-dependent.

---

## 9. Confidence & Sample Size

Monte Carlo estimates improve with more samples.

The solver:

* Uses a fixed or adaptive sample budget
* May report confidence intervals internally
* Never claims certainty unless ( P = 0 )

When sample size is insufficient, the solver may:

* Flag estimates as low-confidence
* Prefer conservative policies

---

## 10. Interaction with Policies

The probability engine provides **raw metrics only**:

* Voltorb probability
* Value distribution
* Expected value

It does **not**:

* Choose moves
* Apply objectives
* Recommend quitting

Those decisions belong exclusively to the policy layer.

---

## 11. Safety Guarantees

The probability layer guarantees:

* No logically impossible board is sampled
* Probabilities are consistent with known information
* Risk is never understated when CSP guarantees are absent

However, it **cannot guarantee survival** in ambiguous states.

---

## 12. Limitations

* Estimates are approximate, not exact
* Sampling variance exists
* Some decisions remain unavoidable risks

These limitations are inherent to the problem, not the method.

---

## 13. Summary

The probability engine transforms logical ambiguity into **quantified risk**, enabling rational decisions when certainty is impossible.
By operating strictly within the CSP-defined space, it complements deterministic reasoning without compromising correctness.

---

End of document.
