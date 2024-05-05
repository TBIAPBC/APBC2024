import argparse
import sys
import numpy as np
import math




def read_input(input_text, diagonal):
    # Remove comments and strip whitespace characters, keep only non-empty lines
    input_text = [line.split("#")[0].strip() for line in input_text if line.split("#")[0].strip()]

    # Column count can be read from first input line
    n_col = len(input_text[0].split())

    # For row count, iterate through lines until the number of characters doesn't match anymore
    for n_row, line in enumerate(input_text):
        if n_col != len(line.split()):
            n_row += 1
            break

    print("Dimensions")
    print(f" {n_row} {n_col}")
    # Initialise weight matrices with -math.inf, as symmetric matrices for easier handling
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
        # Leave first row at -inf
        from_west[i, 1:] = input_text[i+line_offset].split()

    # Fill diagonal matrix
    if diagonal:
        line_offset = 2*n_row - 1
        for i in range(n_row - 1):
            from_diag[i+1, 1:] = input_text[i+line_offset].split()

    return from_north, from_west, from_diag


def logic_now(from_north, from_west, from_diag, diagonal, trace):
    n_row, n_col = from_north.shape

    # initialise dynamic programming matrix (requires additional row and column for initialisation)
    dp_mat = np.full((n_row + 1, n_col + 1), -math.inf)

    # Store directions during algorithm - leads to higher memory requirements but requires no computation in backtracing
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

            # Store direction corresponding to highest scoring value
            direction_index = np.argmax([from_north_val, from_west_val, from_diag_val])
            backtrace_mat[row_id][col_id] = ["S", "E", "D"][direction_index]
            # debug print
            #if row_id==0 and col_id < 3:
            #    print(f"Step {col_id}")
            #    print(f"update value at {row_id}/{col_id}")
            #    print(f"max of {from_north_val} {from_west_val} {from_diag_val}")
            #    print(dp_mat)

    dp_row = n_row
    dp_col = n_col
    path = ""
    i = 0
    while dp_col > 1 or dp_row > 1:
        row_id = dp_row - 1
        col_id = dp_col - 1
        i += 1

        current_field = dp_mat[dp_row, dp_col]

        print(path)
        print(f"{row_id} {col_id}")


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
        else:
            stop("This isn't working")
        
    print("don2)")
    print(path)        





if __name__ == "__main__":

    # Handle parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="*", default=argparse.SUPPRESS)
    parser.add_argument("-d", "--diagonal", action="store_true")
    parser.add_argument("-t", "--trace", action="store_true")
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

    if args.verbose:
        print("south weights")
        print(from_north)
        print("east weights")
        print(from_west)
        print("diag weights")
        print(from_diag)

    logic_now(from_north, from_west, from_diag, args.diagonal, args.trace)
