import sys
import re
from collections import Counter

def word_count(text):
    words = re.findall(r'\b[a-zA-Z0-9äöüÄÖÜß]+\b', text)
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    return word_counts, words

def word_list(words, ignore_case=False):
    if ignore_case:
        words = [word.lower() for word in words]
    counts = Counter(words)
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

    for word, count in sorted_counts:
        print(f"{word}\t{count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        if not sys.stdin.isatty():
            text = sys.stdin.read()
            word_counts, words = word_count(text)
            total_words = len(words)
            unique_words = len(set(words))
            print(f"{unique_words} / {total_words}")
            sys.exit(0)
        else:
            print("Usage: python word_counter.py [-I] [-l] <file_name>")
            sys.exit(1)

    file_name = sys.argv[-1]
    ignore_case = "-I" in sys.argv[1:]
    print_list_case = "-l" in sys.argv[1:]

    try:
        with open(file_name, 'r') as file:
            text = file.read()
    except FileNotFoundError:
        print("File not found.")
        sys.exit(1)

    word_counts, words = word_count(text)

    if ignore_case and print_list_case:
        total_words = len(words)
        unique_words = len(set(words))
        print(f"{unique_words} / {total_words}")
        word_list(words, ignore_case=True)
    else:
        if ignore_case:
            total_words = len(words)
            unique_words = len(set(words))
            print(f"{unique_words} / {total_words}")
        if print_list_case:
            word_list(words)
        if not ignore_case and not print_list_case:
            total_words = len(words)
            unique_words = len(set(words))
            print(f"{unique_words} / {total_words}")
