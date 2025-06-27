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
import itertools
from functools import reduce

import core.mylog as mylog
import lcgroups

logger = mylog.get_logger()


def get_largeness_threshold(ell, votes_count, comm_size):
    return math.ceil((votes_count * ell) / comm_size)


def get_group_approvals(supporting_voters, votes):
    return reduce(lambda acc, v: acc | votes[v].approvals, supporting_voters, set())


def get_group_approvals_from_voter_obj(supporting_voters):
    return reduce(lambda acc, v: acc | v.approvals, supporting_voters, set())


def large_cohesive_groups_analysis(election, comm_size):
    return_dict = {
        "maximal_lc_groups": dict(),
        "usable_cands_per_g_size": dict(),
        "max_ell_in_lc_groups": 0,
    }
    cands_as_numbers = [c.ordinal_number for c in election.candidates]
    current_max_ell = 0
    candidate_support_map = election.get_candidate_support_map()
    votes = election.votes
    for group_size in range(1, comm_size + 1):
        current_usable_cands = set()
        l_thres = get_largeness_threshold(group_size, len(votes), comm_size)
        # logger.info(f"Testing group size: {group_size} w. thr: {l_thres}")
        for group_inducing_cands in itertools.combinations(
            cands_as_numbers, group_size
        ):
            cands_supporters = map(
                lambda x: candidate_support_map[x], group_inducing_cands
            )
            supporting_voters = reduce(lambda a, b: a & b, cands_supporters)
            if len(supporting_voters) >= l_thres:
                return_dict["max_ell_in_lc_groups"] = group_size
                all_group_members_approvals = get_group_approvals(
                    supporting_voters, votes
                )
                maximal_lc_group = {
                    "voters": supporting_voters,
                    "inducing_cands": group_inducing_cands,
                    "approved_by_all_group_members": all_group_members_approvals,
                    "ell": group_size,
                }
                return_dict["maximal_lc_groups"].setdefault(group_size, []).append(
                    maximal_lc_group
                )
                current_usable_cands |= all_group_members_approvals
        if return_dict["max_ell_in_lc_groups"] < group_size:
            break
        return_dict["usable_cands_per_g_size"][group_size] = current_usable_cands
    return return_dict


def extract_all_lc_groups(maximal_lc_groups, comm_size, votes, min_ell, max_ell=None):
    votes_count = len(votes)
    all_groups = []
    for ell, groups in maximal_lc_groups.items():
        if ell < min_ell:
            continue
        if max_ell and ell > max_ell:
            continue
        l_thres = get_largeness_threshold(ell, votes_count, comm_size)
        for group in groups:
            for new_group_voters in itertools.combinations(group["voters"], l_thres):
                new_lc_group = {
                    "voters": new_group_voters,
                    "inducing_cands": group["inducing_cands"],
                    "approved_by_all_group_members": get_group_approvals(
                        new_group_voters, votes
                    ),
                    "ell": ell,
                }
                all_groups.append(new_lc_group)
    return all_groups
