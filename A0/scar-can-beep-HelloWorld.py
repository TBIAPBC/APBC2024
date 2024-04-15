output = open('HelloWorld-test1.out', 'w')
output.write('Hello World!\n')
with open('HelloWorld-test1.in', 'r') as hello_input:
    output.write(hello_input.readline())