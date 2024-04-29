#IMPORT
import pandas as pd
import argparse

#FUNCTIONS
def call_parser():
    '''
    Parses the argument for use in the Terminal.

    Returns:
    - filename: string of input file name
    - optimise: boolean; should the program optimise?
    '''
    #PARSER
    parser = argparse.ArgumentParser('Calculate the sum of squares')
    parser.add_argument('file', help='The input file')
    parser.add_argument('-o', '--optimise', action='store_true', help='Program gives optimal solution')

    args = parser.parse_args()
    return args.file, args.optimise

def branch_and_bound(matrix, free, bound, path=[], cost=0):
    solutions = []
    if not free:  
        return [path]
    now = free.pop(0)
    for i in free:
        if not pd.isna(matrix.loc[now, i]):
            cost_new = cost + matrix.loc[now, i]
            if cost_new <= bound:
                path_new = path + [now+i]
                free_new = free.copy()
                free_new.remove(i)
                solutions.extend(branch_and_bound(matrix, free_new, bound, path_new, cost_new))
    return solutions

def get_matrix(file_name):
    with open(file_name,'r') as f:
        first = f.readline().split()
        n_capitals = int(first[0])
        if n_capitals%2 != 0:
            raise InputError('The input file specifies an odd number of capitals!')
        bound = int(first[1])
        capitals = f.readline().split()
        matrix_list = []
        for i in range(n_capitals):
            matrix_list.append(f.readline().split())
    free = capitals.copy()
    matrix = pd.DataFrame(columns=capitals, data=matrix_list, index=capitals)
    matrix = matrix.apply(pd.to_numeric, errors='coerce')
    return matrix, free, bound
###########################################################################################

#MAIN
file_name, optimise = call_parser()
matrix, free, bound = get_matrix(file_name)
solutions = branch_and_bound(matrix, free, bound)

#OUTPUT
if optimise:
    for solution in solutions:
        cost=sum(matrix[pair[0]][pair[1]] for pair in solution)
        if cost <= bound:
            bound = cost
    print(bound)

else:   
    for solution in solutions:
        for pair in solution:
            print(pair,end=' ')
        print('')