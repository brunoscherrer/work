import numpy as np
from scipy.optimize import linprog

def generate_max_affine_problem(n, max_k=3, seed=None):
    """Génère un système max-affine aléatoire."""
    if seed is not None:
        np.random.seed(seed)
    
    K_list = []
    A_list = {}
    b_list = {}
    
    for i in range(n):
        k_i = np.random.randint(1, max_k+1)
        K_i = list(range(k_i))
        K_list.append(K_i)
        for k in K_i:
            A_list[(i,k)] = np.random.uniform(-1, 1, size=n)
            b_list[(i,k)] = np.random.uniform(-1, 1)
    
    return K_list, A_list, b_list

def solve_point_fix(K_list, A_list, b_list, tol=1e-8, verbose=True):
    """Algorithme itératif avec affichage verbose."""
    n = len(K_list)
    K_current = [list(K_i) for K_i in K_list]  # copie des ensembles
    
    iteration = 0
    while True:
        iteration += 1
        if verbose:
            print(f"\n--- Itération {iteration} ---")
            print("Ensembles K_i actuels :", K_current)
        
        # Construction du PL linéaire
        num_vars = n + 1
        c = np.zeros(num_vars)
        c[-1] = 1  # minimiser t
        
        A_ub = []
        b_ub = []
        
        for i in range(n):
            for k in K_current[i]:
                # x_i - A x - b <= t
                row = np.zeros(num_vars)
                row[i] = 1
                row[-1] = -1
                row[:n] -= A_list[(i,k)]
                A_ub.append(row)
                b_ub.append(b_list[(i,k)])
        
        for i in range(n):
            for k in K_current[i]:
                # x_i >= A x + b
                row = np.zeros(num_vars)
                row[i] = -1
                row[:n] += A_list[(i,k)]
                A_ub.append(row)
                b_ub.append(-b_list[(i,k)])
        
        bounds = [(None, None)] * num_vars
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        if not res.success:
            print("PL impossible")
            return None
        
        x = res.x[:n]
        t = res.x[-1]
        
        if verbose:
            print("x =", x)
            print("z =", t)
        
        if t <= tol:
            if verbose:
                print("\nPoint fixe trouvé !")
            return x
        
        # z > 0 : enlever la contrainte la plus violée
        max_violation = -np.inf
        max_pair = None
        for i in range(n):
            for k in K_current[i]:
                violation = x[i] - (A_list[(i,k)] @ x + b_list[(i,k)])
                if violation > max_violation:
                    max_violation = violation
                    max_pair = (i,k)
        
        i_remove, k_remove = max_pair
        K_current[i_remove].remove(k_remove)
        if verbose:
            print(f"Suppression de la contrainte la plus violée : i={i_remove}, k={k_remove}, violation={max_violation:.6f}")
        
        if len(K_current[i_remove]) == 0:
            if verbose:
                print("\nAucun point fixe n'existe : un ensemble K_i est vide.")
            return None

# ---------------------------
# Exemple d'utilisation
# ---------------------------
if __name__ == "__main__":



    n = 10
    max_k = 2


    for s in range(100):

        print("\nSeed:",s)
        
        K_list, A_list, b_list = generate_max_affine_problem(n, max_k, seed=s)
    
        x_star = solve_point_fix(K_list, A_list, b_list, verbose=True)
    
        if x_star is not None:
            print("\nSolution finale :", x_star)
        else:
            print("\nAucune solution n'existe pour ce problème.")
