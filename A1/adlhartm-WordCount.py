"""
script for counting words in a file. 

"""

import argparse
import sys
import re

    
def count_words(word_list):
    """ Takes list of words and counts their frequency. 
    
    Args:
        word_list (list):
            list of words to count

    Returns:
        word_count_pairs (list): 
            list of tuples, with first value in tuple corresponding to 
            the word and second value in tuple to the corresponding count.
            Tuples are sorted descending by count and ascending 
            alphabetically in case of ties.

    """
    # count the number of occurences of each word
    word_count = {}
    
    for word in word_list: 
        if word not in word_count: 
            word_count[word] = 0
        word_count[word] +=1
    
    
    # get tuples of words with count
    word_count_pairs = list(word_count.items())
    
    # sort pairs descending by counts and ascending alphabetically
    sorted_word_count_pairs = sorted(word_count_pairs, key=lambda x:(-x[1],x[0]))
    
    return sorted_word_count_pairs


def main(file_content, ignorecase = False, list_results = False):

    
    # find all words (alphanumerical) in file using regular expresion
    words = re.findall("\w+", file_content)
    
    # convert all words to lowercase, if case should be ignored
    if ignorecase: 
        words = [word.lower() for word in words]
    
    # if word list should not be provided, simply output the number of words and unique words
    if not list_results: 
        
        # number of unique words / total number of words
        print(f"{len(set(words))} / {len(words)}")

    else: 
        
        # get tuples of words with count
        word_count_pairs = count_words(words)
  
        # output table of words
        for word, count in word_count_pairs: 
            print(f"{word}\t{count}")


if __name__ == "__main__":

    # create Argument parser
    parser = argparse.ArgumentParser(
                    prog='Word Count',
                    description='Count the number of words in a file',
                    )

    parser.add_argument('input', nargs='?', 
                        type=argparse.FileType(),
                        default=sys.stdin, 
                        help  = 'specify path to input file or provide file content via stdin ')   
    
    parser.add_argument('-I', action='store_true',
                        help = "ignore case")
    
    parser.add_argument('-l', action='store_true', 
                        help = "out list of words instead of total word count")


    # parse arguments
    args = parser.parse_args()

    main(file_content= args.input.read(), ignorecase=args.I, list_results = args.l)