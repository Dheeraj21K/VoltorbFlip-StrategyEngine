# Voltorb Flip Solver

*A Constraint-Based, Explainable Decision System*

---

## Overview

This project implements a **Voltorb Flip solver** using **formal constraint satisfaction and probabilistic reasoning**, rather than machine learning.

The solver is designed to be:

* Correct-by-construction
* Fully explainable
* Independent of labeled data
* Objective-aware (level survival vs profit maximization)
* Suitable for interactive and web-based use

Voltorb Flip is treated not as a guessing game, but as a **structured decision problem under uncertainty**, where logical guarantees are applied first and probability is used only when unavoidable.

---

## Motivation & Origin

This project started from a very practical frustration.

While playing *Voltorb Flip* in Pokémon HeartGold/SoulSilver, the grind to obtain high-value rewards (such as **Dratini**) became increasingly slow and inconsistent. Even after learning commonly shared strategies and guides, progress often stalled due to unavoidable losses or overly conservative play.

I experimented with existing Voltorb Flip solvers, but repeatedly encountered issues:

* They were **slow** or inefficient
* They did not explicitly optimize for **level retention or profit**
* Most importantly, they lacked **transparency** — recommendations were made without clear reasoning, often leading to unexpected losses

Eventually, it became clear that the core issue was not poor strategy, but poor modeling.

Voltorb Flip can be naturally expressed as a **Constraint Satisfaction Problem (CSP)** with explicit rules, limited state space, and structured uncertainty. Once viewed this way, several gaps in existing solvers became apparent:

* Logic and probability were often mixed incorrectly
* Heuristics were used where guarantees were possible
* Decision-making lacked objective awareness (survival vs reward)

This project was built to address those gaps.

The goal is not merely to “solve” Voltorb Flip, but to provide:

* **Provably safe decisions when possible**
* **Quantified risk when certainty is impossible**
* **Clear explanations for every recommendation**
* **Explicit optimization objectives**

What began as a personal frustration evolved into a structured, explainable decision system intended to help both casual players and those who want to understand *why* a move is recommended — not just *what* to click.

---

## Key Features

### Constraint Satisfaction Engine (CSP)

* Models each tile as a variable with domain `{0,1,2,3}`
* Enforces row and column sum and Voltorb constraints
* Produces guaranteed-safe and guaranteed-Voltorb deductions

### Probabilistic Risk Estimation

* Uses Monte Carlo sampling over **only valid boards**
* Computes per-tile Voltorb probability
* Estimates expected value (EV) for profit decisions

### Objective-Aware Policies

* **Level Maximization**: survival-first, conservative play
* **Profit Maximization**: reward-first, risk-aware play
* **Quit Recommendation**: suggests stopping when risk outweighs benefit

### Explainability

* Every recommendation includes:

  * Risk estimate
  * Expected outcome
  * Objective alignment
* No black-box decisions

### UI & Web Ready

* Core logic is UI-agnostic
* Designed for CLI first
* Future-ready for web deployment (API + frontend)

---

## Why Not Machine Learning?

This project intentionally avoids supervised or deep learning.

Reasons:

* No labeled dataset is required or assumed
* Logical correctness cannot be guaranteed by ML
* The problem has a small, well-defined state space
* Exact reasoning outperforms learned heuristics

Instead, the solver relies on:

* Constraint Satisfaction
* Monte Carlo sampling
* Expected utility optimization

This results in **stronger guarantees, better transparency, and clearer reasoning**.

---

## Solver Architecture

```
User Input / Board State
        ↓
Constraint Satisfaction Engine
        ↓
Deterministic Deductions
        ↓
(If ambiguity remains)
Probability Estimation
        ↓
Policy Engine
(Level / Profit / Quit)
        ↓
Ranked Move Suggestions + Explanation
```

Each layer is independent, testable, and replaceable.

---

## Modes of Operation

### Level Maximization Mode

* Prioritizes level retention and survival
* Minimizes Voltorb exposure
* May recommend quitting early to preserve progress

### Profit Maximization Mode

* Targets high-value tiles (2s and 3s)
* Accepts higher risk
* Maximizes expected coin gain

---

## Project Structure

```
voltron_flip/
├── src/
│   ├── core/          # Board model & CSP logic
│   ├── probability/  # Monte Carlo & EV
│   ├── policies/     # Decision strategies
│   └── engine.py     # System orchestrator
│
├── docs/              # Design & theory
├── ui/                # CLI (web later)
├── tests/             # Unit tests
└── README.md
```

---

## Getting Started

### Environment Setup

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run (CLI – coming soon)

```bash
python ui/cli.py
```

---

## Documentation

Detailed design documentation is available in `/docs`:

* `design.md` — system architecture & philosophy
* `csp_model.md` — formal CSP formulation
* `probability.md` — Monte Carlo & risk estimation
* `policies.md` — decision strategies
* `limitations.md` — guarantees and edge cases

These documents define the solver’s behavior and should be treated as authoritative.

---

## Guarantees & Limitations

* Guaranteed-safe moves are **provably non-Voltorb**
* Probabilistic moves are explicitly labeled as risk
* Some boards are inherently ambiguous
* The solver never claims certainty where none exists

See `docs/limitations.md` for a full discussion.

---

## Future Work

* Web interface (FastAPI + frontend)
* Visual probability heatmaps
* User-configurable risk tolerance
* Performance optimizations for sampling
* Exportable analysis for learning purposes

---

## License

MIT License (to be added).

---

## Summary

This project demonstrates how **symbolic reasoning and probabilistic decision-making** can outperform machine learning for structured logic games.

It is designed to be:

* Transparent
* Correct
* Extensible
* Production-ready

---

End of README.
