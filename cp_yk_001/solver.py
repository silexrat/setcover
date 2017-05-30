#!/usr/bin/python
# -*- coding: utf-8 -*-
from reader import parse_input


def solve_it(input_data):
    item_count, set_count, sets = parse_input(input_data)

    # build a trivial solution
    # pick add sets one-by-one until all the items are covered
    solution = [0]*set_count
    coverted = set()
    
    for s in sets:
        solution[s.index] = 1
        coverted |= set(s.items)
        if len(coverted) >= item_count:
            break
        
    # calculate the cost of the solution
    obj = sum([s.cost*solution[s.index] for s in sets])

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
    else:
        file_location = '../data/sc_6_1'

    input_data_file = open(file_location, 'r')
    input_data = ''.join(input_data_file.readlines())
    input_data_file.close()
    print 'Solving:', file_location
    print solve_it(input_data)

