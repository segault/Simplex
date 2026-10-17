#INPUT - Ulvi

def show_tableau(tableau):
    print("\nTableau:")
    for row in tableau:
        print(row)

def get_input():
    max = False

    try:
        max = input("Is this a maximum? (Y/n): ")
        if max.lower() == "y":
            max = True

        objective_coeffs = []
        constraints = []
        objective_coeffs = list(map(int, input("Enter the coefficients for the objective function\n> ").split()))

        print(f'Enter the coefficients and RHS for the constraints\nType "done" when finished.')
        while (True):
            input_str = input("> ")
            if input_str.lower() == "done":
                break
            constraints.append(list(map(int, input_str.split())))

        print("\nObjective Function Coefficients:", objective_coeffs)
        print("Constraints:")
        for constraint in constraints:
            print(constraint)

    except ValueError:
        print("Invalid input. Please enter numeric values.")
    except Exception as e:
        print(f"An error occurred: {e}")

    if not max:
        for i in range(len(objective_coeffs)):
            objective_coeffs[i] *= -1

    tableau = []
    j = 0
    for i in range(len(constraints)):
        tableau.append(constraints[i][0:-1])

        slack = [0] * (len(constraints[0]) - 1)
        slack[i] = 1
        tableau[j] += slack

        tableau[j].append(constraints[i][-1])
        j+=1

    tableau.append(objective_coeffs + [0] * len(constraints) + [0])
    return tableau

if __name__ == "__main__":
    tableau = get_input()
    show_tableau(tableau)
