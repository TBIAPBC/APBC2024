import sys

with open(sys.argv[1], 'r') as file:
    print("Hello World!")
    print(file.read().strip(), end='')
