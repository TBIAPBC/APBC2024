"""
Script for finding all possible pairs for a set of items associated with a given cost, 
while keeping the total cost below a given bound.

"""

import argparse
import sys
import time

FUNCTION_CALLS = 0

def read_input(file_content): 
    """Read input file.
    

    Args:
        file_content (str): file content.
        First line number of capitals and bound. 
        Second line capital names. 
        Following lines cost matrix

    Returns:
        cost_limit (INT): cost limit.
        capitals (list): list of capital names.
        matrix (list): cost matrix.

    """
    
    # list to store cost matrix
    matrix = []
    
    for line_nr, line in enumerate(file_content.split("\n")): 
        # get number of capitals and cost limit from first line
        if line_nr == 0: 
            n_capitals, cost_limit = line.strip().split()
            
        # get capital names from second line  
        elif line_nr == 1:
            capitals = line.strip().split() 
            # sanity check
            assert len(capitals) == int(n_capitals)
            
        # read cost matrix
        else: 
            if line != "\n":
                tmp = [int(x.replace("-", "0")) for x in line.strip().split()]
                if len(tmp) == len(capitals):
                    matrix.append(tmp)


    return int(cost_limit), capitals, matrix


def print_solution(solution, capitals): 
    """ print solution. 
    

    Args:
        solution (list): 
            list containing list of capital indices as first value
            and cost of solution as second value.
        capitals (list): 
            list of capitals, in correct order corresponding to solution indices.

    Returns:
        None.

    """
    
    
    # get names of capitals, corresponding to indices in given solution
    tmp = [capitals[i] for i in solution[0]]
    
    # get pairs of capitals from solution
    pairs = [tmp[i]+tmp[i+1] for i in range(0, len(capitals)-1, 2) ]
    
    # print pairs
    print(' '.join(pairs))
    



def find_city_partition(matrix, cost_limit, current_solution, capitals,
                        optimize = True, hide_solutions = False):
    
    """Recursive function for finding city partitions.
    

    Args:
        matrix (list):
            cost matrix of cities.
        cost_limit (int):
            upper cost limit
        current_solution (list):
            current solution. List containing list of capital indices as first value
            and cost of solution as second value.
        capitals (list):
            List of capitals, in order corresponding to cost matrix.
        optimize (bool, optional):
            If True, adapt the cost limit whenever a solution is found to limit
            the search to just the optimal cost, without having to enumerate all 
            viable solutions. Defaults to True.
        hide_solutions (bool, optional):
            Do not print solutions found in the process if True. Defaults to False.

    Returns:
        cost_limit (int): 
            current cost limit

    """
    # count function calls
    global FUNCTION_CALLS
    FUNCTION_CALLS += 1

    # current_solution[0] -> list of city indices specifying current partition
    # current_solution[1] -> current cost of partition
    
    # if length of current solution is equal to number of cities, check if viable solution
    if len(current_solution[0]) == len(matrix): 

        # check if solution satisfies cost limit
        if current_solution[1] <= cost_limit: 
            
            # print solution
            if not hide_solutions:
                print_solution(current_solution, capitals)
          
            # return the cost of the found solution 
            return current_solution[1]
        
        
    # iterate over all possible pairs to check
    # in order to remove redundancy and guarantee alphabetical sorting, check only 
    # pairs with the first city having a greater index than the first city of the
    # last checked pair (as alphabetical sorting can be assumed)
        
    for i in range(current_solution[0][-2]+1, len(matrix)): 
        for j in range(i+1, len(matrix)): 
            
            # if cities not already in path and not equal, continue search from there
            if i not in current_solution[0] and j not in current_solution[0] and i != j: 
                
                # add the two cities to the current solution and update the cost
                current_solution[0].append(i)
                current_solution[0].append(j)
                current_solution[1] += matrix[i][j]
                
                # if updated cost still satisfies the cost limit, continue search 
                # with updated path
                if current_solution[1] <= cost_limit:
                    
                    result = find_city_partition(matrix, cost_limit, current_solution,
                                                 capitals, optimize, hide_solutions)
                    
                    # if just optimisation and not complete enumeration should be performed
                    # update the cost limit whenever a better solution was found
                    if optimize: 
                        if result < cost_limit: 
                            cost_limit = result
        
                
                # remove processed cities and update cost
                a = current_solution[0].pop()
                b = current_solution[0].pop()
                current_solution[1] -= matrix[a][b]
                

    return cost_limit

def main(args):
    
    # read input file
    cost_limit, capitals, matrix = read_input(args.input.read())
    
    
    if args.o == True:
        hide_solutions = True
    else: 
        hide_solutions = False
        
        
        
    start = time.time()
    
    # start search with all pairs of the first city, as alphabetical sorting
    # of cities can be assumed
    for i in range(1, len(matrix)): 
        starting_pair = [[0, i], matrix[0][i]] # specify starting pair and starting cost
        result = find_city_partition(matrix, cost_limit, starting_pair, capitals,
                                     optimize = args.o, hide_solutions = hide_solutions)
        
        # update cost limit, will change only if optimize == True 
        if args.o: 
            if result < cost_limit: 
                cost_limit = result
    
        
    end = time.time()
    
    
    # print optimal cost, if only optimize
    if args.o: 
        print(cost_limit)
        
        
    # show execution time and number of times that recursion called if wanted
    if args.t: 
        print(f'\nexecution time {round(end-start, 10)} s')
        print(f'{FUNCTION_CALLS} total function calls')
    
    
if __name__ == "__main__": 
    # create Argument parser
    parser = argparse.ArgumentParser(
                    prog='Optimizing the administration of Atirasu',
                    description='Find possible pairs satisfying cost contraint',
                    )

    parser.add_argument('input', nargs='?', 
                        type=argparse.FileType(),
                        default=sys.stdin, 
                        help  = 'specify path to input file or provide file content via stdin.')   

    parser.add_argument('-o', action='store_true',
                        help = "optimize instead of complete enumeration and show optimal cost only.")
    
    parser.add_argument('-t', action='store_true',
                        help = "show execution time.")

   
    # parse arguments
    args = parser.parse_args()
    
    main(args)


    
    