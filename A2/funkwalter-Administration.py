#!/usr/bin/env python3
import sys
import argparse
from itertools import combinations


def read_input(source):
    lines = source.read().strip().split('\n')
    header = lines[0].split()
    cost_limit = int(header[1])
    capitals = lines[1].split()
    cost_matrix = []
    for line in lines[2:]:
        row_costs = [0 if x == '-' else int(x) for x in line.split()]
        cost_matrix.append(row_costs)
    return capitals, cost_matrix, cost_limit


def generate_pairs(capitals):
    return list(combinations(capitals, 2))


def find_partitions(capitals, all_pairs, cost_matrix, cost_limit, current_pairs=[], index=0, current_cost=0):
    if len(current_pairs) == len(capitals) // 2:
        if current_cost <= cost_limit:
            return [(current_cost, current_pairs.copy())]
        else:
            return []
    if index >= len(all_pairs):
        return []
    results = []
    next_pair = all_pairs[index]
    cap1, cap2 = next_pair
    pair_cost = cost_matrix[capitals.index(cap1)][capitals.index(cap2)]
    used_capitals = []
    for pair in current_pairs:
        for cap in pair:
            used_capitals.append(cap)
    if cap1 not in used_capitals and cap2 not in used_capitals:
        current_pairs.append(next_pair)
        results.extend(find_partitions(
            capitals, all_pairs, cost_matrix, cost_limit,
            current_pairs, index + 1, current_cost + pair_cost))
        current_pairs.pop()
    results.extend(
        find_partitions(capitals, all_pairs, cost_matrix, cost_limit, current_pairs, index + 1, current_cost))
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-o', '--optimize', action='store_true')
    args = parser.parse_args()

    capitals, cost_matrix, cost_limit = read_input(args.file_path)
    all_pairs = generate_pairs(capitals)
    solutions = find_partitions(capitals, all_pairs, cost_matrix, cost_limit)

    if args.optimize:
        if solutions:
            min_cost = min(solutions, key=lambda x: x[0])[0]
            print(min_cost)
        else:
            print("No solution under the cost limit.")
    else:
        unique_solutions = set()
        for cost, pairs in solutions:
            sorted_solution = []
            for pair in sorted(pairs, key=lambda x: (x[0], x[1])):
                sorted_solution.append(''.join(sorted(pair)))
            sorted_solution = ''.join(sorted_solution)
            unique_solutions.add(sorted_solution)
        for solution in sorted(unique_solutions):
            formatted_solution = ' '.join([solution[i:i + 2] for i in range(0, len(solution), 2)])
            print(formatted_solution)


if __name__ == "__main__":
    main()

