#!/usr/bin/env python
# encoding: utf-8
from collections import defaultdict

from cp_estimator import Estimator


class State(object):
    def __init__(self, estimator, set2items, item2sets,
                 parent=None, picked_set=None, decision=None):
        # Don't use this constructor directly. Use .from_task() instead
        self.estimator = estimator  # just copy pointer from the parent
        self.set2items = set2items  # only for not chosen sets and not covered items
        self.item2sets = item2sets  # only for not covered items and not chosen sets
        self.parent = parent        # parent state
        self.picked_set = picked_set
        self.decision = decision  # Whether we build picked_set or not
        self.is_feasible = True
        if decision:
            self.chosen_sets = {picked_set}
        else:
            self.chosen_sets = set()
        self.propagate_constaints()
        self.recalc_cost()

    def recalc_cost(self):
        additional = self.estimator.cost_of_chosen_list(self.chosen_sets)
        if self.parent is None:
            self.current_cost = additional
        else:
            self.current_cost = self.parent.current_cost + additional

    @classmethod
    def from_task(cls, task):
        # Make initial state
        estimator = Estimator(task)

        set2items = {s.index: set(s.items) for s in task.sets}
        item2sets = defaultdict(set)
        for set_idx, set_items in set2items.iteritems():
            for item_idx in set_items:
                item2sets[item_idx].add(set_idx)

        return cls(estimator, set2items, dict(item2sets),
                   parent=None, picked_set=None, decision=False)

    def __repr__(self):
        return 'State(picked={},chosen={})'.format(self.picked_set, self.decision)

    # Search

    def next_child(self):
        picked_set = self.estimator.get_perspective_set(self)
        return self.create_child(picked_set, decision=True)

    def create_child(self, picked_set, decision):
        set2items = {s: i.copy() for s, i in self.set2items.iteritems()}  # TODO: can we avoid this expensive copy?
        item2sets = {i: s.copy() for i, s in self.item2sets.iteritems()}
        return self.__class__(self.estimator, set2items, item2sets,
                              parent=self, picked_set=picked_set, decision=decision)

    def negate(self):
        # Generate sibling state, where picked_set is not chosen
        # If we already there, rollback to the parent state and repeat on it
        state = self
        while state:
            if state.decision:
                return state.parent.create_child(state.picked_set, decision=False)
            else:
                state = state.parent
        return None # if we have eventually got stat = None, it means that we are reached initial state

    # Constraints propagation

    def propagate_constaints(self):
        if self.decision:
            self.propagate_on_choice()
        else:
            self.propagate_on_toss()

    def propagate_on_choice(self):
        self.on_sets_chosen(self.chosen_sets)

    def propagate_on_toss(self):
        if self.picked_set is not None:
            orphan_items = self.set2items.pop(self.picked_set)
            for item_idx in orphan_items:
                sets = self.item2sets[item_idx]
                sets.remove(self.picked_set)
                if not sets:
                    self.is_feasible = False
                    # No matter, what else. State doesn't lead to any feasible solutions
                    return

        # Immediately set 1 for every set that can't be replaced with another set
        required_sets = self.detect_required_sets()
        self.chosen_sets.update(required_sets)
        self.on_sets_chosen(required_sets)

    def detect_required_sets(self):
        required_sets = set()
        for item, sets in self.item2sets.iteritems():
            if len(sets) == 1:
                required_sets.update(sets)
        return required_sets

    def on_items_covered(self, to_remove):
        overvalued_sets = set()
        for item in to_remove:
            overvalued_sets.update(self.item2sets.pop(item))

        for s in overvalued_sets & set(self.set2items):
            items = self.set2items[s]
            items -= to_remove
            if not items:
                del self.set2items[s]

    def on_sets_chosen(self, sets):
        covered_items = set()
        for s in sets:
            covered_items.update(self.set2items.pop(s))

        self.on_items_covered(covered_items)

    # Getting info

    def iter_chosen_sets(self):
        return self.chosen_sets

    def is_all_covered(self):
        return not self.item2sets

    def get_optimistic_cost(self):
        return self.estimator.get_optimistic(self)

