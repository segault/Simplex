#INPUT - Ulvi
decisions = 0 # silly to make it global but i'm tired
max = False

def show_tableau(tableau):
    print("\nTableau:")
    for row in tableau:
        for col in row:
            print(f"{col:>8.2f}", end=" ")
        print()

def build_tableau(objective_coeffs, constraints):
    global max
    tableau = []
    j = 0
    for i in range(len(constraints)):
        tableau.append(constraints[i][0:-1])

        slack = [0] * len(constraints)
        slack[i] = 1
        tableau[j] += slack

        tableau[j].append(constraints[i][-1])
        j+=1

    if max is True:
        for i in range(len(objective_coeffs)):
            objective_coeffs[i] *= -1

    tableau.append(objective_coeffs + [0] * len(constraints) + [0])
    return tableau

def get_input():
    global max
    global decisions

    try:
        ismax = input("is this a maximum? (Y/n): ")
        if ismax.lower() == "y":
            max = True

        objective_coeffs = []
        constraints = []
        objective_coeffs = list(map(int, input("Enter the coefficients for the objective function\n> ").split()))
        decisions = len(objective_coeffs)

        print(f'Enter the coefficients and RHS for the constraints\nType "done" when finished.')
        while (True):
            input_str = input("> ")
            if input_str.lower() == "done":
                break
            input_list = input_str.split()
            if len(input_list) != decisions + 1:
                print(f"Invalid input. Please enter {decisions} coefficients followed by the RHS value.")
                continue
            constraints.append(list(map(int, input_list)))

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

    return build_tableau(objective_coeffs, constraints)

def check_negative(tableau):
    for i in range(len(tableau[0])):
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
    for i in range(len(tableau)):
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
    return tuple(solution), optimum


if __name__ == "__main__":
    tableau = get_input()
    show_tableau(tableau)

    while check_negative(tableau):
        phaseI(tableau)

    while check_dual(tableau):
        phaseII(tableau)

    coords, optm = extract_soln(tableau)
    print(f"\nOptimal solution found: {optm:.2f} at ")
    for i in range(len(coords)):
        print(f"{coords[i]:.2f}")
