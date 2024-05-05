import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input file')
    parser.add_argument('-d', action='store_true', help='accept diagonal inputs')
    parser.add_argument('-t', action='store_true', help='print optimal path')
    return parser.parse_args()


def read_file(filename):
    with open(filename) as f:
        matrix = []
        for line in f:
            if line[0] != "#":
                row = [float(num) for num in line.split()]
                if row:
                    matrix.append(row)
    return matrix

# extracting weights: vertical, horizontal, and diagonal
def get_weights(matrix, diagonal):
    v_weights, h_weights, d_weights = [], [], []
    height = 0
    for row in matrix:
        # collect vertical weights
        # continues until a row of different length (the end of the vertical weights)
        # height keeps track of how many rows have been added 
        if len(row) == len(matrix[0]):
            v_weights.append(row)
            height += 1
        else:
            break
    # collect horizontal and diagonal weights
    # there must be one more row of the hWeights than of the vWeights
    for i in range(height, 2 * height + 1):
        h_weights.append(matrix[i])

    for i in range(2 * height + 1, len(matrix)):
        d_weights.append(matrix[i])

    return v_weights, h_weights, d_weights if diagonal else None # if diagonal movements are not allowed


def calculate_cost_matrix(v_weights, h_weights, d_weights):
    cost_matrix = [[0] * len(v_weights[0]) for _ in range(len(h_weights))]
    for i, row in enumerate(cost_matrix):
        for j in range(len(row)):
            if i == 0:
                if j != 0:
                    cost_matrix[i][j] = round(row[j - 1] + h_weights[0][j - 1], 2)
            elif j == 0:
                cost_matrix[i][j] = round(cost_matrix[i - 1][0] + v_weights[i - 1][0], 2)
            else:
                tmp_up = cost_matrix[i - 1][j] + v_weights[i - 1][j]
                tmp_left = cost_matrix[i][j - 1] + h_weights[i][j - 1]
                tmp_diag = 0
                if d_weights:
                    tmp_diag = cost_matrix[i - 1][j - 1] + d_weights[i - 1][j - 1]
                cost_matrix[i][j] = round(max(tmp_up, tmp_left, tmp_diag), 2)
    return cost_matrix


def print_solution(cost_matrix, diagonal, args, v_weights, d_weights):
    print("{:.2f}".format(cost_matrix[-1][-1]))

    if args.t:
        i, j = len(cost_matrix) - 1, len(cost_matrix[0]) - 1
        path = ''
        while i > 0 or j > 0:
            if i > 0 and j > 0:
                if diagonal and cost_matrix[i - 1][j - 1] + d_weights[i - 1][j - 1] == cost_matrix[i][j]:
                    path = 'D' + path
                    i -= 1
                    j -= 1
                if cost_matrix[i - 1][j] + v_weights[i - 1][j] == cost_matrix[i][j]:
                    path = 'S' + path
                    i -= 1
                else:
                    path = 'E' + path
                    j -= 1
            elif i == 0:
                path = 'E' + path
                j -= 1
            else:
                path = 'S' + path
                i -= 1
        print(path)


def main():
    args = parse_arguments()
    matrix = read_file(args.input)
    v_weights, h_weights, d_weights = get_weights(matrix, args.d)
    cost_matrix = calculate_cost_matrix(v_weights, h_weights, d_weights)
    print_solution(cost_matrix, args.d, args, v_weights, d_weights)

if __name__ == "__main__":
    main()


