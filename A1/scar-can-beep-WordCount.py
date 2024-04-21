#IMPORT
import argparse

#FUNCTIONS
def call_parser():
    '''
    Parses the argument for use in Terminal.

    Returns:
    - filename: string of input file name
    - ignore: boolean (should the case be ignored?)
    - list: boolean (should it print the sorted list?)
    '''
    #PARSER
    parser = argparse.ArgumentParser('Calculate the sum of squares')
    parser.add_argument('file', help='The input file')
    parser.add_argument('-I', '--ignore', action='store_true', help='Ignore case')
    parser.add_argument('-l', '--list', action='store_true', help='Give list')

    args = parser.parse_args()
    return args.file, args.ignore, args.list

def get_word_count(file_name, ignore=False, return_list=False):
    
    #INPUT
    with open(file_name,'r',encoding='utf-8') as input_file:
        input = input_file.readlines()
    all_words = {}
    special_chars = '~!@#$%^&*()_±={}|[]:";<>?,./- ' + "'"
    word = ''
    count = 0

    #MAIN LOOP
    for line in input:
        for char in line:
            if char in special_chars or char == '\n':
                if word == '':
                    continue
                try:
                    all_words[word]+=1
                except:
                    all_words[word]=1
                count+=1
                word = ''
            else:
                if ignore:
                    word+=char.lower()
                else:
                    word+=char

    #OUTPUT
    if return_list:
        sorted_items = sorted(all_words,key=lambda x: (-all_words[x],x))
        for i in sorted_items: 
            print(f'{i}\t{all_words[i]}')
    else:
        print(f'{len(all_words)}/{count}')

file_name, ignore, return_list = call_parser()
get_word_count(file_name, ignore, return_list)

                
                
            
            


