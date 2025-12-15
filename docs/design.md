# System Design & Architecture

## 1. Overview

This project implements a **Voltorb Flip solver** using a **constraint satisfaction approach combined with probabilistic reasoning**.
The solver is designed to be:

* Correct-by-construction
* Fully explainable
* Independent of labeled data
* Objective-aware (level survival vs profit maximization)
* UI-agnostic and web-deployable

Rather than relying on machine learning, the system models Voltorb Flip as a **formal decision-making problem under uncertainty**, ensuring logical guarantees whenever possible.

---

## 2. Design Philosophy

The design follows five core principles:

1. **Logic First, Probability Second**
   Deterministic reasoning is always preferred. Probability is used only when logic is insufficient.

2. **No Labeled Data**
   The solver does not rely on supervised learning or pretrained models.

3. **Fail-Proof Recommendations**
   The solver must never suggest a move that violates known constraints.

4. **Explainability Over Performance**
   Every recommendation must be justifiable in human-readable terms.

5. **Separation of Concerns**
   Logical reasoning, probability estimation, decision policy, and UI are strictly decoupled.

---

## 3. High-Level Architecture

The system is structured as a pipeline of independent layers:

```
User Input (board state / actions)
        ↓
Board State Manager
        ↓
Constraint Satisfaction Engine
        ↓
Deterministic Resolution
        ↓
(If ambiguity remains)
Probability Estimation Engine
        ↓
Policy Engine (Level / Profit / Quit)
        ↓
Ranked Recommendations + Explanation
```

Each layer operates independently and exposes a clean interface to the next.

---

## 4. Core Components

### 4.1 Board State Manager (`core/board.py`)

Responsibilities:

* Represent the current board state
* Track revealed tiles and unknown tiles
* Maintain row/column constraints (sum and Voltorb count)
* Apply user actions (flip, mark, undo)

This module contains **no solving logic**.

---

### 4.2 Constraint Satisfaction Engine (`core/constraints.py`, `core/solver.py`)

This is the logical backbone of the solver.

Responsibilities:

* Model each cell as a variable with domain `{0,1,2,3}`
* Enforce row and column constraints
* Eliminate impossible values via constraint propagation
* Detect contradictions early

Guarantees:

* Any move marked as “safe” is provably non-Voltorb
* Any cell marked as “certain Voltorb” must contain a Voltorb

---

### 4.3 Probability Engine (`probability/`)

Used **only when deterministic reasoning cannot progress**.

Responsibilities:

* Generate valid board configurations consistent with constraints
* Estimate per-cell Voltorb probability via sampling
* Compute expected value (EV) for each cell

This module **does not override** logical conclusions.

---

### 4.4 Policy Engine (`policies/`)

The policy layer determines *what to do*, not *what is possible*.

Supported policies:

* **Level Maximization**: minimize probability of losing the current level
* **Profit Maximization**: maximize expected coin gain
* **Quit Recommendation**: suggest quitting when risk exceeds benefit

Policies consume:

* CSP results
* Probability estimates
* Game progression state

---

### 4.5 Engine Orchestrator (`engine.py`)

Responsibilities:

* Coordinate all subsystems
* Decide which engine to invoke
* Produce ranked move suggestions with explanations
* Remain UI-independent

This is the **single entry point** for any interface (CLI, web, etc.).

---

## 5. Deterministic vs Probabilistic Flow

The solver always follows this order:

1. Apply constraint propagation
2. If a guaranteed-safe move exists → recommend it
3. If guaranteed Voltorbs exist → mark them
4. If ambiguity remains:

   * Estimate probabilities
   * Apply selected policy
5. If risk exceeds threshold:

   * Recommend quitting (policy-dependent)

This ordering is **never violated**.

---

## 6. Objective-Aware Solving

The solver supports multiple objectives without changing core logic.

### Level Maximization Mode

* Prioritizes survival probability
* Minimizes Voltorb exposure
* May recommend quitting to retain level

### Profit Maximization Mode

* Targets high-value tiles (2s, 3s)
* Accepts higher risk
* Optimizes expected reward

Policies are interchangeable and extensible.

---

## 7. UI Independence & Web Deployment

The solver core:

* Does not depend on UI frameworks
* Exposes clean data structures
* Can be wrapped by:

  * CLI
  * REST API (FastAPI)
  * Web frontend

This ensures future deployment requires **no refactor of logic**.

---

## 8. Non-Goals

This project explicitly avoids:

* Supervised machine learning
* Deep learning
* Reinforcement learning
* Heuristic-only solvers
* Black-box decision making

These approaches offer no correctness guarantees for this problem.

---

## 9. Summary

This system treats Voltorb Flip as a **formal reasoning and decision problem**, not a pattern-recognition task.
By combining constraint satisfaction, probabilistic estimation, and policy-driven optimization, the solver achieves correctness, transparency, and flexibility without reliance on data-driven models.

---

End of document.
