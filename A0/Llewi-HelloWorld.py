input = open("HelloWorld-test1.in", "r")
lines = input.readlines()
input.close()

output = open("HelloWorld-test1.out", "w")
output.write("Hello World!\n")
for line in lines:
    output.write(line)

output.close()
