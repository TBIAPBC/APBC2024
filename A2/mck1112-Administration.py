import sys
import argparse
import pandas as pd

# read in the cost matrix from the file
def read_file(input_file):
    with open(input_file) as f:
        info = f.readline().strip().split()
        header = f.readline().strip().split()
        lines = [line.strip().split() for line in f.readlines()]

        matrix = []
        for line in lines:
            row = []
            for num in line:
                try:
                    row.append(int(num))
                except ValueError:
                    row.append(0)
            matrix.append(row)

    return info, header, matrix

# calculate score of a path
def calculate_score(path, dist_df):
    score = 0
    for pair in path:
        score += dist_df.loc[pair[0], pair[1]]
    return score

# check if a path is complete
def complete_path(path, num_cities):
    if len(path) == num_cities // 2:
        return True
    return False

# check if a city is in a path
def city_in_path(city, path):
    for pair in path:
        for c in pair:
            if city == c:
                return True
    return False

# recursive Branch and Bound algorithm
def branch_and_bound(dist_df, num_cities, paths_list, explored_paths, remaining_cities):

    path = paths_list[-1]

    global upper_bound

    if calculate_score(path, dist_df) > upper_bound:
        paths_list.remove(path)
        if not paths_list:
            paths_list.append([])
        return

    if complete_path(path, num_cities):
        if args.o:
            upper_bound = calculate_score(path, dist_df)
        return

    paths_list.remove(path)

    for city in remaining_cities:
        if not city_in_path(city, path):
            for city2 in remaining_cities:
                if city2 != city and not city_in_path(city2, path):
                    new_path = path.copy()
                    new_path.append([city, city2])
                    new_path_set = frozenset(map(frozenset, new_path))

                    if new_path_set not in explored_paths:
                        explored_paths.add(new_path_set)
                        remaining_cities_copy = remaining_cities.copy()
                        remaining_cities_copy.remove(city2)
                        remaining_cities_copy.remove(city)
                        paths_list.append(new_path)
                        branch_and_bound(dist_df, num_cities, paths_list, explored_paths, remaining_cities_copy)

    return paths_list


parser = argparse.ArgumentParser(description='Administration optimization')
parser.add_argument('input_file', help='Name of the input file')
parser.add_argument('-o', action='store_true', help='Return best score')
args = parser.parse_args()

if __name__ == "__main__":
    info, header, matrix = read_file(args.input_file)

    if int(info[0]) % 2 == 1:
        print("Incapable of forming pairs, number of cities is not even")
        sys.exit()

    global upper_bound
    upper_bound = int(info[1])

    distances_df = pd.DataFrame(matrix, columns=header, index=header)
    cities = header

    paths = branch_and_bound(distances_df, int(info[0]), [[]], set(), cities)

    try:
        paths.remove([])
    except:
        pass

    if args.o:
        print(upper_bound)
    else:
        for path in paths:
            for p in path:
                print(*p, sep="", end=" ")
            print("")
