
import sys 

def hello_world(filename):
    try: 
        print("Hello World!")

        with open(filename, 'r') as file:
            print(file.read(), end='')
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")

if __name__ == "__main__":
    filename = input("Enter the filename: ")
    
    
    hello_world(filename)

