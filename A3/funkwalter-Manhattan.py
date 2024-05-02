#!/usr/bin/env python3
import sys
import argparse

def read_and_parse_input(use_diagonal):
    lines = [line.strip() for line in sys.stdin if line.strip() and not line.startswith('#')]

    data = []
    for line in lines:
        split_line = line.split()
        float_line = list(map(float, split_line))
        data.append(float_line)

    matrices = []
    current_matrix = []
    previous_length = len(data[0])
    rows_collected = 0
    rows_first_matrix = 0

    for row in data:
        if len(row) != previous_length:
            if not matrices:  
                rows_first_matrix = rows_collected  
            matrices.append(current_matrix)
            current_matrix = []
            rows_collected = 0
            previous_length = len(row)

        if len(matrices) == 1 and rows_collected == rows_first_matrix + 1:
            if use_diagonal:
                if len(matrices) == 2:  
                    matrices.append(current_matrix)
                    current_matrix = []
                elif len(matrices) == 1:
                    matrices.append(current_matrix)
                    current_matrix = []
            else:
                matrices.append(current_matrix)
                current_matrix = []

        current_matrix.append(row)
        rows_collected += 1

    if current_matrix:
        matrices.append(current_matrix)

    north_south = matrices[0] if len(matrices) > 0 else []
    west_east = matrices[1] if len(matrices) > 1 else []
    diagonals = matrices[2] if use_diagonal and len(matrices) > 2 else []

    n = len(north_south)
    m = len(west_east[0]) if west_east else 0

    return n, m, north_south, west_east, diagonals

def find_maximum_weight_path(n, m, north_south, west_east, diagonals, track_path=False):
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    predecessor = [[None] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + north_south[i - 1][0]
        predecessor[i][0] = (i - 1, 0)

    for j in range(1, m + 1):
        dp[0][j] = dp[0][j - 1] + west_east[0][j - 1]
        predecessor[0][j] = (0, j - 1)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            options = {
                (i - 1, j): dp[i - 1][j] + north_south[i - 1][j] if j < len(north_south[i - 1]) else dp[i - 1][j],
                (i, j - 1): dp[i][j - 1] + west_east[i][j - 1] if j - 1 < len(west_east[i]) else dp[i][j - 1]
            }

            if diagonals and i - 1 < len(diagonals) and j - 1 < len(diagonals[i - 1]):
                options[(i - 1, j - 1)] = dp[i - 1][j - 1] + diagonals[i - 1][j - 1]

            predecessor[i][j], dp[i][j] = max(options.items(), key=lambda x: x[1])

    if track_path:
        path = []
        i, j = n, m
        while (i, j) != (0, 0):
            prev_i, prev_j = predecessor[i][j]
            if (prev_i, prev_j) == (i - 1, j):
                path.append('S')
            elif (prev_i, prev_j) == (i, j - 1):
                path.append('E')
            elif (prev_i, prev_j) == (i - 1, j - 1):
                path.append('D')
            i, j = prev_i, prev_j

        path.reverse()
        return dp[n][m], ''.join(path)

    return dp[n][m]

def format_weight(weight):
    if weight == int(weight):
        return f"{int(weight)}"
    else:
        return f"{weight:.2f}"

def main():
    parser = argparse.ArgumentParser(description="Find the maximum weight path in a Manhattan-like grid.")
    parser.add_argument('infile', type=argparse.FileType('r'), nargs='?', default=sys.stdin, help='Input file containing the grid data')
    parser.add_argument('-d', '--diagonal', action='store_true', help='Include diagonals')
    parser.add_argument('-t', '--track', action='store_true', help='Track and print the path taken')

    args = parser.parse_args()
    sys.stdin = args.infile

    n, m, north_south, west_east, diagonals = read_and_parse_input(args.diagonal)
    diagonals = diagonals if args.diagonal else []

    if args.track:
        max_weight, path_string = find_maximum_weight_path(n, m, north_south, west_east, diagonals, track_path=True)
        formatted_weight = format_weight(max_weight)
        print(formatted_weight)
        print(path_string)
    else:
        max_weight = find_maximum_weight_path(n, m, north_south, west_east, diagonals)
        formatted_weight = format_weight(max_weight)
        print(formatted_weight)

if __name__ == "__main__":
    main()

