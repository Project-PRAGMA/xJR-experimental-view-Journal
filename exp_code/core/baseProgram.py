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

from gurobipy import *
import multiprocessing as mproc

import core.cfg as cfg
import core.mylog as mylog

logger = mylog.get_logger()
import isxJRChecker
from datetime import datetime

import math

CANDIDATE_VARIABLE_NAME = "cc"
COVERAGE_VARIABLE_NAME = "coverage"
APPROVAL_VARIABLE_NAME = "approvalScore"

JR_CONSTRAINT_NAME = "jrconstraint"

COMM_OF_GIVEN_SIZE = 0
CORE_MIN = 1
APPROVAL_MAX = 2
APPROVAL_MIN = 3
COVERAGE_MAX = 4
COVERAGE_MIN = 5

COMPUTE_EJR = 0
COMPUTE_PJR = 1

ERASE_LINE_ASCII = "\u001b[2K"


def compute(
    candidates,
    voters,
    lab,
    uab,
    lcb,
    ucb,
    committeeSize,
    goal=COMM_OF_GIVEN_SIZE,
    requireJR=True,
    just_group_size=None,
):

    try:
        m, _, _ = _basicModel(
            candidates,
            voters,
            lab,
            uab,
            lcb,
            ucb,
            committeeSize,
            goal,
            requireJR,
            just_group_size,
        )
        m.optimize()
        if not m.Status == GRB.OPTIMAL:
            return False, None
        else:
            cov_var = m.getVarByName(COVERAGE_VARIABLE_NAME)
            app_var = m.getVarByName(APPROVAL_VARIABLE_NAME)
            return (
                True,
                int(m.objVal),
                int(round(cov_var.X, 0)),
                int(round(app_var.X, 0)),
            )
    except GurobiError as e:
        print(f"Error reported: {e}")


def enumerate_specific_jr_groups_comp_hints(
    candidates,
    voters,
    committeeSize,
    just_group_size=None,
    cand_hints=None,
    available_candidates=None,
):
    """
    cand_hints is a list of tuples; each tuple consists of a set of
    a set of candidates and a number specifying how many of them have to
    be selected in a final committee

    forbidden_groups is a list of lists/sets representing committees that are
    already checked
    """
    lab = 0
    uab = len(voters) * committeeSize
    lcb = 0
    ucb = len(voters)
    requireJR = True
    goal = COMM_OF_GIVEN_SIZE if just_group_size else CORE_MIN

    if goal == COMM_OF_GIVEN_SIZE:
        logger.debug(
            f"Computing all JR-justifying groups of size: {just_group_size} "
            f"with {len(cand_hints) if cand_hints else 0} candidate hints"
        )
    else:
        logger.debug(f"Computing all minimum JR-justifying groups")

    try:
        m, _, _ = _basicModel(
            candidates,
            voters,
            lab,
            uab,
            lcb,
            ucb,
            committeeSize,
            goal,
            requireJR,
            just_group_size,
        )

        m.update()

        if cand_hints:
            # logger.info(f"HINTs: {len(cand_hints)}")
            for potential_cands, required_number in cand_hints:
                if required_number <= 1:
                    continue
                m.addConstr(
                    quicksum(
                        m.getVarByName(
                            "{}[{}]".format(CANDIDATE_VARIABLE_NAME, cand_id)
                        )
                        for cand_id in potential_cands
                    )
                    >= required_number
                )

        if available_candidates:
            for cand_id in candidates:
                if cand_id in available_candidates:
                    continue
                m.addConstr(
                    m.getVarByName("{}[{}]".format(CANDIDATE_VARIABLE_NAME, cand_id))
                    == 0
                )

        solutions_chunk = 10
        m.setParam(GRB.Param.PoolSearchMode, 2)
        # Get solutions_chunk possible solutions
        m.setParam(GRB.Param.PoolSolutions, solutions_chunk)
        m.setParam(GRB.Param.PoolGap, 0)
        m.setParam(GRB.Param.MIPGap, 0)

        continue_computing = True

        while continue_computing:
            m.update()
            m.optimize()
            if not m.Status == GRB.OPTIMAL:
                logger.debug(f"No minimum JR justifying groups found")
                break
            solutions = []
            logger.debug(f"JR justifying groups count: {m.SolCount}")
            for sol_number in range(m.SolCount):
                committee = []
                m.Params.SolutionNumber = sol_number
                for candId in candidates:
                    candVar = m.getVarByName(
                        "{}[{}]".format(CANDIDATE_VARIABLE_NAME, candId)
                    )
                    if int(round(candVar.Xn, 0)) == 1:
                        committee.append(candId)
                cov_var = m.getVarByName(COVERAGE_VARIABLE_NAME)
                app_var = m.getVarByName(APPROVAL_VARIABLE_NAME)
                solutions.append(
                    (
                        int(m.poolObjVal),
                        int(round(cov_var.Xn, 0)),
                        int(round(app_var.Xn, 0)),
                        committee,
                    )
                )
            continue_computing = m.solCount == solutions_chunk
            for solution in solutions:
                # logger.info(f"yielding: {solution}")
                yield (True, solution)
            for _, _, _, forbidden_committee in solutions:
                m.addConstr(
                    quicksum(
                        m.getVarByName(
                            "{}[{}]".format(CANDIDATE_VARIABLE_NAME, cand_id)
                        )
                        for cand_id in forbidden_committee
                    )
                    <= (
                        (
                            just_group_size
                            if just_group_size is not None
                            else committeeSize
                        )
                        - 1
                    )
                )
            if continue_computing:
                logger.debug(f"Computing next solution pool")
    except GurobiError as e:
        print(f"Error reported: {e}")
    # logger.info("Finishing")
    return False, []


def enumerate_groups(
    candidates,
    voters,
    lab,
    uab,
    lcb,
    ucb,
    committeeSize,
    goal=COMM_OF_GIVEN_SIZE,
    requireJR=True,
    just_group_size=None,
    usable_cands=None,
):
    try:
        m, _, _ = _basicModel(
            candidates,
            voters,
            lab,
            uab,
            lcb,
            ucb,
            committeeSize,
            goal,
            requireJR,
            just_group_size,
        )

        m.update()
        for cand_id in [c for c in candidates if c not in usable_cands]:
            candVar = m.getVarByName("{}[{}]".format(CANDIDATE_VARIABLE_NAME, cand_id))
            m.addConstr(candVar == 0)

        m.setParam(GRB.Param.PoolSearchMode, 2)
        # Use maximum possible number of solutions
        m.setParam(GRB.Param.PoolSolutions, 2000000000)
        m.setParam(GRB.Param.PoolGap, 0)
        m.setParam(GRB.Param.MIPGap, 0)
        m.optimize()
        if not m.Status == GRB.OPTIMAL:
            logger.info(f"No minimum JR justifying groups found")
            return False, None
        solutions = []
        logger.info(f"Minimum JR justifying groups count: {m.SolCount}")
        for sol_number in range(m.SolCount):
            committee = []
            m.Params.SolutionNumber = sol_number
            for candId in candidates:
                candVar = m.getVarByName(
                    "{}[{}]".format(CANDIDATE_VARIABLE_NAME, candId)
                )
                if int(round(candVar.Xn, 0)) == 1:
                    committee.append(candId)
            cov_var = m.getVarByName(COVERAGE_VARIABLE_NAME)
            app_var = m.getVarByName(APPROVAL_VARIABLE_NAME)
            solutions.append(
                (
                    int(m.poolObjVal),
                    int(round(cov_var.Xn, 0)),
                    int(round(app_var.Xn, 0)),
                    committee,
                )
            )
        return True, solutions
    except GurobiError as e:
        print(f"Error reported: {e}")


def computeEJR(
    candidates, voters, lab, uab, lcb, ucb, committeeSize, relevant_cands=None
):
    return computeEJRorPJR(
        candidates,
        voters,
        lab,
        uab,
        lcb,
        ucb,
        committeeSize,
        COMPUTE_EJR,
        relevant_cands,
    )


def computePJR(
    candidates, voters, lab, uab, lcb, ucb, committeeSize, relevant_cands=None
):
    return computeEJRorPJR(
        candidates,
        voters,
        lab,
        uab,
        lcb,
        ucb,
        committeeSize,
        COMPUTE_PJR,
        relevant_cands,
    )


def compute_pav(
    candidates, voters, lab, uab, lcb, ucb, committeeSize, satisfactionLevel=None
):
    try:
        if isinstance(voters, list):
            voters = dict(
                (index_voter[0], index_voter[1].approvals)
                for index_voter in enumerate(voters)
            )
        m = Model("MaxApproval")
        m.setParam("OutputFlag", False)

        indicatorVCOVars = m.addVars(
            len(voters), len(candidates), committeeSize, vtype=GRB.BINARY
        )

        candidateVars = m.addVars(
            candidates, name=CANDIDATE_VARIABLE_NAME, vtype=GRB.BINARY
        )

        voterVars = m.addVars(
            voters.keys(), name="vr", vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0
        )

        coreSizeVar = m.addVar(
            name="coreSize", vtype=GRB.INTEGER, lb=0, ub=committeeSize
        )

        approvalScoreVar = m.addVar(
            name=APPROVAL_VARIABLE_NAME, vtype=GRB.INTEGER, lb=1
        )

        coverageVar = m.addVar(name=COVERAGE_VARIABLE_NAME, vtype=GRB.INTEGER, lb=1)

        satisfactionVar = m.addVar(name="satisfaction", vtype=GRB.CONTINUOUS, lb=1)

        m.addConstrs(
            indicatorVCOVars[i, j, k] <= candidateVars[j]
            for i in range(len(voters))
            for j in range(len(candidates))
            for k in range(committeeSize)
        )

        m.addConstrs(
            indicatorVCOVars.sum(i, "*", k) == 1
            for i in range(len(voters))
            for k in range(committeeSize)
        )

        m.addConstrs(
            indicatorVCOVars.sum(i, j, "*") <= 1
            for i in range(len(voters))
            for j in range(len(candidates))
        )

        m.addConstr(coreSizeVar == committeeSize)

        m.addConstr(quicksum(candidateVars[i] for i in candidates) == coreSizeVar)
        m.addConstrs(
            (voterVars[j] <= quicksum(candidateVars[i] for i in voters[j]))
            for j in voters.keys()
        )
        m.addConstrs(
            (voterVars[j] >= candidateVars[i]) for j in voters.keys() for i in voters[j]
        )

        m.addConstr(coverageVar == quicksum(voterVars[j] for j in voters.keys()))

        m.addConstr(coverageVar <= ucb)
        m.addConstr(coverageVar >= lcb)

        m.addConstr(
            approvalScoreVar
            == (
                quicksum(
                    quicksum(candidateVars[i] for j in voters.keys() if i in voters[j])
                    for i in candidates
                )
            )
        )

        m.addConstr(approvalScoreVar <= uab)
        m.addConstr(approvalScoreVar >= lab)

        coefficients = dict()
        for vnr, vote in voters.items():
            for cand in candidates:
                for k in range(committeeSize):
                    owaCoeff = float(1 / float(k + 1))
                    voterLikesCandidateCoeff = 1 if cand in vote else 0
                    coefficients[(vnr, cand, k)] = owaCoeff * float(
                        voterLikesCandidateCoeff
                    )
        m.addConstr(indicatorVCOVars.prod(coefficients) == satisfactionVar)

        if satisfactionLevel == None:
            m.setObjective(satisfactionVar, GRB.MAXIMIZE)
        else:
            m.addConstr(satisfactionVar == satisfactionLevel)

        ## MULTIPLE SOLUTIONS
        ##m.setParam(GRB.Param.PoolSolutions, 10)
        ##m.setParam(GRB.Param.PoolGap, 0)
        ##m.setParam(GRB.Param.MIPGap, 0)
        ####

        m.optimize()

        if not m.Status == GRB.OPTIMAL:
            return False, None, indicatorVCOVars, None, None
        else:
            ### LOOKING THROUGH MULTIPLE SOLUTIONS
            for sol_number in range(m.SolCount):
                # print(sol_number)
                m.Params.SolutionNumber = sol_number
            ####
            return True, m.objVal, indicatorVCOVars, coverageVar.X, approvalScoreVar.X

    except GurobiError as GErr:
        print("Error reported: {}".format(GErr))


def _basicModel(
    candidates,
    voters,
    lab,
    uab,
    lcb,
    ucb,
    committeeSize,
    goal,
    requireJR,
    just_group_size=None,
):
    def approvalMaximization():
        m.setObjective(approvalScoreVar, GRB.MAXIMIZE)

    def approvalMinimization():
        m.setObjective(approvalScoreVar, GRB.MINIMIZE)

    def coverageMaximization():
        m.setObjective(coverageVar, GRB.MAXIMIZE)

    def coverageMinimization():
        m.setObjective(coverageVar, GRB.MINIMIZE)

    def coreMinimization():
        m.setObjective(coreSizeVar, GRB.MINIMIZE)

    if isinstance(voters, list):
        voters = dict(
            (index_voter[0], index_voter[1].approvals)
            for index_voter in enumerate(voters)
        )
    try:
        m = Model("MaxApproval")
        m.setParam("OutputFlag", False)

        candidateVars = m.addVars(
            candidates, name=CANDIDATE_VARIABLE_NAME, vtype=GRB.BINARY
        )

        voterVars = m.addVars(
            voters.keys(), name="vr", vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0
        )

        coreSizeVar = m.addVar(
            name="coreSize", vtype=GRB.INTEGER, lb=0, ub=committeeSize
        )

        approvalScoreVar = m.addVar(
            name=APPROVAL_VARIABLE_NAME, vtype=GRB.INTEGER, lb=0
        )

        coverageVar = m.addVar(name=COVERAGE_VARIABLE_NAME, vtype=GRB.INTEGER, lb=0)

        if goal != CORE_MIN:
            # Check for failure of an implication that if just_group_size is true
            # then requireJR is true as well. Derived from the below
            # a => b <=> not a or b
            if not ((not (just_group_size != None)) or requireJR):
                raise ValueError(
                    "Requested a given size of a justifying group but no "
                    "JR concept required. For what the group should be justifying then?"
                )
            if just_group_size:
                m.addConstr(coreSizeVar == just_group_size)
            else:
                m.addConstr(coreSizeVar == committeeSize)

        m.addConstr(quicksum(candidateVars[i] for i in candidates) == coreSizeVar)
        m.addConstrs(
            (voterVars[j] <= quicksum(candidateVars[i] for i in voters[j]))
            for j in voters.keys()
        )
        m.addConstrs(
            (voterVars[j] >= candidateVars[i]) for j in voters.keys() for i in voters[j]
        )

        if requireJR:
            smallerThanCohesiveSize = int(
                math.ceil(float(len(voters)) / float(committeeSize) - 1)
            )
            m.addConstrs(
                (
                    quicksum(1 - voterVars[j] for j in voters.keys() if i in voters[j])
                    <= smallerThanCohesiveSize
                    for i in candidates
                ),
                JR_CONSTRAINT_NAME,
            )

        m.addConstr(coverageVar == quicksum(voterVars[j] for j in voters.keys()))

        m.addConstr(coverageVar <= ucb)
        m.addConstr(coverageVar >= lcb)

        m.addConstr(
            approvalScoreVar
            == (
                quicksum(
                    quicksum(candidateVars[i] for j in voters.keys() if i in voters[j])
                    for i in candidates
                )
            )
        )

        m.addConstr(approvalScoreVar <= uab)
        m.addConstr(approvalScoreVar >= lab)

        if goal == COMM_OF_GIVEN_SIZE or goal == CORE_MIN:
            coreMinimization()
        if goal == APPROVAL_MAX:
            approvalMaximization()
        if goal == APPROVAL_MIN:
            approvalMinimization()
        if goal == COVERAGE_MAX:
            coverageMaximization()
        if goal == COVERAGE_MIN:
            coverageMinimization()

        return (m, voterVars, candidateVars)

    except GurobiError as GErr:
        print("Error reported: {}".format(GErr))


def computeEJRorPJR(
    candidates,
    voters,
    lab,
    uab,
    lcb,
    ucb,
    committeeSize,
    whatToCompute,
    goal=COMM_OF_GIVEN_SIZE,
    pjr_ejr_relevant_cands=None,
):

    def log_computation_end(committee_counter, failed, searches_threshold=10):
        axiom = "EJR" if whatToCompute == COMPUTE_EJR else "PJR"
        result_str = f"{axiom} " + "MET" if not failed else f"NOT MET"
        if committee_counter < searches_threshold:
            logging_func = logger.debug
        else:
            logging_func = logger.info
        logging_func(f"Committee search iterations: {committee_counter} ({result_str})")

    def print_if_verbose(toprint):
        if not cfg.is_verbose:
            return
        now = datetime.now()
        dt_string = now.strftime("%d.%m.%Y %H:%M:%S")
        print(f"{ERASE_LINE_ASCII}{dt_string}: {toprint}", end="\r")

    xJRCheckers = {
        COMPUTE_EJR: isxJRChecker.isEJR_ilp,
        COMPUTE_PJR: isxJRChecker.isPJR_ilp,
    }
    if isinstance(voters, list):
        voters = dict(
            (index_voter[0], index_voter[1].approvals)
            for index_voter in enumerate(voters)
        )

    if whatToCompute not in [COMPUTE_EJR, COMPUTE_PJR]:
        raise ValueError(
            "Neither ejr nor pjr requested. Use constants to specify a correct goal."
        )

    try:
        m, _, candidate_vars = _basicModel(
            candidates, voters, lab, uab, lcb, ucb, committeeSize, goal, True
        )
        search_counter = 0
        while True:
            search_counter = search_counter + 1
            m.update()
            print_if_verbose(f"Getting {search_counter} committee")
            m.optimize()
            if not m.Status == GRB.OPTIMAL:
                log_computation_end(search_counter, failed=True)
                return False, None
            else:
                committee = []
                committeeVars = []
                for candId in candidates:
                    candVar = m.getVarByName(
                        "{}[{}]".format(CANDIDATE_VARIABLE_NAME, candId)
                    )
                    if int(round(candVar.X, 0)) == 1:
                        committee.append(candId)
                        committeeVars.append(candVar)
                logger.debug(f"Checking commitee {committee} for EJR/PJR")
                votersAsBinaryMatr = isxJRChecker.appListsProfilesToBinaryMatrix(
                    voters.values(), candidates
                )
                print_if_verbose(
                    f"Checking {search_counter} committee\t\t"
                    f"Constraints {m.getAttr('NumConstrs')}"
                )
                xjr_check = xJRCheckers[whatToCompute](
                    votersAsBinaryMatr, committee, committeeSize, pjr_ejr_relevant_cands
                )
                # DIRTY HACK --- because the function above can return either a tuple or only True/False
                unhappy_group = None
                if isinstance(xjr_check, tuple):
                    check_ok = xjr_check[0]
                    unhappy_group = xjr_check[1]
                    failing_ell = xjr_check[2]
                else:
                    check_ok = xjr_check

                if check_ok:
                    cov_var = m.getVarByName(COVERAGE_VARIABLE_NAME)
                    app_var = m.getVarByName(APPROVAL_VARIABLE_NAME)
                    log_computation_end(search_counter, failed=False)
                    print_if_verbose("")
                    return (
                        True,
                        int(m.objVal),
                        int(round(cov_var.X, 0)),
                        int(round(app_var.X, 0)),
                    )

                m.addConstr(quicksum(committeeVars) <= len(committeeVars) - 1)

                if unhappy_group is not None and (whatToCompute == COMPUTE_PJR):
                    approvals_union = set()
                    for curr_voter in unhappy_group:
                        approvals_union = approvals_union.union(set(voters[curr_voter]))
                    union_var = m.addVar(vtype=GRB.INTEGER, lb=0)
                    m.addGenConstrNorm(
                        union_var, [candidate_vars[i] for i in approvals_union], 1
                    )
                    m.addConstr(union_var >= failing_ell)

                # We ensure that the enumeration takes into consideration the just found unhappy group
                if unhappy_group is not None and (whatToCompute == COMPUTE_EJR):
                    logger.debug("Unhappy groups discovered for EJR!")
                    per_voter_vars = []
                    for curr_voter in unhappy_group:
                        curr_approvals = voters[curr_voter]
                        logger.debug(
                            f"Unhappy voter {curr_voter} approvals: {curr_approvals}"
                        )
                        if len(curr_approvals) < failing_ell:
                            continue
                        norm_var = m.addVar(vtype=GRB.INTEGER, lb=0)
                        m.addGenConstrNorm(
                            norm_var, [candidate_vars[i] for i in curr_approvals], 1
                        )
                        per_voter_vars.append(norm_var)
                    max_var = m.addVar(vtype=GRB.INTEGER, lb=0)
                    m.addGenConstrMax(max_var, per_voter_vars)
                    m.addConstr(max_var >= failing_ell)

                print_if_verbose(f"Missed committees = {search_counter}")
    except GurobiError as e:
        print("Gurobi Error reported: " + str(e))
    except Exception as e:
        print("Error reported: " + str(e))
