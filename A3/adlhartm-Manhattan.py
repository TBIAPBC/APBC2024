"""

Manhattan Tourist Problem.

"""

import sys
import argparse
import numpy as np


def read_input(file_content, include_diagonal = True): 
    
    # dictionary to store weight matrix
    weights = {"S":[], "E":[], "D":[]}
    
    # start reading south matrix
    current_direction = "S"
    
    m = None
    n = None

    lines = file_content.split("\n")
    
    
    # read in all matrices
    for line in lines:
        # ignore comment and empty lines
        if not line.startswith("#") and len(line) != 0:
           
            data = [float(x) for x in line.strip().split()]
            
            # get number of columns in grid from south direction
            if n == None: 
                n = len(data)
            
            # if done reading south, switch to east
            if  current_direction =="S" and len(data) != n:
                
                # get number of rows in grid from number of read lines for south direction
                m = len(weights["S"])+1
                
                current_direction = "E"
                expected_lines = m    

            # read east until number of lines match expectation
            if current_direction == "E":
                if expected_lines == 0:
                    
                    if include_diagonal:
                        current_direction = "D"
                    else: 
                        break
                else: 
                    expected_lines -=1
                    
            weights[current_direction].append(data)
     
    
    # sanity check for the expected matrix dimensions for all directions
    for direction in weights: 
       
        if direction == "S": 
            i = len(weights[direction])
            j = len(weights[direction][0])
            assert i == m-1 and j == n
          
        elif direction == "E": 
            i = len(weights[direction])
            j = len(weights[direction][0])
            assert i == m and j == n-1
        
        elif direction == "D": 
            if len(weights[direction]) != 0 : 
                i = len(weights[direction])
                j= len(weights[direction][0])
                assert i == m-1 and j == n-1
               
    grid_dimension = (m, n)    
    
    return weights, grid_dimension


def trace_back(scores, weights):
    
    m, n = scores.shape
    i = m-1
    j = n-1
    
    path = ""
    
    # find path through DP matrix, preferring south direction in case of ties
    while i>0 or j>0: 

        current_score = scores[i,j]
        if i>0:
            S = scores[i-1][j] + weights["S"][i-1][j]
            if S == current_score: 
                path += "S"
                i-=1
                continue
        if j>0:
            E = scores[i][j-1] + weights["E"][i][ j-1]
            if E == current_score: 
                path += "E"
                j-=1
                continue
            
        if i>0 and j>0:
            D = scores[i-1][ j-1] + weights["D"][i-1][j-1]
            if D == current_score: 
                path += "D"
                i-=1
                j-=1
                continue
    
    return path[::-1]
    

def get_DP_matrix(weights, grid_dimension): 
   
    # check if diagonal weights were read in
    include_diagonal = bool(len(weights["D"])>0)

    
    # initalisie zero matrix with correct dimensions
    scores = np.zeros(grid_dimension)


    # fill first column, only south direction allowed
    for i in range(1, grid_dimension[0]):
        S = scores[i-1][ 0]+weights["S"][i-1 ][ 0]
        scores[i,0] = S
        
    # fill first row, only east direction allowed    
    for j in range(1, grid_dimension[1]): 
        E = scores[0][ j-1]+weights["E"][0][ j-1 ]
        scores[0][j] = E
        
    # fill remaining DP-matrix    
    for i in range(1, grid_dimension[0]): 
        for j in range(1, grid_dimension[1]): 
            
                values = []
               
                E = scores[i][ j-1]+weights["E"][i][ j-1 ]
                values.append(E)

                S = scores[i-1][j]+weights["S"][i-1][j]
                values.append(S)

                if include_diagonal: 
                    D = scores[i-1][j-1] + weights["D"][i-1][ j-1]
                    values.append(D)
                
                max_val = max(values)
                scores[i,j] = max_val
        
   
    return scores



def main(args): 
   
    # read input
    weights, grid_dimension = read_input(args.input.read(), args.d)
    
    # get DP-matrix
    scores = get_DP_matrix(weights, grid_dimension)

    # get max score and print results
    max_score = scores[-1][-1]
    if max_score.is_integer(): 
        print("{:.0f}".format(max_score))
    else: 
        print("{:.2f}".format(max_score))
        
    # trace back path
    if args.t: 
        path = trace_back(scores, weights)
        print(path)
   
    
if __name__ == "__main__": 
    
    #create Argument parser
    parser = argparse.ArgumentParser(
                    prog='Manhattan Tourist Problem',
                    )

    parser.add_argument('input', nargs='?', 
                        type=argparse.FileType(),
                        default=sys.stdin, 
                        help  = "specify path to input file or provide file content via stdin")   

    parser.add_argument('-d', action='store_true',
                        help = "include diagonal edge weights")

    parser.add_argument('-t', action='store_true',
                        help = "trace path")


    # parse arguments
    args = parser.parse_args()

    main(args)
   




