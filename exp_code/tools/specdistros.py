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

import math
import sys

sys.path.append("..")

import distribs
import tools.pblib as pbtools


def get_line_voters_distributions(groups_count):
    return [get_line_voters_distribution(gc) for gc in range(4, 21, 2)]


def get_anti_ejr_distributions(committee_size, cand_count, voters_count):
    # parties_counts = range(2,11)
    parties_counts = range(2, 3)
    return [
        distribs.PartyListWithCoreLinRemainder(
            discore.DistributionParameters(
                committee_size=committee_size,
                parties_count=pc,
                remaining_prob=rem_prob,
                min_cand_count=cand_count,
                min_votes_count=voters_count,
            )
        )
        for pc in parties_counts
        for rem_prob in [  # [0.3 + c*0.0125 for c in range(56)]
            0.0 + c * 0.0125 for c in range(81)
        ]
    ]


def get_line_voters_distribution(groups_count):
    min_cand_count = 100
    cand_count = math.ceil(min_cand_count / groups_count) * groups_count

    min_votes_count = 100
    voters_count = math.ceil(min_votes_count / groups_count) * groups_count

    group_probabilities = []
    for voter_index in range(voters_count):
        group_probabilities.append(
            [
                (
                    1
                    if group_index == voter_index % groups_count
                    or (group_index + 1) % groups_count == voter_index % groups_count
                    else 0
                )
                for group_index in range(groups_count)
            ]
        )

    candidates = [cands.Candidate(c) for c in range(cand_count)]
    candidates = cands.Candidates(candidates)
    return distribs.LineVotersDistribution(
        discore.DistributionParameters(
            candidates=candidates,
            overlapping_ratio=0,
            groups_count=groups_count,
            votes_count=voters_count,
            voter_group_probabilities=group_probabilities,
        )
    )
