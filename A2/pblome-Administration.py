import sys
import math
import itertools


def bab(no_cities, bound, cities, dist, optimise):

    solutions = []
    
    cost = {}
    for i in range(len(cities)):
        for j in range(i+1, len(cities)):
            cost[cities[i]+cities[j]] = dist[i][j]
    # this works to produce a dictionary with the costs for all tuples (only considering the upper triangle matrix
    # and thus avoiding duplicates) (if input is in lexicographical order, this is also)
    
    stack = []
    for i in range(1,len(cities)):
        stack.append(tuple([cities[0]+cities[i]]))
    # append all interior nodes at depth 1 to the stack (here: all pairs including the alphabetically first city)
    
    if optimise:
        opt_value = bound+1
        while stack:
            sol = stack.pop()
            cost[sol] = 0
            visited_cities = [char for pair in sol for char in pair]
            unvisited_cities = [city for city in cities if city not in visited_cities]

            for partition in sol:
                cost[sol] += cost[partition]
            
            if cost[sol] < opt_value:
                if len(sol) == no_cities /2:
                    #opt_sol = sol # If you want to print the optimal partition as well and not just the value, you can uncomment this 
                    opt_value = cost[sol] # if we want to optimise, the bound is always updated if a lower value was found
                else:
                    # append all child nodes to the stack
                    pairs = [''.join(pair) for pair in itertools.combinations(unvisited_cities, 2)]
                    for pair in pairs:
                        stack.append((*sol, pair))
            else:
                continue
        return opt_value#, opt_sol
        
    else:
        while stack:
            sol = stack.pop()
            cost[sol] = 0
            visited_cities = [char for pair in sol for char in pair]
            unvisited_cities = [city for city in cities if city not in visited_cities]

            for partition in sol:
                cost[sol] += cost[partition]
            
            if cost[sol] <= bound:
                if len(sol) == no_cities /2:
                    solutions.append(sol)
                else:
                    # append all child nodes to the stack
                    pairs = [''.join(pair) for pair in itertools.combinations(unvisited_cities, 2)]
                    for pair in pairs:
                        stack.append((*sol, pair))
            else:
                continue
                # not a valid path
        unique_sols = list(set([tuple(sorted(sol)) for sol in solutions]))
        sorted_sols = sorted(unique_sols)
        return sorted_sols


def read_matrix(file):
    header = file[0].split()
    no_cities = int(header[0])

    if (no_cities % 2) == 1 : # checks if number of cities is even 
        print("The number of cities is not even. Thus we cannot find a valid partition into tuples.")
        sys.exit()
    bound = int(header[1])
    
    cities = file[1].split()
    
    A = file[2:]
    D = []
    for row in A:
        line = row.split()
        line = [entry for entry in line if entry]
        D.append(line)
    for i in range(no_cities):
        for j in range(no_cities):
            if D[i][j] == "-":
                D[i][j] = math.inf 
            elif D[i][j]:
                D[i][j] = int(D[i][j])
    return no_cities, bound, cities, D


if __name__ == "__main__":
    
    input = sys.stdin.read().splitlines()
    no_cities, bound, cities, dist = read_matrix(input)   
    
    optimise = False

    if "-o" in sys.argv:
        optimise = True
        
    result = bab(no_cities, bound, cities, dist, optimise)
    
    if optimise:
        if result == bound+1:
            print("No feasible solution was found.")
        else:
            print(result)
    else:
        if result:
            for partition in result:
                print(' '.join(partition))
        else:
            print("No feasible solution was found.")
