#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

script for plotting gold and health vs rounds from runRobotRace.py output

"""
import argparse
import matplotlib.pyplot as plt

def main(args): 
    
    
    gold = {}
    health = {}
    
    # read gold and health per round for all players
    with open(args.input) as f: 
        
        lines = f.readlines()
        i = 0
        
        while i < len(lines):
            
            line = lines[i]
            if line.split() == ['Player', 'Health', 'Gold', 'Position']: 
                while 'Gold Pots' not in lines[i+1]:
                    i+=1
                    d = lines[i].split()
                   
                    if d[0] not in gold: 
                        gold[d[0]] = []
                        health[d[0]] = []
                        
                    gold[d[0]].append(int(d[2]))
                    health[d[0]].append(int(d[1]))
            i+=1
               
    # plot progression of gold and health per round
    fig, axes = plt.subplots(2, 1, figsize = (7, 7))

    ax = axes[0]
    for player, g in gold.items(): 
        ax.plot(g, label = player, lw = 0.7)
    ax.set_xlabel('round')
    ax.set_ylabel('gold')
    ax.legend(fontsize = 8, handlelength =1, ncol = len(gold), loc = 'lower center', bbox_to_anchor  = (0.5, 1))


    ax = axes[1]
    for player, g in health.items(): 
        ax.plot(g, label = player, lw = 0.7)
    ax.set_xlabel('round')
    ax.set_ylabel('health')
    ax.legend(fontsize = 8, handlelength =1, ncol = len(gold), loc = 'lower center', bbox_to_anchor  = (0.5, 1))
    
    plt.tight_layout()
    plt.savefig('.'.join([args.output, args.format]))

if __name__ == '__main__': 
    


    parser = argparse.ArgumentParser(description="plot RobotRace")
    parser.add_argument('-i', '--input', help="input file", type=str)
    parser.add_argument('-o', '--output', help="output file", type=str, default = 'RobotRace')
    parser.add_argument('-f', '--format', help="output file format", type=str, default='pdf')
    
    
    args = parser.parse_args()

    main(args)

             

