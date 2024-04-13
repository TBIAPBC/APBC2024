
print("Please specify an input file to read:")
file_in = input()
print("Hello World!")
with open(file_in, 'r') as input:
    line = input.read().rstrip('\n')
    print(line)