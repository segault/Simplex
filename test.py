#INPUT - Ulvi

def show_tableau(tableau):
    print("\nTableau:")
    for row in tableau:
        print(row)

def build_tableau(objective_coeffs, constraints, max):
    tableau = []
    j = 0
    for i in range(len(constraints)):
        tableau.append(constraints[i][0:-1])

        slack = [0] * len(constraints)
        slack[i] = 1
        tableau[j] += slack

        tableau[j].append(constraints[i][-1])
        j+=1

    if max:
        for i in range(len(objective_coeffs)):
            objective_coeffs[i] *= -1

    tableau.append(objective_coeffs + [0] * len(constraints) + [0])
    return tableau

def get_input():
    max = False

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

        print("\nObjective Function Coefficients:", objective_coeffs)
        print("Constraints:")
        for constraint in constraints:
            print(constraint)

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

    if not max:
        for i in range(len(objective_coeffs)):
            objective_coeffs[i] *= -1

    return build_tableau(objective_coeffs, constraints, max)

# PHASE I - JAVI/ULVI

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

    if len(ratios) == 0:
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
            tableau[y] = [tableau[y][x] - factor * tableau[row][x] for x in range(len(tableau[0]))]


if __name__ == "__main__":
    tableau = get_input()
    show_tableau(tableau)

    tableau2 = tableau.copy()
    while check_negative(tableau2):
        phaseI(tableau2)

    show_tableau(tableau2)
