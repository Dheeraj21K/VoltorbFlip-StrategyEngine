# Voltorb Flip Solver

## Overview

**Voltorb Flip Solver** is a transparent, strategy-aware decision support tool for the Pokémon Voltorb Flip minigame.

Unlike brute-force solvers or opaque probability grids, this project treats Voltorb Flip as a **Constraint Satisfaction Problem (CSP)** combined with **risk-aware decision policies**, giving players full control over how they want to play instead of forcing a single “optimal” move.

The solver is designed to be interactive, explainable, and speedrunner-friendly.

---

## Key Features

### Constraint-Based Reasoning
- Models the board using row and column sum + Voltorb constraints
- Performs deterministic elimination before probabilistic reasoning

### Monte Carlo Probability Estimation
- Uses time-bounded sampling when CSP deductions are insufficient
- Estimates per-tile Voltorb probability, expected value, and risk tiers

### Dual Solver Policies

The solver supports two explicit play strategies:

#### Level Maximization Mode
- Prioritizes survival and level retention
- Recommends tiles with the lowest Voltorb probability
- Suggests quitting when survival probability drops

#### Profit Maximization Mode
- Prioritizes expected multiplier gain
- Accepts higher risk for higher reward
- Optimized for aggressive progression

---

## Quit Recommendation

When continuing becomes statistically unfavorable, the solver displays a **non-blocking advisory** suggesting that quitting may be optimal.

This is:
- Inline (not a popup)
- Optional
- Advisory only

The solver advises. The player decides.

---

## User Interface

### Interaction
- Mouse and keyboard navigation (arrow keys supported)
- Click or type to enter revealed values
- Manual **Analyze** button (no auto-play)

### Visual Design
- Calm board layout with minimal color clutter
- Subtle risk overlays
- Single best-move highlight
- Mode-aware visual emphasis

Designed for clarity, speed, and low cognitive load.

---

## Architecture

### Frontend
- React + TypeScript
- Fully typed solver contracts
- Keyboard-first interaction design

### Backend
- FastAPI (Python)
- CSP engine for deterministic inference
- Monte Carlo sampler for probabilistic estimates
- Policy layer for strategy-specific ranking

### Solver Flow

Board Input
↓
Constraint Validation
↓
CSP Deduction
↓
Monte Carlo Sampling (if needed)
↓
Policy Ranking (Level / Profit)
↓
UI Recommendation + Explanation


---

## What This Solver Does Not Do

- No auto-play
- No forced decisions
- No black-box ML guesses
- No hidden heuristics

All recommendations are explainable and transparent.

---

## Project Status

- Core solver complete
- UI complete
- Dual policies implemented
- Ready for deployment

---

## Future Work

- Save and load board states
- Mobile-friendly layout
- Performance optimizations
- Strategy comparison metrics

---

## License

MIT License

---

## Design Philosophy

This project treats Voltorb Flip not as a puzzle to be solved for the player, but as a decision-making problem where risk, reward, and intent matter.
