import sys
filename = sys.argv[1]
print("Hello World!")
with open(filename, 'r') as file:
    print(file.read(), end='')
