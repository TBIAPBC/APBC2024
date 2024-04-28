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
    print(num_authorities)
    print(cost_limit)

    authority_names = input_text[1].split()
    print(authority_names)

    cost_mat = np.zeros((num_authorities, num_authorities))
    for i, line in enumerate(input_text[2:]):
        vals = line.split()
        for j in range(len(vals)):
            if i >= j:
                cost_mat[i, j] = math.inf
            else:
                cost_mat[i, j] = int(vals[j])
    #print(cost_mat)
    #print(np.argmin(cost_mat, keepdims=True))
    return cost_mat, cost_limit

def main(input_text, optimize):
    cost_mat, cost_limit = read_input(input_text)
    solset = set()
    sol = rec(cost_mat, (), 0, cost_limit, solset)
    print("DONE")
    print(solset)

def rec(cost_mat, current_pairs, cost, cost_limit, solutions):
    #if cost > cost_limit:
    #    return
    if len(current_pairs)*2 >= cost_mat.shape[0]:
        solutions.add(current_pairs)
        return
    
    reduced_mat = cost_mat.copy()
    print(current_pairs)
    for pair in current_pairs:
        reduced_mat[pair[0], :] = math.inf
        reduced_mat[:, pair[0]] = math.inf
        reduced_mat[pair[1], :] = math.inf
        reduced_mat[:, pair[1]] = math.inf

    print(reduced_mat)
    sorted_indices = np.argsort(reduced_mat, axis=None)
    
    i, j = np.unravel_index(sorted_indices[0], reduced_mat.shape)
    if not math.isfinite(cost_mat[i, j]):
        exit("Infinite cost, shouldn't happen")

    # Create new tuple for preliminary solution
    # Sort so that solutions stay unique
    new_pair = tuple(sorted((i, j))) #(min(i, j), max(i, j))
    new_pairs = tuple(sorted((*current_pairs, new_pair)))

    # Continue recursion
    rec(cost_mat, new_pairs, cost+cost_mat[i, j], cost_limit, solutions)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="*", default=argparse.SUPPRESS)
    parser.add_argument("-o", "--optimize", action="store_true")
    args = parser.parse_args()

    # Try to read from standard input
    if not sys.stdin.isatty():
        input_text = sys.stdin.readlines()
    else:
        # Alternatively read from file
        try:
            file_name = args.filename[0]
        except:
            exit("Please provide filename")
        input_text = open(file_name, "r", encoding="UTF-8").readlines()

    #main(input_text, args.optimize)

    cost_mat, cost_limit = read_input(input_text)



def bnb(current_path, current_cost, remaining_candidates):
    print(f"New iteration {current_path} ({current_cost})")
    # Check cost
    if current_cost > cost_limit:
        print("Too expensive")
        return
    
    # Is finished?
    if len(current_path) * 2 >= n:
        print("finished")
        print(current_path)
        return
    
    
    # Remove impossible candidates
    used_indices = [index for tup in current_path for index in tup]     # Typical python line to flatten nested list
    remaining_candidates = [candidate for candidate in remaining_candidates if candidate[0] not in used_indices and candidate[1] not in used_indices]

    for new_candidate in remaining_candidates:
        new_path = (*current_path, new_candidate)
        new_remaining_candidates = [c for c in remaining_candidates if c != new_candidate]
        new_cost = current_cost + cost_mat[new_candidate[0], new_candidate[1]]
        #print(new_path)
        #print(new_remaining_candidates)
        #print(new_cost)

        bnb(new_path, new_cost, new_remaining_candidates)

    #new_pair = tuple(sorted((i, j))) #(min(i, j), max(i, j))
    #new_pairs = tuple(sorted((*current_pairs, new_pair)))

    # Trim remaining_solutions to be valid
    stop=1

n = cost_mat.shape[0]
all_solutions = ()
for i in range(n):
    for j in range(i+1, n):
        all_solutions = (*all_solutions, (i,j))
print(all_solutions)
print("START")
bnb((), 0, all_solutions)
