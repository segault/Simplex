#INPUT - Ulvi

def show_tableau(tableau):
    print("\nTableau:")
    for row in tableau:
        for col in row:
            print(f"{col:>8.2f}", end=" ")
        print()

def standardize(consts, coeffs):
    op = coeffs[-2].lower()
    coeffs.pop(-2)
    coeffs = [float(x) for x in coeffs]

    if op == "e":
        consts.append(coeffs); # <=
        consts.append([-x for x in coeffs]) # >= --> <=
    elif op == "ge":
        consts.append([-x for x in coeffs]) # >= --> <=
    else:
        consts.append(coeffs)

def get_input():
    global decisions
    global max
    max = input("Is this a maximization problem? (y/n): ").strip().lower() == 'y'
    decisions = int(input("Enter the number of decision variables: "))
    count = int(input("Enter the number of constraints: "))
    constraints = []
    objective = list(map(float, input("Enter the coefficients and constant (if applicable) \
of the objective function (space-separated):\nO: ").split()))

    # standardize objective
    # moving all terms to the left (given like C = 3x + 3y) negates them
    # but then if minimizing, we negate again to make it a max,
    # therefore only the max really gets negated
    # if max is True:
    #     objective = [-x for x in objective]
    # else:
    #     if len(objective) > decisions:
    #         objective[-1] *= -1 # if there's a constant, it's negated. why?
    #
    if len(objective) == decisions + 1:
        constant = objective.pop()
        if not max:
            constant *= -1 # if there's a constant, it's negated. why?
    else:
        constant = 0.0

    if max is True:
        objective = [-x for x in objective]

    print("Enter constraints, relation (e/ge/le), and RHS (space separated)\n \
e = equals | ge = greater than/equals | le = less than/equals: ")
    for i in range(count):
        coeffs = list(map(str, input(f"{i+1}: ").split()))
        standardize(constraints, coeffs)

    tableau = []
    m = len(constraints)

    for i in range(m):
        constraint = constraints[i]

        slack = [0] * m
        slack[i] = 1

        row = constraint[:-1] + slack + [constraint[-1]]
        tableau.append(row)

    tableau.append(objective + [0] * m + [constant])

    return tableau


def check_negative(tableau):
    for i in range(len(tableau[0])-1):
        if tableau[-1][i] < 0:
            return True
    return False

def phaseI(tableau):
    ratios = []
    col = None
    for i in range(len(tableau[0])-1):
        if tableau[-1][i] < 0: #leftmost first
            col = i
            break

    if col is None:
        return tableau

    #compare ratios
    for j in range(len(tableau)-1):
        if tableau[j][col] > 0:
            ratio = tableau[j][-1]/tableau[j][col]
            ratios.append((ratio, j))

    if not ratios:
        print("PHASE I: No valid ratios found. The problem is unbounded.")
        exit(1)

    #lowest ratio
    lowest, row = min(ratios)

    #pivot
    pivot = tableau[row][col]
    for x in range(len(tableau[0])):
        tableau[row][x] /= pivot

    for y in range(len(tableau)):
        if y == row:
            continue

        else:
            factor = tableau[y][col]

            tableau[y] = [
                    tableau[y][x] - factor * tableau[row][x]
                    for x in range(len(tableau[0]))
            ]

def check_dual(tableau):
    for i in range(len(tableau)-1):
        if tableau[i][-1] < 0:
            return True
    return False

def phaseII(tableau):
    ratios = []
    row = None

    for i in range(len(tableau) - 1):
        if tableau[i][-1] < 0:
            if row is None or tableau[i][-1] < tableau[row][-1]:
                row = i

    if row is None:
        return tableau

    #compare ratios again
    for j in range(len(tableau[0]) - 1):
        if tableau[row][j] < 0:
            ratio = tableau[-1][j] / -tableau[row][j]
            ratios.append((ratio, j))

    if not ratios:
        print("PHASE II: No valid ratios found. The problem is infeasible.")
        exit(1)

    #lowest ratio
    lowest, col = min(ratios)

    #pivot
    pivot = tableau[row][col]
    tableau[row] = [x / pivot for x in tableau[row]]

    for y in range(len(tableau)):
        if y == row:
            continue

        factor = tableau[y][col]

        tableau[y] = [
            tableau[y][x] - factor * tableau[row][x]
            for x in range(len(tableau[0]))
        ]

    return tableau

def extract_soln(tableau):
    global max
    global decisions
    solution = [0.0] * decisions
    eps = 1e-9

    for col in range(decisions):
        for row in range(len(tableau) - 1):
            if (
                abs(tableau[row][col] - 1) < eps
                and all(
                    abs(tableau[k][col]) < eps
                    for k in range(len(tableau) - 1)
                    if k != row
                )
                and abs(tableau[-1][col]) < eps
            ):
                solution[col] = tableau[row][-1]
                break

    optimum = tableau[-1][-1]
    if not max:
        optimum = -optimum
    return tuple(solution), optimum


if __name__ == "__main__":
    tableau = get_input()
    show_tableau(tableau)

    rhs_feasible = all(row[-1] >= 0 for row in tableau[:-1])
    dual_feasible = all(x >= 0 for x in tableau[-1][:-1])

    if rhs_feasible:
        while check_negative(tableau):
            phaseI(tableau)

    elif dual_feasible:
        while check_dual(tableau):
            phaseII(tableau)
    else:
        while check_negative(tableau):
            phaseI(tableau)
        while check_dual(tableau):
            phaseII(tableau)

    coords, optm = extract_soln(tableau)
    print(f"\nOptimal solution found: {optm:.2f} at ")
    for i in range(len(coords)):
        print(f"{coords[i]:.2f}")
