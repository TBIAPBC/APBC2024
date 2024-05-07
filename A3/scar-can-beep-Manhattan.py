#IMPORT
import argparse

#FUNCTIONS
def call_parser():
    '''
    Parses the argument for use in the Terminal.

    Returns:
    - filename: string of input file path
    - optimise: boolean; should the program optimise?
    '''
    parser = argparse.ArgumentParser('Solve Manhattan Tourist Problem')
    parser.add_argument('file', help='The input file')
    parser.add_argument('-t', '--traceback', action='store_true', help='Program prints traceback of best solution')
    parser.add_argument('-d', '--diagonal', action='store_true', help='Program takes diagonal paths into account')

    args = parser.parse_args()
    return args.file, args.traceback, args.diagonal

def get_grid(file_name):
    '''
    Generates a Manhattan grid dictionary from the input file.

    Args:
    - file_name(string): Path to the input file

    Returns:
    - grid(dictionary): Number of attractions(floats) ordered by direction and row
    '''
    grid = {'north-south': [], 'west-east': [], 'diagonal': []}
    list_index = -1
    with open(file_name,'r') as f:
        no_comments = False
        line_counter = 0
        count = -1
        for line in f:
            count+=1
            if '#' in line or line == '\n':
                newlist=True
                continue
            else:
                if count == 0:
                    no_comments = True
                    newlist=True
                    line_counter = len(line.split())
                elif no_comments:
                    if len(line.split()) != line_counter:
                        newlist=True
                        line_counter = len(line.split())
                if newlist:
                    list_index+=1
                    newlist=False
                grid[list(grid.keys())[list_index]].append(list(float(x) for x in line.strip().split()))
    return grid

def get_max(row, col, grid, matrix,check_diagonal):
    '''
    Returns the best way (max sights)
    '''
    if row == 0:
        if col == 0:
            return 0
        return matrix[row][col-1] + grid['west-east'][row][col-1]
    elif col == 0:
        return matrix[row-1][col] + grid['north-south'][row-1][col]
    else:
        east_south = matrix[row-1][col] + grid['north-south'][row-1][col]
        south_east = matrix[row][col-1] + grid['west-east'][row][col-1]
        if check_diagonal:
            diagonal = matrix[row-1][col-1] + grid['diagonal'][row-1][col-1]
            return max(east_south,south_east,diagonal)
        else:
            return max(east_south,south_east)

def trace_back(row, col, grid, matrix, diagonal=False, track=''):
    sights = matrix[row][col]
    if row == 0:
        if col == 0:
            return track
        else:
            return trace_back(row, col - 1, grid, matrix, diagonal, 'E' + track)
    elif col == 0:
        return trace_back(row - 1, col, grid, matrix, diagonal, 'S' + track)

    east_south = matrix[row - 1][col] + grid['north-south'][row - 1][col]
    south_east = matrix[row][col - 1] + grid['west-east'][row][col - 1]
    if diagonal:
        diagonal_val = matrix[row - 1][col - 1] + grid['diagonal'][row - 1][col - 1]
        if sights == diagonal_val:
            return trace_back(row - 1, col - 1, grid, matrix, diagonal, 'D' + track)

    if sights == east_south:
        return trace_back(row - 1, col, grid, matrix, diagonal, 'S' + track)
    elif sights == south_east:
        return trace_back(row, col - 1, grid, matrix, diagonal, 'E' + track)
    

#MAIN
file_name, traceback, check_diagonal = call_parser()

grid = get_grid(file_name)

matrix = []
n_row = len(grid['north-south'])
n_col = len(grid['west-east'][0])

for row in range(n_row+1):
    matrix.append([])
    for col in range(n_col+1):
        matrix[row].append(get_max(row,col,grid,matrix,check_diagonal))

#OUTPUT
print(int(matrix[-1][-1]))
if traceback:
    track = trace_back(n_row,n_col,grid,matrix,check_diagonal)
    print(track)