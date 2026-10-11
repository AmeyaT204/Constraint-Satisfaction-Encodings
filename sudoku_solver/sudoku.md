# Sudoku Z3 SAT Solver

A Python-based Sudoku solver that models a 9×9 Sudoku puzzle as a Boolean satisfiability (SAT) problem using the Z3 theorem prover.

## Overview

The solver defines a three-dimensional grid of Boolean variables and applies the fundamental rules of Sudoku as logical constraints. Z3 evaluates these constraints to find a valid assignment for all variables, producing a solved 9×9 board.

## Prerequisites

- Python 3
- The Z3 solver library

Install the dependency with:

```bash
pip install z3-solver
```

## SAT Encoding Strategy

The puzzle is modeled using a 9×9×9 three-dimensional array of Boolean variables:

```python
grid[i][j][k]
```

- `i` represents the row (0–8).
- `j` represents the column (0–8).
- `k` represents the digit (0–8), corresponding to Sudoku digits 1–9.

If `grid[i][j][k]` is `True`, the cell at row `i` and column `j` contains the digit `k + 1`.

### Constraints

The solver applies the following constraints:

1. **Cell constraint:** Every cell `(i, j)` contains exactly one digit.
2. **Row constraint:** Every row contains each digit exactly once.
3. **Column constraint:** Every column contains each digit exactly once.
4. **3×3 block constraint:** Every 3×3 sub-grid contains each digit exactly once.
5. **Clue constraint:** Every given digit is fixed to its provided value.

Together, these constraints ensure that any satisfying assignment is a valid solution to the Sudoku puzzle.

## Input File Format

Clues are loaded from a text file, for example `tests/easy_puzzle1.txt`. The parser reads the file row by row.

- Digits `1` through `9` are treated as fixed clues and added to the solver as hard constraints.
- Other characters (such as `.`, `0`, `_`, or letters) are treated as empty cells.
- Commas and spaces are ignored.

Each puzzle should contain nine rows, with nine cell entries per row.

### Example input

Save the following as `tests/easy_puzzle1.txt`:

```text
5, 3, ., ., 7, ., ., ., .
6, ., ., 1, 9, 5, ., ., .
., 9, 8, ., ., ., ., 6, .
8, ., ., ., 6, ., ., ., 3
4, ., ., 8, ., 3, ., ., 1
7, ., ., ., 2, ., ., ., 6
., 6, ., ., ., ., 2, 8, .
., ., ., 4, 1, 9, ., ., 5
., ., ., ., 8, ., ., 7, 9
```

## Usage

1. Save the puzzle in a text file using the format above.
2. Update the file path in the `load_clues_from_file` call at the bottom of `sudoku_solver.py`:

   ```python
   load_clues_from_file("tests/your_puzzle_file.txt", s, grid)
   ```

3. Run the script from the directory containing `sudoku_solver.py`:

   ```bash
   python sudoku_solver.py
   ```

## Output

If the clues are consistent with the Sudoku rules, the solver prints a message similar to:

```text
Satisfiable! The valid state is:
```

followed by the completed 9×9 grid.

If the constraints contradict one another or no solution exists, it prints:

```text
Unsatisfiable: No solution exists.
```

## Notes

- `Satisfiable` means at least one solution satisfies all encoded constraints.
- `Unsatisfiable` means no solution satisfies the encoded constraints.
- A SAT solver may return one valid solution; this does not necessarily prove that the puzzle has a unique solution.
