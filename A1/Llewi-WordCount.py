import sys
import re

# Tested with commands...
# python Llewi-WordCount.py WordCount-test1.in
# python Llewi-WordCount.py -l WordCount-test2.in
# python Llewi-WordCount.py -l WordCount-test3.in -I

def main(input_text: str, ignore_case, print_list):
    
    if ignore_case:
        input_text = input_text.lower()

    # Replace special characters with space
    non_word_chars = find_non_word_chars(input_text)
    for char in non_word_chars:
        input_text = input_text.replace(char, " ")
    
    # Create count dict
    word_dict = {}
    words = input_text.split() # splits words separated by one or multiple whitespace characters
    for word in words:
        if word in word_dict:
            word_dict[word] += 1
        else:
            word_dict[word] = 1
    
    # Output
    if not print_list:
        print(f"{len(word_dict)} / {sum(word_dict.values())}")
        return

    # print list - sort by (reversed) count first, then alphabetically
    sorted_list = sorted(word_dict.items(), key=lambda item: (-item[1], item[0]))
    for item in sorted_list:
        print(f"{item[0]}\t{item[1]}")


def find_non_word_chars(input_text: str):
    input_text = input_text.replace("\n", " ")
    pattern = re.compile(r'[^a-zA-ZäöüÄÖÜß]')
    non_word_chars = set(pattern.findall(input_text))
    #non_word_chars.remove('\\')
    return non_word_chars


if __name__ == "__main__":

    user_args = sys.argv[1:] if len(sys.argv) else []

    ignore_case = "-I" in user_args
    print_list = "-l" in user_args
    
    # Try to read from standard input
    if not sys.stdin.isatty():
        input_text = sys.stdin.read()
        #print("From STDIN")
    else:
        # Alternatively read from file
        remainder = [t for t in user_args if t != "-I" and t != "-l"]
        if len(remainder) < 1:
            raise("Neither input file nor standard input provided; stopping program")
        file_name = remainder[0]
        input_text = open(file_name, "r", encoding="UTF-8").read()
        #print("From FILE")
    
    main(input_text, ignore_case, print_list)
