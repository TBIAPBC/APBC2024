input = open("HelloWorld-test1.in", "r")
lines = input.read().splitlines()
input.close()

output = open("HelloWorld-test1.out", "w")
output.write("Hello World!\n")
for i, line in enumerate(lines):
    output.write(line)
    if i < len(output) - 1:
        output.write("\n")

output.close()
