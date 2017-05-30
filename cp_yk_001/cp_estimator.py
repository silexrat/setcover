#!/usr/bin/env python
# encoding: utf-8
from itertools import chain


class Estimator(object):
    def __init__(self, task):
        self.set_costs = {s.index: s.cost for s in task.sets}

    def get_optimistic(self, state):
        # split every set on the not covered items and choose the cheapest one for every item
        splitted_costs = {set_idx: float(self.set_costs[set_idx]) / len(items)
                          for set_idx, items in state.set2items.iteritems()
                          if items}
        additional = sum(min(splitted_costs[set_idx] for set_idx in sets)
                         for item, sets in state.item2sets.iteritems())
        return state.current_cost + additional

    def cost_of_chosen_list(self, chosen_sets):
        return sum(self.set_costs[s_idx] for s_idx in chosen_sets)

    def cost_of_chosen(self, set_idx):
        return self.set_costs[set_idx]

    def get_perspective_set(self, state):
        min_cover = min(map(len, state.item2sets.itervalues()))

        sets = set(chain.from_iterable(sets
                                       for sets in state.item2sets.itervalues()
                                       if len(sets) == min_cover))

        return min(sets, key=lambda set_idx: float(self.set_costs[set_idx]) / len(state.set2items[set_idx]))

    def cheapest_set(self, sets):
        return min(sets, key=lambda set_idx: self.set_costs[set_idx])
