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

from core.baseProgram import compute, COVERAGE_MAX, APPROVAL_MAX, compute_pav
from core.baseProgram import (
    COMPUTE_PJR,
    COMPUTE_EJR,
    computeEJRorPJR,
    computePJR,
    computeEJR,
)
from gmpy2 import mpq
from elections import ApprovalElection
from candidates import Candidates, Candidate
import sys
import tools.tools as tools
import core.mylog as mylog

logger = mylog.get_logger()
import lcgroups
from functools import reduce


class JRCommittee(object):
    def compute(self, candidates, voters, mesh, stats, existenceSymbol):
        committeeSize = mesh.committeeSize
        mesh.clipMeshByValues(
            stats.minJRCov, stats.maxJRCov, stats.minJRApp, stats.maxJRApp
        )

        for cell in mesh.getUnclippedCells():
            lc, uc, la, ua = cell
            toOut = "."
            #      print(lc, uc, la, ua )
            if compute(candidates, voters, la, ua, lc, uc, committeeSize)[0]:
                toOut = existenceSymbol
            mesh.setValueOfCell(cell, toOut)

    def compute_once(
        self, candidates, voters, committee_size, min_cov, max_cov, min_app, max_app
    ):
        return compute(
            candidates, voters, min_app, max_app, min_cov, max_cov, committee_size
        )

    def description(self):
        return "JR Committee"


def _compute_relevant_cands(committee_size, candidates, voters):
    cands = Candidates([Candidate(c) for c in candidates])
    election = ApprovalElection(voters, cands)
    logger.debug(f"Starting LC group analysis")
    lc_groups_data = lcgroups.large_cohesive_groups_analysis(election, committee_size)
    max_lc_group_size = lc_groups_data["max_ell_in_lc_groups"]
    usable_cands_per_g_size = lc_groups_data["usable_cands_per_g_size"]
    maximal_lc_groups = lc_groups_data["maximal_lc_groups"]
    logger.debug(f"#Maximal lc Groups: {len(maximal_lc_groups)}")
    pjr_ejr_relevant_cands = reduce(
        lambda acc, usable: acc | usable,
        [item[1] for item in usable_cands_per_g_size.items() if item[0] > 1],
        set(),
    )
    logger.debug(
        f"All candidates: {len(candidates)}; usable candidates: {len(pjr_ejr_relevant_cands)}"
        f"; Ratio: {int(len(pjr_ejr_relevant_cands)/len(candidates)*100)}%"
    )
    return pjr_ejr_relevant_cands


class PJRCommittee(object):

    def __init__(self):
        self.relevant_cands = None

    def compute(self, candidates, voters, mesh, stats, existenceSymbol):
        committeeSize = mesh.committeeSize
        mesh.clipMeshByValues(
            stats.minJRCov, stats.maxJRCov, stats.minJRApp, stats.maxJRApp
        )

        for cell in mesh.getUnclippedCells():
            lc, uc, la, ua = cell
            toOut = "."
            if computeEJRorPJR(
                candidates, voters, la, ua, lc, uc, committeeSize, COMPUTE_PJR
            )[0]:
                toOut = existenceSymbol
            mesh.setValueOfCell(cell, toOut)

    def compute_once(
        self, candidates, voters, committee_size, min_cov, max_cov, min_app, max_app
    ):
        if self.relevant_cands is None:
            self.relevant_cands = _compute_relevant_cands(
                committee_size, candidates, voters
            )
        return computePJR(
            candidates,
            voters,
            min_app,
            max_app,
            min_cov,
            max_cov,
            committee_size,
            self.relevant_cands,
        )

    def description(self):
        return "PJR Committee"


class EJRCommittee(object):
    def __init__(self):
        self.relevant_cands = None

    def compute(self, candidates, voters, mesh, stats, existenceSymbol):
        committeeSize = mesh.committeeSize
        mesh.clipMeshByValues(
            stats.minJRCov, stats.maxJRCov, stats.minJRApp, stats.maxJRApp
        )

        for cell in mesh.getUnclippedCells():
            lc, uc, la, ua = cell
            toOut = "."
            if computeEJRorPJR(
                candidates, voters, la, ua, lc, uc, committeeSize, COMPUTE_EJR
            )[0]:
                toOut = existenceSymbol
            mesh.setValueOfCell(cell, toOut)

    def compute_once(
        self, candidates, voters, committee_size, min_cov, max_cov, min_app, max_app
    ):
        if self.relevant_cands is None:
            self.relevant_cands = _compute_relevant_cands(
                committee_size, candidates, voters
            )
        return computeEJR(
            candidates,
            voters,
            min_app,
            max_app,
            min_cov,
            max_cov,
            committee_size,
            self.relevant_cands,
        )

    def description(self):
        return "EJR Committee"


class AnyCommittee(object):
    def compute(self, candidates, voters, mesh, stats, existenceSymbol):
        committeeSize = mesh.committeeSize
        mesh.clipMeshByValues(stats.minCov, stats.maxCov, stats.minApp, stats.maxApp)

        for cell in mesh.getUnclippedCells():
            lc, uc, la, ua = cell
            toOut = "."
            #      print(lc, uc, la, ua )
            if compute(
                candidates,
                voters,
                la,
                ua,
                lc,
                uc,
                committeeSize,
                goal=APPROVAL_MAX,
                requireJR=False,
            )[0]:
                toOut = existenceSymbol
            mesh.setValueOfCell(cell, toOut)

    def compute_once(
        self, candidates, voters, committee_size, min_cov, max_cov, min_app, max_app
    ):
        return compute(
            candidates,
            voters,
            min_app,
            max_app,
            min_cov,
            max_cov,
            committee_size,
            goal=APPROVAL_MAX,
            requireJR=False,
        )

    def description(self):
        return "Any Committee"


class MaxApprovalCommittee(object):
    def compute(self, candidates, voters, mesh, stats, existenceSymbol):
        committeeSize = mesh.committeeSize
        mesh.clipMeshByValues(stats.minCov, stats.maxCov, stats.maxApp, stats.maxApp)

        for cell in mesh.getUnclippedCells():
            lc, uc, la, ua = cell
            toOut = "."
            #      print(lc, uc, la, ua )
            if compute(
                candidates,
                voters,
                la,
                ua,
                lc,
                uc,
                committeeSize,
                goal=COVERAGE_MAX,
                requireJR=False,
            )[0]:
                toOut = existenceSymbol
            mesh.setValueOfCell(cell, toOut)

    def description(self):
        return "Max. Approval Committee"


class ChamberlinCourantCommittee(object):
    def compute(self, candidates, voters, mesh, stats, existenceSymbol):
        committeeSize = mesh.committeeSize
        mesh.clipMeshByValues(stats.maxCov, stats.maxCov, stats.minApp, stats.maxApp)

        for cell in mesh.getUnclippedCells():
            lc, uc, la, ua = cell
            toOut = "."
            #      print(lc, uc, la, ua )
            if compute(
                candidates, voters, la, ua, lc, uc, committeeSize, requireJR=False
            )[0]:
                toOut = existenceSymbol
            mesh.setValueOfCell(cell, toOut)

    def description(self):
        return "Chamberlin-Courant Committee"


class SinglePAV(object):

    def __init__(self):
        self.computed_data = None

    def compute(
        self, candidates, voters, min_app, max_app, min_cov, max_cov, comm_size
    ):
        success, satisfaction, _, coverage, approval = compute_pav(
            candidates, voters, min_app, max_app, min_cov, max_cov, comm_size
        )
        return success, satisfaction, coverage, approval

    def compute_once(
        self, candidates, voters, committee_size, min_cov, max_cov, min_app, max_app
    ):
        # We actually really want to compute it once!
        if not self.computed_data:
            self.computed_data = self.compute(
                candidates, voters, min_app, max_app, min_cov, max_cov, committee_size
            )
        success = (
            self.computed_data[2] <= max_cov
            and self.computed_data[2] >= min_cov
            and self.computed_data[3] <= max_app
            and self.computed_data[2] >= min_app
        )
        return (
            success,
            self.computed_data[1],
            self.computed_data[2],
            self.computed_data[3],
        )

    def description(self):
        return "Single PAV Committee"


class SingleSequentialPhragmen(object):

    def __init__(self):
        self.computed_data = None

    def compute(self, candidates, voters, committee_size):
        committees = self.computeAllCommittees(candidates, voters, committee_size)
        committeesWithAppAndCoverage = []
        # Select only one committee
        selected_committee = committees[0]
        coverage, approval = tools.committeApprovalAndCoverage(
            candidates, voters, selected_committee
        )
        return True, None, coverage, approval

    def compute_once(
        self, candidates, voters, committee_size, min_cov, max_cov, min_app, max_app
    ):
        if isinstance(voters, list):
            voters = dict(
                (index_voter[0], index_voter[1].approvals)
                for index_voter in enumerate(voters)
            )
        # We actually really want to compute it once!
        if not self.computed_data:
            self.computed_data = self.compute(candidates, voters, committee_size)
        success = (
            self.computed_data[2] <= max_cov
            and self.computed_data[2] >= min_cov
            and self.computed_data[3] <= max_app
            and self.computed_data[2] >= min_app
        )
        return (
            success,
            self.computed_data[1],
            self.computed_data[2],
            self.computed_data[3],
        )

    def description(self):
        return "Single sequential Phragmen committee"

    def computeAllCommittees(self, candidates, preferences, committeeSize):

        def __enough_approved_candiates():
            appr = set()
            for pref in preferences.values():
                appr.update(set(pref))
            if len(appr) < committeeSize:
                print("committeesize is larger than number of approved candidates")
                exit()

        __enough_approved_candiates()

        load = {vnr: 0 for vnr in preferences.keys()}
        com_loads = {(): load}

        approvers_weight = {}
        for c in candidates:
            approvers_weight[c] = sum(1 for v in preferences.values() if c in v)

        #
        for _ in range(
            0, committeeSize
        ):  # size of partial committees currently under consideration
            com_loads_next = {}
            for committee, load in iter(com_loads.items()):
                approvers_load = {}
                for c in candidates:
                    approvers_load[c] = sum(
                        load[vnr] for vnr, v in preferences.items() if c in v
                    )
                new_maxload = [
                    (
                        mpq(approvers_load[c] + 1, approvers_weight[c])
                        if approvers_weight[c] > 0
                        else len(candidates) * len(preferences)
                    )
                    for c in candidates
                ]
                for c in candidates:
                    if c in committee:
                        new_maxload[c] = sys.maxsize
                for c in candidates:
                    if new_maxload[c] <= min(new_maxload):
                        new_load = {}
                        for vnr, v in preferences.items():
                            if c in v:
                                new_load[vnr] = new_maxload[c]
                            else:
                                new_load[vnr] = load[vnr]
                        com_loads_next[tuple(sorted(committee + (c,)))] = new_load
            # remove suboptimal committees, leave only the best branching_factor many (subject to ties)
            com_loads = {}
            cutoff = min([max(load) for load in com_loads_next.values()])
            for com, load in iter(com_loads_next.items()):
                if max(load) <= cutoff:
                    com_loads[com] = load
        return [set(comm) for comm in com_loads.keys()]
