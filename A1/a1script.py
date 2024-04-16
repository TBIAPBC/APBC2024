import sys

# to be called with cat <inputfilename> | py a1script.py

user_args = sys.argv[1:] if len(sys.argv) else []

if "-I" in user_args:
    print("i")

if "-l" in user_args:
    print("l")

remainder = [t for t in user_args if t != "-I" and t != "-l"]

print(remainder)
if not sys.stdin.isatty():
    input_text = sys.stdin.read()
else:
    
    file_name = sys.argv[1]
    input_text = open(file_name, "r", encoding="UTF-8").read()

# py a1script.py 



#print(input_text)


#print(sys.stdin.read())
#file_name = sys.argv[1]
#print(len(sys.argv))
#print(sys.argv[0])
