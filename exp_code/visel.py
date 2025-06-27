#!/usr/bin/env python3

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2025 Andrzej Kaczmarczyk<droodev@gmail.com>
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the “Software”), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import argparse
import networkx as nx
import matplotlib.pyplot as plt

import readel


def show_election(election):

    cap = 30

    def v_node_label(index):
        return min(len(election.candidates), cap) + index

    voter_nodes = [
        (v_node_label(i), {"color": "#8B0000"})
        for i in range(len(election.votes))
        if i < cap
    ]

    graph = nx.Graph()
    graph.add_nodes_from(
        (c.ordinal_number for c in election.candidates if c.ordinal_number < cap)
    )
    graph.add_nodes_from(voter_nodes)
    for ord_vote in enumerate(election.votes):
        if ord_vote[0] >= cap:
            continue
        for approved in ord_vote[1].approvals:
            if approved >= cap:
                continue
            graph.add_edge(v_node_label(ord_vote[0]), approved)

    # Then create a bipartite layout
    pos = nx.bipartite_layout(graph, (v[0] for v in voter_nodes))

    colors = [node[1].get("color", "#A0CBE2") for node in graph.nodes().data()]

    # Pass that layout to nx.draw
    nx.draw(
        graph,
        pos,
        node_color=colors,
        edge_color="#00bb5e",
        width=1,
        edge_cmap=plt.cm.Blues,
        with_labels=True,
    )
    plt.show()


def get_args_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("-if", "--inputFile", required=True, help="Election to draw")
    return ap


def main(parsed_args):
    election_path = parsed_args.inputFile
    election = readel.read_preflib_election(election_path)
    show_election(election)


if __name__ == "__main__":
    args = get_args_parser().parse_args()
    main(args)
