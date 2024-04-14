#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main(args):
    
    file = args[1]
    
    print('Hello World!')
    
    with open(file, 'r') as f: 
        print(f.read().rstrip('\n'))
    

if __name__ == '__main__': 
    main(sys.argv)

