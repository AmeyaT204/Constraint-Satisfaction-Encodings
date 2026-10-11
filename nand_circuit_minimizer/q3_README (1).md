# NANDy's Logic Lab: Exact NAND-Circuit Synthesis with Z3

`q3.py` finds a **minimum-size** circuit of NAND gates (arbitrary fan-in) that computes a given CNF formula. Z3 does the search; the Python code only builds the constraints and decodes the model.

## Requirements

- Python 3.8+
- `z3-solver` (`pip install z3-solver`)
- Nothing else. The file imports only the standard library and `z3`.

## Usage

```python
from q3 import synthesize

synthesize([[-1, 2]])   # (¬x1 ∨ x2)  ->  [[1], [0, 2]]
```

Check it with the provided validator:

```bash
python3 checker.py q3.py                      # all sample tests
python3 checker.py q3.py tests/04_xor.txt     # one test
python3 checker.py q3.py -v                   # print the circuits
```

## Input / output

**Input:** `clauses: list[list[int]]`, where `+i` is `x_i` and `-i` is `¬x_i`. The number of primary inputs `n` is the largest `|literal|`, or `1` if there are no literals. `[]` is the constant `True`, and an empty clause `[]` inside the list is the constant `False`.

**Output:** `list[list[int]]`. Element `k` lists the inputs of gate `k`:

| id | meaning |
|----|---------|
| `0 .. n-1` | primary input `x1 .. xn` |
| `n + j` | output of gate `j` |

Every id in element `k` is `< n + k`, no element is empty, and the last gate is the output.

## How it works

### Outer loop

Try `g = 1, 2, 3, …` gates. The first `g` for which Z3 returns `sat` is the minimum, because every smaller `g` was proven `unsat`.

### Encoding for a fixed `g`

Let `rows` be all `2^n` assignments and `target[a]` the CNF's value on assignment `a`.

**Variables**

- `c[j][i]`: gate `j` reads node `i`, for every `i < n + j`. This is what guarantees acyclicity.
- `v[j][a]`: value of gate `j` on assignment `a`.

Primary-input values are constants per row, so they need no variables.

**Constraints**

1. **Fan-in ≥ 1.** `Or(c[j][0], …, c[j][n+j-1])`.
2. **NAND semantics.** For every gate `j` and row `a`:

   `v[j][a] == Not( And_i ( Or(Not(c[j][i]), val(i, a)) ) )`

   The gate is false only when every selected input is true. Unselected inputs are ignored, which gives arbitrary fan-in.
3. **Output.** `v[g-1][a] == target[a]` for every row. The last gate is the circuit output.

**Symmetry breaking** (safe, because a minimum circuit never needs the excluded cases)

- Every non-output gate feeds at least one later gate. Otherwise it could be deleted.
- No two gates have identical input sets. Otherwise one is a removable duplicate.

These prune the search and mostly speed up the `unsat` proofs for `g - 1`.

### Decoding

On `sat`, gate `j`'s inputs are all `i` with `c[j][i]` true in the model.

## Edge cases

| formula | result |
|---------|--------|
| `[]` (constant True) | 2 gates: `NAND(x1)`, then `NAND(x1, g0)` |
| contains an empty clause (constant False) | 3 gates |
| variable below `n` that never appears | still a primary input; its value is a don't-care |

No special-casing is needed. These all come out of the truth-table encoding.

## Complexity and performance

The encoding has about `g · (n + g/2)` selector variables and `g · 2^n` value variables. The cost is dominated by proving `g - 1` gates impossible, so runtime grows quickly with `n` and the minimum size.

Measured on sample-style cases:

| case | min gates | time |
|------|-----------|------|
| `¬x1 ∨ x2`, AND, unsat, XOR, majority-3, tautology | 2, 2, 3, 4, 4, 2 | ≤ 0.1 s |
| one-hot(x1..x3) ∧ (x4 XOR x5), my reconstruction | 10 | ~11 s |

The last row is my own reconstruction of `09_onehot_xor`, not the course file. Re-running with symmetry breaking disabled confirmed that 9 gates is unsatisfiable for that formula, so the symmetry breaking is sound. The course file probably differs slightly from my guess (its listed minimum is 9).

## Rules followed

- The circuit is found by Z3, with no enumeration, hand-built circuits, or hard-coded answers.
- Gates are NAND only, with fan-in ≥ 1 and strictly earlier inputs.
- Minimality comes from the increasing-`g` loop.
