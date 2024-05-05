import sys

def read_matrix(file, diagonal):

    n = len(file[0].split())
    
    n_s_matrix = file[:n-1] # reads first uncommented non-empty n-1 lines (but in HV2 we only have n-2 lines -> mistake ?)
    w_e_matrix = file[n-1:2*n-1]
    
    D_ns = []
    D_we = []
            
    for row in n_s_matrix:
        line = row.split()
        line = [float(entry) for entry in line if entry]
        D_ns.append(line)
        
    for row in w_e_matrix:
        line = row.split()
        line = [float(entry) for entry in line if entry]
        D_we.append(line)
        
    if diagonal:
        diag_matrix = file[2*n-1:]
        D_diag = []
        for row in diag_matrix:
            line = row.split()
            line = [float(entry) for entry in line if entry]
            D_diag.append(line)
    else:
        D_diag =[]
        
    return D_ns, D_we, D_diag


def calculate_dist(i,j,D,D_ns,D_we,D_diag=[]):
    if D[i][j] != None:
        return D[i][j]
    elif i == 0:
        return D_we[0][j-1]+D[0][j-1]
    elif j == 0:
        return D_ns[i-1][0]+D[i-1][0]
    else:
        if D_diag:
            weight = max(D[i-1][j-1]+D_diag[i-1][j-1],D[i][j-1]+D_we[i][j-1], D[i-1][j]+D_ns[i-1][j])
        else:
            weight = max(D[i][j-1]+D_we[i][j-1], D[i-1][j]+D_ns[i-1][j])
        return weight


def manhattan_dist(D_ns, D_we, D_diag=[]):
    n = len(D_we)
    D = [[None for _ in range(n)] for _ in range(n)]
    D[0][0] = 0

    for i in range(n):
        for j in range(n):
            D[i][j] = calculate_dist(i,j,D,D_ns,D_we,D_diag)
    return D


def backtrack(D,D_ns, D_we, D_diag=[]):
    path = ""
    n = len(D_we)
    i = n-1
    j = n-1
    while i>0 or j>0:
        
        if D[i][j] == D[i-1][j]+D_ns[i-1][j]:
            path += "S"
            i -= 1
        elif D[i][j] == D[i][j-1]+D_we[i][j-1]:
            path += "E"
            j -= 1
        elif D_diag:
            if D[i][j] == D[i-1][j-1]+D_diag[i-1][j-1]:
                path += "D"
                i -= 1
                j -= 1
        else:
            print("There was an error while backtracing.")
            break

    return path[::-1]


if __name__ == "__main__":
    
    input = sys.stdin.read().splitlines()
    
    filtered_input = [line for line in input if not line.startswith('#') and line]
    
    diagonal = False
    path = False

    if "-d" in sys.argv:
        diagonal = True
    if "-t" in sys.argv:
        path = True
    
    D_ns, D_we, D_diag = read_matrix(filtered_input, diagonal)
        
    result = manhattan_dist(D_ns,D_we,D_diag)
    
    n = len(D_we)
    if result[n-1][n-1] == int(result[n-1][n-1]):
        print(int(result[n-1][n-1]))
    else:
        print(format(result[n-1][n-1], ".2f"))
    
    if path:
        print(backtrack(result, D_ns, D_we, D_diag))
