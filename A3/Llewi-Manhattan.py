import argparse
import sys
import numpy as np
import math




def read_input(input_text, diagonal):
    # Remove comments and strip whitespace characters, keep only non-empty lines
    input_text = [line.split("#")[0].strip() for line in input_text if line.split("#")[0].strip()]

    # Determine dimensions
    # For row count, iterate through lines until the number of characters doesn't match anymore
    n_col = len(input_text[0].split())
    for n_row, line in enumerate(input_text):
        if n_col != len(line.split()):
            n_row += 1
            break

    # Initialise weight matrices with -math.inf
    # Invalid paths (e.g. going east in the eastmost cities) will be prohibited by a value of negative infinity, so they will never be chosen
    from_north = np.full((n_row, n_col), -math.inf)
    from_west = from_north.copy()
    from_diag = from_north.copy()

    # Fill south matrix
    for i in range(n_row-1):
        # Leave first line at -inf, real weights start at second line
        from_north[i+1,] = input_text[i].split()
    
    # Fill east matrix
    line_offset = n_row - 1
    for i in range(n_row):
        # Leave first column at -inf
        from_west[i, 1:] = input_text[i+line_offset].split()

    # Fill diagonal matrix
    if diagonal and len(input_text) > 2*n_row - 1:
        line_offset = 2*n_row - 1
        for i in range(n_row - 1):
            from_diag[i+1, 1:] = input_text[i+line_offset].split()

    return from_north, from_west, from_diag


def compute_dynamic_programming_mat(from_north, from_west, from_diag):
    n_row, n_col = from_north.shape

    # initialise dynamic programming matrix (requires additional row and column for initialisation)
    dp_mat = np.full((n_row + 1, n_col + 1), -math.inf)

    # Alternative implementation - store directions during algorithm. Leads to higher memory requirements but requires no computation in backtracing
    backtrace_mat = [["-"] * n_col for _ in range(n_row)]

    # Walk through matrix column by column, row by row and build optimal partial solution.
    for row_id in range(n_row):
        for col_id in range(n_col):

            # Indexing into dp_mat requires offset
            dp_row = row_id + 1
            dp_col = col_id + 1

            # Initialise first field separately
            if row_id == 0 and col_id == 0:
                dp_mat[dp_row, dp_col] = 0
                continue

            # Calculate value for each potential predecessor
            from_north_val = dp_mat[dp_row - 1, dp_col] + from_north[row_id, col_id]
            from_west_val = dp_mat[dp_row, dp_col - 1] + from_west[row_id, col_id]
            #from_diag_val = -math.inf
            #if diagonal:
            from_diag_val = dp_mat[dp_row - 1, dp_col - 1] + from_diag[row_id, col_id]

            # Assign highest scoring value
            dp_mat[dp_row, dp_col] = np.max([from_north_val, from_west_val, from_diag_val])

            # Alternative implementation - store direction corresponding to highest scoring value
            direction_index = np.argmax([from_north_val, from_west_val, from_diag_val])
            backtrace_mat[row_id][col_id] = ["S", "E", "D"][direction_index]

    return dp_mat, backtrace_mat


def backtrace(dp_mat, from_north, from_west, from_diag):
    dp_row, dp_col = from_north.shape
    path = ""
    while dp_col > 1 or dp_row > 1:
        row_id = dp_row - 1
        col_id = dp_col - 1
        current_field = dp_mat[dp_row, dp_col]

        # Is route from north possible?
        if current_field == dp_mat[dp_row - 1, dp_col] + from_north[row_id, col_id]:
            dp_row -= 1
            path = "S" + path
            continue

        # Is route from west possible?
        elif current_field == dp_mat[dp_row, dp_col - 1] + from_west[row_id, col_id]:
            dp_col -= 1
            path = "E" + path
            continue

        # Otherwise it has to be from diagonal
        elif current_field == dp_mat[dp_row - 1, dp_col - 1] + from_diag[row_id, col_id]:
            dp_row -= 1
            dp_col -= 1
            path = "D" + path
            continue
        # If not, that's an error
        else:
            exit("This isn't working")
    
    return path


def backtrace_from_directions_mat(backtrace_mat):
    row_id = len(backtrace_mat) - 1
    col_id = len(backtrace_mat[0]) - 1
    path = ""
    while row_id > 0 or col_id > 0:
        direction = backtrace_mat[row_id][col_id]
        path = direction + path
        if direction == "S":
            row_id -= 1
        elif direction == "E":
            col_id -= 1
        elif direction == "D":
            row_id -= 1
            col_id -= 1
        else:
            exit("This isn't working")
    
    return path


if __name__ == "__main__":

    # Handle parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="*", default=argparse.SUPPRESS)
    parser.add_argument("-d", "--diagonal", action="store_true")
    parser.add_argument("-t", "--trace", action="store_true")
    parser.add_argument("-a", "--alternative_backtrace_implementation", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    #parser.add_argument("-o", "--optimize", action="store_true")
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
    from_north, from_west, from_diag = read_input(input_text, args.diagonal)

    # Run logic
    dp_mat, backtrace_mat = compute_dynamic_programming_mat(from_north, from_west, from_diag)

    # Print weight
    max_weight = dp_mat[-1, -1]
    if max_weight.is_integer():
        print(int(max_weight))
    else:
        print(np.format_float_positional(max_weight, 2))

    # Backtrace if you want
    if args.trace:
        if args.alternative_backtrace_implementation:
            path = backtrace_from_directions_mat(backtrace_mat)
        else:
            path = backtrace(dp_mat, from_north, from_west, from_diag)
        print(path)
