from z3 import Bool, Solver, And, Or, Not, BoolVal, sat


def _eval_cnf(clauses, bits):
    # value of the CNF under one assignment (bits[j] is x_{j+1})
    for cl in clauses:
        if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in cl):
            return False
    return True


def _try(clauses, n, g, rows, target):
    """Is there a g-gate NAND circuit matching `target` on all rows?"""
    s = Solver()
    # c[j][i]: gate j reads node i (i < n + j)
    c = [[Bool(f"c_{j}_{i}") for i in range(n + j)] for j in range(g)]
    # v[j][a]: value of gate j on assignment a
    v = [[Bool(f"v_{j}_{a}") for a in range(len(rows))] for j in range(g)]

    def val(i, a):
        # value of node i on assignment a (constant for primary inputs)
        return BoolVal(rows[a][i]) if i < n else v[i - n][a]

    for j in range(g):
        # fan-in >= 1
        s.add(Or(c[j]))
        # gate = NAND over the chosen inputs
        for a in range(len(rows)):
            all_true = And([Or(Not(c[j][i]), val(i, a)) for i in range(n + j)])
            s.add(v[j][a] == Not(all_true))

    # output gate computes the formula
    for a in range(len(rows)):
        s.add(v[g - 1][a] if target[a] else Not(v[g - 1][a]))

    # symmetry breaking (safe for a minimum circuit):
    # every non-output gate feeds some later gate
    for j in range(g - 1):
        s.add(Or([c[k][n + j] for k in range(j + 1, g)]))
    # no two gates have identical input sets (duplicates are removable)
    for j in range(g):
        for k in range(j + 1, g):
            diff = []
            for i in range(n + j):
                diff.append(c[j][i] != c[k][i])
            for i in range(n + j, n + k):
                diff.append(c[k][i])  # k reads something j can't see
            s.add(Or(diff))

    if s.check() != sat:
        return None
    m = s.model()
    circuit = []
    for j in range(g):
        circuit.append([i for i in range(n + j)
                        if m.eval(c[j][i], model_completion=True)])
    return circuit


def synthesize(clauses):
    lits = [abs(l) for cl in clauses for l in cl]
    n = max(lits) if lits else 1
    rows = [[bool((a >> j) & 1) for j in range(n)] for a in range(1 << n)]
    target = [_eval_cnf(clauses, r) for r in rows]
    g = 1
    while True:
        res = _try(clauses, n, g, rows, target)
        if res is not None:
            return res
        g += 1