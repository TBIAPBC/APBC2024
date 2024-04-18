import argparse

#PARSER
parser = argparse.ArgumentParser()
parser.add_argument('file', help='Insert input file path here')
args = parser.parse_args()
file_location = args.file

#MAIN
print('Hello World!')
with open(file_location, 'r') as hello_input:
    print(hello_input.readline(),end='')