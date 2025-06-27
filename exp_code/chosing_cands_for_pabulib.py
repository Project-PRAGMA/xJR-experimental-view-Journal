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


import statistics
import random
import pathlib
import argparse

import core.mylog as mylog

logger = mylog.get_logger()
import distribs


def get_argument_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-if",
        "--input_file",
        required=True,
        help="Pabulib source distribution",
        type=pathlib.PurePath,
    )
    ap.add_argument(
        "-t",
        "--trialsCount",
        required=True,
        help="Number of " "experiment trials for one distribution",
        type=int,
    )
    ap.add_argument(
        "-n",
        "--voters_count",
        required=True,
        help="Number of voters in a single election",
        type=int,
    )
    ap.add_argument(
        "-m",
        "--candidates_count",
        required=True,
        help="Number of candidates in a single election",
        type=int,
    )
    return ap


if __name__ == "__main__":
    args = get_argument_parser().parse_args()

    pabulib_distro = distribs.PabulibElectionBasedDistribution(args.input_file, True)
    means = []
    for _ in range(args.trialsCount):
        election = pabulib_distro.generate(100, 100)
        means.append(statistics.mean([len(vote.approvals) for vote in election.votes]))
    print(statistics.stdev(means))
