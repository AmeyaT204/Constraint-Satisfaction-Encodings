from z3 import *


def get_moves(grid):
    """(docstring unchanged)"""
    T = 15

    # --- little grid helpers ------------------------------------------------
    H = len(grid)
    W = max(len(row) for row in grid)

    def ch(r, c):
        # anything off the grid (or past a short row) acts like a wall
        if 0 <= r < H and 0 <= c < len(grid[r]):
            return grid[r][c]
        return '#'

    def blocked(r, c):
        return ch(r, c) == '#'

    def any_(lst):
        # Or() over an empty list is awkward in z3, so be explicit
        return Or(lst) if lst else BoolVal(False)

    cells = [(r, c) for r in range(H) for c in range(W) if not blocked(r, c)]

    # direction name -> (row delta, col delta)
    DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    ACTS = ['U', 'D', 'L', 'R', 'W']   # W = wait

    # --- variables ----------------------------------------------------------
    # P[t][cell]: player stands on cell at time t
    # B[t][cell]: a box sits on cell at time t
    # A[t][a]   : action a is taken between time t and t+1
    P = [{(r, c): Bool(f"P_{t}_{r}_{c}") for (r, c) in cells} for t in range(T + 1)]
    B = [{(r, c): Bool(f"B_{t}_{r}_{c}") for (r, c) in cells} for t in range(T + 1)]
    A = [{a: Bool(f"A_{t}_{a}") for a in ACTS} for t in range(T)]

    s = Solver()

    # --- initial state: pin every variable to what the grid says -----------
    for (r, c) in cells:
        s.add(P[0][(r, c)] if ch(r, c) in '@+' else Not(P[0][(r, c)]))
        s.add(B[0][(r, c)] if ch(r, c) in '$*' else Not(B[0][(r, c)]))

    # --- goal: every goal cell holds a box at the end ----------------------
    # (#boxes == #goals and boxes are never created/destroyed, so this
    #  means every box ends up on a goal)
    for (r, c) in cells:
        if ch(r, c) in '.*+':
            s.add(B[T][(r, c)])

    # --- exactly one action per step ---------------------------------------
    for t in range(T):
        acts = [A[t][a] for a in ACTS]
        s.add(Or(acts))                                  # at least one
        for i in range(len(acts)):
            for j in range(i + 1, len(acts)):
                s.add(Not(And(acts[i], acts[j])))        # atmost one 

    # --- waits only at the tail of the plan --------------------------------
    for t in range(T - 1):
        s.add(Implies(A[t]['W'], A[t + 1]['W']))

    # --- exactly one player cell at t=0 is already pinned; transitions keep it so

    for t in range(T):
        # ---- preconditions: which moves are legal --------------------------
        for (r, c) in cells:
            for d, (dr, dc) in DIRS.items():
                q = (r + dr, c + dc)           # cell the player steps onto
                q2 = (r + 2 * dr, c + 2 * dc)  # cell a pushed box would land on
                here = And(A[t][d], P[t][(r, c)])

                if blocked(*q):
                    # can't walk into a wall / off the map
                    s.add(Not(here))
                    continue

                if blocked(*q2):
                    # q is open, but if it holds a box we couldn't push it
                    s.add(Not(And(here, B[t][q])))
                else:
                    # pushing a box into another box is not allowed
                    s.add(Not(And(here, B[t][q], B[t][q2])))

        # ---- next player position -----------------------------------------
        # you end up on x if you waited there, or stepped onto it from the
        # neighbouring cell with the matching action
        for (r, c) in cells:
            ways = [And(A[t]['W'], P[t][(r, c)])]
            for d, (dr, dc) in DIRS.items():
                src = (r - dr, c - dc)
                if src in P[t]:
                    ways.append(And(A[t][d], P[t][src]))
            s.add(P[t + 1][(r, c)] == any_(ways))

        # ---- next box positions -------------------------------------------
        # a box on x survives unless it gets pushed away from x;
        # a box appears on x if it was pushed in from the adjacent cell
        for (r, c) in cells:
            x = (r, c)
            pushed_away = []
            pushed_in = []
            for d, (dr, dc) in DIRS.items():
                behind = (r - dr, c - dc)          # where the player stands to push x along d
                if behind in P[t]:
                    pushed_away.append(And(A[t][d], P[t][behind]))
                behind2 = (r - 2 * dr, c - 2 * dc)  # player two cells back,
                mid = behind                        # box one cell back
                if behind2 in P[t] and mid in B[t]:
                    pushed_in.append(And(A[t][d], P[t][behind2], B[t][mid]))

            stays = And(B[t][x], Not(any_(pushed_away)))
            s.add(B[t + 1][x] == Or(stays, any_(pushed_in)))

    # --- solve and decode ---------------------------------------------------
    if s.check() != sat:
        return ""

    m = s.model()
    plan = []
    for t in range(T):
        for a in ACTS:
            if is_true(m.eval(A[t][a], model_completion=True)):
                if a != 'W':        # skip the padding waits
                    plan.append(a)
                break
    return "".join(plan)