# Constraint Satisfaction Model

## 1. Problem Formalization

Voltorb Flip is modeled as a **Constraint Satisfaction Problem (CSP)**.

A CSP is defined by:

* A set of variables
* A domain of values for each variable
* A set of constraints restricting valid assignments

The goal is to identify all assignments that satisfy the constraints and use them to make safe or optimal decisions.

---

## 2. Variables

Each cell on the 5×5 board is modeled as a variable:

[
X_{i,j} \quad \text{for } i,j \in {1,\dots,5}
]

Where:

* `i` = row index
* `j` = column index

Total variables: **25**

---

## 3. Domains

Each variable has a finite domain:

[
D(X_{i,j}) = {0, 1, 2, 3}
]

Where:

* `0` represents a Voltorb
* `1, 2, 3` represent multiplier tiles

If a tile has already been revealed by the user, its domain collapses to a singleton set.

---

## 4. Constraints

### 4.1 Row Constraints

For each row `r`:

#### Sum Constraint

[
\sum_{j=1}^{5} X_{r,j} = S_r
]

#### Voltorb Count Constraint

[
|{ j \mid X_{r,j} = 0 }| = V_r
]

Where:

* `S_r` is the known row sum
* `V_r` is the known Voltorb count for the row

---

### 4.2 Column Constraints

For each column `c`:

#### Sum Constraint

[
\sum_{i=1}^{5} X_{i,c} = S_c
]

#### Voltorb Count Constraint

[
|{ i \mid X_{i,c} = 0 }| = V_c
]

Where:

* `S_c` is the known column sum
* `V_c` is the known Voltorb count for the column

---

## 5. Global Consistency

A board configuration is **valid** if and only if:

* All variables are assigned values from their domains
* All row constraints are satisfied
* All column constraints are satisfied

There are **no diagonal or adjacency constraints**.

---

## 6. Constraint Propagation

The solver performs **iterative domain reduction** using constraint propagation.

### Key idea:

A value `v ∈ D(X_{i,j})` is removed if:

* No valid row configuration supports it, or
* No valid column configuration supports it

Propagation continues until:

* No further domain reductions are possible, or
* A contradiction is detected (empty domain)

---

## 7. Deterministic Deductions

The CSP model enables several guaranteed deductions:

### Guaranteed Safe Tile

If:
[
0 \notin D(X_{i,j})
]
Then the tile **cannot be a Voltorb**.

### Guaranteed Voltorb

If:
[
D(X_{i,j}) = {0}
]
Then the tile **must be a Voltorb**.

### Forced Assignments

If a row or column has only one configuration satisfying its constraints, all involved cells become fixed.

---

## 8. Contradiction Detection

A contradiction occurs if:

* Any variable domain becomes empty, or
* A row/column has no valid configurations remaining

Contradictions are used to:

* Reject hypothetical assumptions
* Prune invalid board states
* Ensure solver correctness

---

## 9. Relation to Probability Engine

The CSP engine defines the **space of valid boards**.

The probability engine:

* Samples from this space
* Never introduces configurations violating CSP constraints

Thus:

> Probability estimation is strictly subordinate to logical feasibility.

---

## 10. Guarantees Provided by the CSP Layer

The CSP layer guarantees:

* No false “safe” recommendations
* No logically impossible boards considered
* Early detection of impossible user actions

These guarantees hold **independently of policy or probability choices**.

---

## 11. Summary

By modeling Voltorb Flip as a CSP, the solver achieves:

* Formal correctness
* Explainable deductions
* Safe interaction with probabilistic reasoning

This model serves as the **foundation for all higher-level decision making** in the system.

---

End of document.
