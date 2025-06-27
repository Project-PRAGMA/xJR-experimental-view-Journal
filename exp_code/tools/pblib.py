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

from pathlib import Path
import sys

sys.path.append("..")

import distribs


def collect_ignored_files(path):
    with open(path, "r") as ignored_f:
        ignored_paths = [Path(line.strip()) for line in ignored_f]
    return ignored_paths


def get_election_based_distributions(directory, ignore_file=None):
    """
    Returns a collection of real-life distribution based on the given directory
    """
    ignored_paths = collect_ignored_files(path) if ignore_file else []
    extension = "pb"
    distros = [
        distribs.PabulibElectionBasedDistribution(path)
        for path in list(Path(directory).glob("**/*." + extension))
        if path not in ignored_paths
    ]
    return distros


def get_election_composite_distributions(directory, ignore_file=None):
    """
    Returns a composite distribution based on the given directory
    """
    ignored_paths = collect_ignored_files(path) if ignore_file else []
    extension = "pb"
    distros = [
        distribs.PabulibElectionBasedDistribution(path)
        for path in list(Path(directory).glob("**/*." + extension))
        if path not in ignored_paths
    ]
    return distribs.PabulibElectionCompositeDistribution(
        get_election_based_distributions(directory, ignored_paths), "canonical_pabulib"
    )
