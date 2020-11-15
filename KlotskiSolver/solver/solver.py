from typing import Callable
import networkx as nx
from queue import Queue

from KlotskiSolver.solver.board import Board


class Solver:
    def __init__(self, starting_layout: Board, end_condition: Callable[[Board], bool]):
        self.starting_layout = starting_layout
        self.end_condition = end_condition
        self.g = nx.Graph()
        self.should_thread_keep_going = False

    def generate_graph(self):
        self.g.clear()
        self.g.add_node(self.starting_layout)
        q = Queue()
        q.put(self.starting_layout)
        self.should_thread_keep_going = True
        while not q.empty() and self.should_thread_keep_going:
            b = q.get()  # type:Board
            if self.end_condition(b):
                return self.g, b
            if not self.g.nodes[b].get('expanded'):
                moves = b.generate_possible_moves()
                for move in moves:
                    self.g.add_edge(b, move)
                    q.put(move)
                    if self.end_condition(move):
                        return self.g, move
                self.g.nodes[b]['expanded'] = True
        return self.g, None

    def cancel_graph_generation(self):
        self.should_thread_keep_going = False
