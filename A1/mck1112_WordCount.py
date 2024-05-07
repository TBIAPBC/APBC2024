import sys
import re
from collections import Counter

def word_count(file_name):
    try:
        with open(file_name, 'r') as file:
            text = file.read()
            # Extract words from the text using regular expression; handling German language as well
            words = re.findall(r'\b[a-zA-z0-9äöüÄÖÜß]+\b', text)
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            return word_counts, words
    except FileNotFoundError:
        print("File not found.")
        sys.exit(1)

def word_list(words, ignore_case=False):
    if ignore_case:
        words = [word.lower() for word in words]
    counts = Counter(words)
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

    for word, count in sorted_counts:
        print(f"{word}\t{count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python word_counter.py [-I] [-l] <file_name>")
        sys.exit(1)
    
    file_name = sys.argv[-1]
    ignore_case = "-I" in sys.argv[1:]
    print_list_case = "-l" in sys.argv[1:]

    word_counts, words = word_count(file_name)

    if ignore_case and print_list_case:
        total_words = len(words)
        unique_words = len(set(words))
        print("Total words:", total_words)
        print("Different words:", unique_words)
        word_list(words, ignore_case=True)
    else:
        if ignore_case:
            total_words = len(words)
            unique_words = len(set(words))
            print("Total words:", total_words)
            print("Different words:", unique_words)
        if print_list_case:
            word_list(words)