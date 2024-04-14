file_name = input("Enter input file name:")

print("Hello World!")
with open(file_name, "r") as file:
	for line in file:
		print(line.rstrip())
