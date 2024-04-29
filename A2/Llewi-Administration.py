import argparse
import sys
import numpy as np
import math

# Tested with commands...
# python Llewi-Administration.py Administration-test1.in
# python Llewi-Administration.py < Administration-test1.in
# cat Administration-test1.in | python Llewi-Administration.py

def read_input(input_text):
    parts = input_text[0].split()
    num_authorities = int(parts[0])
    cost_limit = int(parts[1])
    city_names = input_text[1].split()

    cost_mat = np.zeros((num_authorities, num_authorities))
    for i, line in enumerate(input_text[2:]):
        vals = line.split()
        for j in range(len(vals)):
            if i >= j:
                cost_mat[i, j] = math.inf
            else:
                cost_mat[i, j] = int(vals[j])

    return city_names, cost_mat, cost_limit


def bnb(remaining_cities, current_path, current_cost, upper_bound, optimize):

    # Bound - Check cost
    if current_cost > upper_bound:
        return {}
    
    # Check finish
    if len(current_path) * 2 >= cost_mat.shape[0]:
        # Map citiy indices to names, sort list of named tuples lexicographically
        proper_solution = sorted([city_names[tup[0]]+city_names[tup[1]] for tup in current_path])
        
        # Store in dictionary as concatenated string
        return {" ".join(proper_solution): current_cost}
    
    # Partition into branches for arbitrary unvisited city
    next_branch_city = remaining_cities[0]
    next_pairs = [(next_branch_city, city) for city in remaining_cities if city != next_branch_city]

    # Branch - cover all cases for next_branch_city
    all_solutions = {}
    for next_pair in next_pairs:
        next_remaining_cities = [city for city in remaining_cities if city not in next_pair]
        next_path = [*current_path, next_pair]
        next_cost = current_cost + cost_mat[next_pair[0], next_pair[1]]

        solutions = bnb(next_remaining_cities, next_path, next_cost, upper_bound, optimize)
        all_solutions.update(solutions)

        # Update upper bound
        if optimize and solutions:
            upper_bound = min(upper_bound, min(solutions.values()))

    return all_solutions


if __name__ == "__main__":
    
    # Handle parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="*", default=argparse.SUPPRESS)
    parser.add_argument("-o", "--optimize", action="store_true")
    args = parser.parse_args()

    # Read file
    if not sys.stdin.isatty():
        # Read from standard input
        input_text = sys.stdin.readlines()
    else:
        # Alternatively read from file
        try:
            file_name = args.filename[0]
        except:
            exit("Please provide filename")
        input_text = open(file_name, "r", encoding="UTF-8").readlines()

    # Parse file
    city_names, cost_mat, cost_limit = read_input(input_text)

    # Run algorithm
    n = cost_mat.shape[0]
    all_cities = [i for i in range(n)]

    # Here comes the logic
    result = bnb(all_cities, [], 0, upper_bound=cost_limit, optimize=args.optimize)

    if args.optimize:
        print(int(min(result.values())))
    else:
        print("\n".join(sorted(result.keys())))
