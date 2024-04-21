import sys
import re
from collections import Counter


def wordcount(text, ignorecase):
    
    chars = r"[ \".,?!%^()\-_+\s;:\[\]']+"

    words = re.split(chars, text)
    words = [word for word in words if word]
    if ignorecase==True:
        words_I = [word.lower() for word in words]
        wordcounts = Counter(words_I)
    else:
        wordcounts = Counter(words)
    
    sorted_words = sorted(wordcounts.items(), key= lambda x: (-x[1],x[0]))
    sorted_dict = dict(sorted_words)
    num_words = 0
    for word in list(wordcounts.keys()):
        num_words += wordcounts[word]
    unique_words = len(wordcounts)
    return num_words, unique_words, sorted_dict


if __name__ == "__main__":
    
    input = sys.stdin.read()

    ignorecase = False
    includelist = False

    if "-I" in sys.argv:
        ignorecase = True
    if "-l" in sys.argv:
        includelist = True
        
    result = wordcount(input, ignorecase)

    if includelist == True:
        for line in list(result[2].keys()):
            print(f"{line}\t{result[2][line]}")
    else:
        print(f"{result[1]} / {result[0]}")
