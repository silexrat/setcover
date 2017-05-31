#!/usr/bin/env python
# encoding: utf-8
import sys

from cp_state import State

# Python has no tail-recursion optimization.
# Even more, python has a limit on recursion depth
# So, we need to write big loops iteratively


class Solution(object):
    def __init__(self, task):
        self.best_cost = sys.maxint  # Larger than any cost, that we can take
        self.best_solution = None
        self.set_count = task.set_count
        self.proven_as_optimal = False
        self.steps = 0

    def store_result(self, state):
        if state.current_cost < self.best_cost:
            #print self.steps, 'update solution to', state.current_cost
            solution = [0] * self.set_count
            state_on_stack = state
            while state_on_stack:
                for s in state_on_stack.iter_chosen_sets():
                    solution[s] = 1
                state_on_stack = state_on_stack.parent

            self.best_solution = solution
            self.best_cost = state.current_cost

    def __repr__(self):
        return 'Solution(cost={}, optimal={}, steps={}, sets={})'.format(
            self.best_cost, self.proven_as_optimal, self.steps, self.best_solution)


def deep_search(task):
    state = State.from_task(task)
    solution = Solution(task)
    while state:
        solution.steps += 1
        if not state.is_feasible:
            state = state.parent
            continue

        if state.is_all_covered():
            solution.store_result(state)
            state = state.negate()
            continue

        if state.get_optimistic_cost() >= solution.best_cost:
            state = state.negate()
            continue

        state = state.next_child()

    solution.proven_as_optimal = True
    return solution


if __name__ == '__main__':
    from reader import read_input
    task = read_input('sc_27_0')
    print deep_search(task)
    # from profile import run
    # run('deep_search(task)', sort=2)  # sort - 2 cumtime, 1 - totime
