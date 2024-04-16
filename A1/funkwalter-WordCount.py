#!/usr/bin/env python3
import sys
import re
from collections import Counter


def process_text(text, ignore_case):
    if ignore_case:
        text = text.lower()
    return re.findall(r'\b[a-zA-Z0-9äöüÄÖÜß]+\b', text)


def main():
    ignore_case = '-I' in sys.argv
    list_words = '-l' in sys.argv
    if ignore_case:
        sys.argv.remove('-I')
    if list_words:
        sys.argv.remove('-l')

    if len(sys.argv) == 1:
        input_text = sys.stdin.read()
    else:
        with open(sys.argv[1], 'r') as file:
            input_text = file.read()

    words = process_text(input_text, ignore_case)
    word_count = Counter(words)

    if list_words:
        for word, count in sorted(word_count.items(), key=lambda item: (-item[1], item[0])):
            print(f"{word}\t{count}")
    else:
        total_words = sum(word_count.values())
        unique_words = len(word_count)
        print(f"{unique_words} / {total_words}")


if __name__ == "__main__":
    main()

