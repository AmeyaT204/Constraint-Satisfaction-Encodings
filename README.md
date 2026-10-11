# Constraint Satisfaction & SAT Encodings

This repository contains a collection of three algorithmic solvers developed as a course assignment. The solvers apply SAT solving techniques to effectively model constraints and explore solution spaces for complex logic and planning problems.

The implementations utilizes the Microsoft **Z3 Theorem Prover** via its Python API to encode and solve the constraints.

## Projects Included

The repository is structured into three distinct solver modules:

### 1. [Sudoku Solver](./sudoku_solver)
A SAT-based solver for standard 9x9 Sudoku puzzles. 
* **Encoding:** Maps the puzzle into a 9x9x9 3D array of Boolean variables.
* **Constraints:** Enforces exactly-one logic for cells, rows, columns, and 3x3 blocks.

### 2. [Sokoban Puzzle Solver](./sokoban_solver)
An automated planner for the classic warehouse logic puzzle .
* **Encoding:** Uses a fixed-horizon time-step model (up to 15 steps) to track player movements and box coordinates.
* **Constraints:** Models legal pushing mechanics, interior obstacles, and grid boundaries using propositional logic.
* **Tools:** Includes an independent plan checker and a step-by-step visualizer for debugging state transitions.

### 3. [NAND-Based Circuit Minimizer](./nand_circuit_minimizer)
A logic synthesis tool that converts Boolean formulas in Conjunctive Normal Form (CNF) into exact minimum-size NAND circuits.
* **Encoding:** Restricts the solution to an acyclic graph of NAND gates with arbitrary fan-in. 
* **Constraints:** Evaluates truth tables across all `2^n` variable assignments to ensure functional equivalence while strictly minimizing the total gate count.

## Key Learnings
Building these solvers provided hands-on experience in:
* **Problem Encoding:** Translating physical, spatial, and logical rules into strict Boolean constraints.
* **Constraint Satisfaction:** Leveraging automated theorem provers to explore massive solution spaces efficiently.
* **Algorithm Optimization:** Refining models to reduce variable counts and improve solver execution times.

## Requirements
* Python 3.x
* `z3-solver` package

```bash
pip install z3-solver
