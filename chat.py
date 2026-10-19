# hello
import math

EPS = 1e-9
MAX_ITERATIONS = 10_000


class InfeasibleError(Exception):
    pass


class UnboundedError(Exception):
    pass


def get_input():
    direction = input("Maximize? [Y/n]: ").strip().lower()
    if direction not in ("", "y", "yes", "n", "no"):
        raise ValueError("Enter Y or N.")
    maximize = direction in ("", "y", "yes")

    objective = [
        float(x) for x in input("Objective coefficients: ").split()
    ]
    if not objective or not all(math.isfinite(x) for x in objective):
        raise ValueError("Provide finite objective coefficients.")

    n = len(objective)
    print(f"Enter {n} coefficients, then <=, >=, or =, then RHS.")
    print('Type "done" when finished.')

    constraints = []
    while True:
        entry = input("> ").strip()
        if entry.lower() == "done":
            break

        pieces = entry.split()
        if len(pieces) != n + 2:
            raise ValueError(
                f"Expected {n} coefficients, an operator, and RHS."
            )

        operator = pieces[n]
        if operator not in ("<=", ">=", "="):
            raise ValueError("Operator must be <=, >=, or =.")

        coefficients = [float(x) for x in pieces[:n]]
        rhs = float(pieces[-1])

        if not all(math.isfinite(x) for x in coefficients + [rhs]):
            raise ValueError("All numbers must be finite.")

        constraints.append((coefficients, operator, rhs))

    if not constraints:
        raise ValueError("Enter at least one constraint.")

    return maximize, objective, constraints


def build_tableau(objective, constraints):
    n = len(objective)
    normalized = []

    # Make every RHS nonnegative.
    for coefficients, operator, rhs in constraints:
        if rhs < 0:
            coefficients = [-x for x in coefficients]
            rhs = -rhs
            operator = {
                "<=": ">=",
                ">=": "<=",
                "=": "="
            }[operator]

        normalized.append((coefficients, operator, rhs))

    names = [f"x{i + 1}" for i in range(n)]
    extra_columns = {}
    artificial_columns = {}

    # Add slack and surplus columns.
    for i, (_, operator, _) in enumerate(normalized):
        if operator in ("<=", ">="):
            extra_columns[i] = len(names)
            name = f"s{i + 1}" if operator == "<=" else f"u{i + 1}"
            names.append(name)

    # Add artificial columns.
    for i, (_, operator, _) in enumerate(normalized):
        if operator in (">=", "="):
            artificial_columns[i] = len(names)
            names.append(f"a{i + 1}")

    tableau = []
    basis = []

    for i, (coefficients, operator, rhs) in enumerate(normalized):
        row = coefficients[:] + [0.0] * (len(names) - n)

        if operator == "<=":
            row[extra_columns[i]] = 1.0
            basis.append(extra_columns[i])

        elif operator == ">=":
            row[extra_columns[i]] = -1.0
            row[artificial_columns[i]] = 1.0
            basis.append(artificial_columns[i])

        else:
            row[artificial_columns[i]] = 1.0
            basis.append(artificial_columns[i])

        tableau.append(row + [rhs])

    # Reserve the last row for the objective.
    tableau.append([0.0] * (len(names) + 1))

    return tableau, names, basis, set(artificial_columns.values())


def set_objective(tableau, basis, costs):
    # Tableau convention: Z - sum(c_j * x_j) = 0.
    objective_row = [-c for c in costs] + [0.0]

    # Eliminate coefficients of current basic variables.
    for i, basic_column in enumerate(basis):
        cb = costs[basic_column]

        if cb != 0:
            for j in range(len(objective_row)):
                objective_row[j] += cb * tableau[i][j]

    tableau[-1] = objective_row


def pivot(tableau, basis, pivot_row, pivot_column):
    value = tableau[pivot_row][pivot_column]

    # Make pivot element equal to 1.
    tableau[pivot_row] = [
        x / value for x in tableau[pivot_row]
    ]

    # Eliminate all other entries in the pivot column.
    for i in range(len(tableau)):
        if i == pivot_row:
            continue

        factor = tableau[i][pivot_column]
        if factor != 0:
            tableau[i] = [
                x - factor * y
                for x, y in zip(tableau[i], tableau[pivot_row])
            ]

    basis[pivot_row] = pivot_column


def simplex(tableau, basis):
    columns = len(tableau[0]) - 1

    for iteration in range(MAX_ITERATIONS):
        # Bland's rule: choose leftmost negative coefficient.
        entering = next(
            (j for j in range(columns)
             if tableau[-1][j] < -EPS),
            None
        )

        # No negative coefficients means optimal.
        if entering is None:
            return iteration

        leaving = None
        best_ratio = math.inf

        # Minimum ratio test.
        for i in range(len(basis)):
            a = tableau[i][entering]

            # Only strictly positive coefficients qualify.
            if a <= EPS:
                continue

            b = tableau[i][-1]

            if b < -1e-7:
                raise ArithmeticError("Basis is not feasible.")

            # RHS may be zero.
            ratio = max(0.0, b) / a

            # Break ties by basic variable index.
            if (
                leaving is None
                or ratio < best_ratio - EPS
                or (
                    abs(ratio - best_ratio) <= EPS
                    and basis[i] < basis[leaving]
                )
            ):
                leaving = i
                best_ratio = ratio

        if leaving is None:
            raise UnboundedError("No valid leaving variable.")

        pivot(tableau, basis, leaving, entering)

    raise RuntimeError("Iteration limit reached.")


def remove_artificial(tableau, names, basis, artificial):
    # Remove artificial variables from the basis.
    for i in range(len(basis) - 1, -1, -1):
        if basis[i] not in artificial:
            continue

        if tableau[i][-1] > 1e-7:
            raise InfeasibleError("Artificial variable is positive.")

        entering = next(
            (
                j for j in range(len(names))
                if j not in artificial
                and j not in basis
                and abs(tableau[i][j]) > EPS
            ),
            None
        )

        if entering is None:
            # This constraint is redundant.
            del tableau[i]
            del basis[i]
        else:
            pivot(tableau, basis, i, entering)

    # Remove artificial columns and reindex the basis.
    keep = [
        j for j in range(len(names))
        if j not in artificial
    ]

    new_index = {
        old: new for new, old in enumerate(keep)
    }

    for i, row in enumerate(tableau):
        tableau[i] = [row[j] for j in keep] + [row[-1]]

    basis[:] = [new_index[old] for old in basis]

    return [names[j] for j in keep]


def show_tableau(tableau, names, basis, objective_label="Z"):
    width = 11

    print("\n" + "".join(
        f"{label:>{width}}"
        for label in ["Basis"] + names + ["RHS"]
    ))

    for i, row in enumerate(tableau):
        label = (
            names[basis[i]]
            if i < len(basis)
            else objective_label
        )

        print(
            f"{label:>{width}}"
            + "".join(f"{value:>{width}.5g}" for value in row)
        )


def solve(maximize, objective, constraints, show_steps=False):
    tableau, names, basis, artificial = build_tableau(
        objective, constraints
    )

    n = len(objective)
    phase1_pivots = 0

    # PHASE I: Find an initial feasible basis.
    if artificial:
        costs = [
            -1.0 if j in artificial else 0.0
            for j in range(len(names))
        ]

        set_objective(tableau, basis, costs)

        if show_steps:
            print("\nPhase I initial tableau:")
            show_tableau(tableau, names, basis, "W")

        phase1_pivots = simplex(tableau, basis)

        if tableau[-1][-1] < -1e-7:
            raise InfeasibleError(
                "Phase I optimum is negative."
            )

        names = remove_artificial(
            tableau, names, basis, artificial
        )

    # PHASE II: Optimize the original objective.
    costs = [
        c if maximize else -c
        for c in objective
    ]

    costs += [0.0] * (len(names) - n)

    set_objective(tableau, basis, costs)

    if show_steps:
        print("\nPhase II initial tableau:")
        show_tableau(tableau, names, basis)

    phase2_pivots = simplex(tableau, basis)

    # Extract decision variable values.
    values = [0.0] * n

    for i, basic_col in enumerate(basis):
        if basic_col < n:
            values[basic_col] = tableau[i][-1]

    optimum = sum(
        c * x for c, x in zip(objective, values)
    )

    return (
        values,
        optimum,
        tableau,
        names,
        basis,
        phase1_pivots,
        phase2_pivots
    )


def main():
    try:
        maximize, objective, constraints = get_input()

        values, optimum, tableau, names, basis, p1, p2 = solve(
            maximize,
            objective,
            constraints,
            show_steps=True
        )

        print("\nFinal tableau:")
        show_tableau(tableau, names, basis)

        print("\nStatus: OPTIMAL")

        for i, x in enumerate(values):
            print(f"x{i + 1} = {x:.10g}")

        print(f"Objective value = {optimum:.10g}")
        print(f"Pivots: Phase I = {p1}, Phase II = {p2}")

    except InfeasibleError as error:
        print(f"INFEASIBLE: {error}")

    except UnboundedError as error:
        print(f"UNBOUNDED: {error}")

    except (ValueError, ArithmeticError, RuntimeError) as error:
        print(f"ERROR: {error}")


if __name__ == "__main__":
    main()

