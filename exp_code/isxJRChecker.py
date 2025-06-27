#!/usr/bin/python3

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

from pulp import *
import math
import core.mylog as mylog

logger = mylog.get_logger()


def appListToBinaryVector(voter, candidates):
    v = [1 if c in voter else 0 for c in candidates]
    return v


def appListsProfilesToBinaryMatrix(voters, candidates):
    return [appListToBinaryVector(voter, candidates) for voter in voters]


def mostPopular(V):
    m = len(V[0])
    n = len(V)
    M = 0
    M_c = -1
    for c in range(m):
        count = sum([V[i][c] for i in range(n)])
        if count > M:
            M = count
            M_c = c
    return (M_c, M)


def removeVoters(V, c):
    Vnew = []
    for v in V:
        if v[c] == 0:
            Vnew += [v]
    return Vnew


def baseXJR_ilp(V, ell, k, available_candidates=None):
    n = len(V)
    m = len(V[0])

    noverk = n / k
    ### BELOW: there is indeed problem with division
    ### but we take ceiling in our ILP, so I commented
    ### this part out
    # if( noverk * k != n ):
    #  print "Problem with division!"

    model = LpProblem("EJR", LpMinimize)

    X = [LpVariable("x%d" % i, cat="Binary") for i in range(n)]
    Y = [LpVariable("y%d" % j, cat="Binary") for j in range(m)]

    if available_candidates:
        for cand in range(m):
            if cand in available_candidates:
                continue
            model += Y[cand] == 0

    # choose ell*noverk voters
    model += lpSum(X) == math.ceil(ell * noverk)
    # choose ell candidates that will witness cohesiveness
    model += lpSum(Y) == ell

    # ensure all chosen candidates are approved by all selected voters
    for i in range(n):
        for j in range(m):
            model += Y[j] <= V[i][j] + (1 - X[i])

    return (model, X, Y)


def pjr_ilp(V, W, ell, k, available_candidates=None):
    n = len(V)
    (model, X, Y) = baseXJR_ilp(V, ell, k, available_candidates)
    # logger.info(f"k: {k}  ell: {ell}  size(W): {len(W)}")
    WW = [LpVariable("w%d" % j, cat="Binary") for j in range(len(W))]

    for j in range(len(W)):
        for i in range(n):
            model += WW[j] >= X[i] * V[i][W[j]]
        model += WW[j] <= lpSum([X[i] * V[i][W[j]] for i in range(n)])

    model += lpSum(WW) <= ell - 1

    return (model, X, Y)


def isPJR_ilp(V, W, k, available_candidates=None):
    # logger.debug(f"PJR ILP, available candidates: {available_candidates}")
    n = len(V)
    for ell in range(2, k + 1):
        (model, X, Y) = pjr_ilp(V, W, ell, k, available_candidates)
        model.solve(GUROBI(msg=0))
        if model.status == 1:
            unhappy_group = []
            for i in range(n):
                if X[i].value() > 0:
                    unhappy_group.append(i)
            return (False, unhappy_group, ell)
    return True


def ejr_ilp(V, W, ell, k, available_candidates=None):
    n = len(V)
    m = len(V[0])
    (model, X, Y) = baseXJR_ilp(V, ell, k, available_candidates)

    for i in range(n):
        approved = 0
        for j in W:
            approved += V[i][j]
        model += m * (1 - X[i]) >= approved - ell + 1

    return (model, X, Y)


def isEJR_ilp(V, W, k, available_candidates=None):
    # logger.debug(f"EJR ILP, available candidates: {available_candidates}")
    n = len(V)

    for ell in range(1, k + 1):
        #    print "Testing EJR", ell
        (model, X, Y) = ejr_ilp(V, W, ell, k, available_candidates)
        model.solve(GUROBI(msg=0))
        if model.status == 1:
            #      print "NO EJR"

            unhappy_group = []
            for i in range(n):
                if X[i].value() > 0:
                    unhappy_group.append(i)

            return (
                False,
                unhappy_group,
                ell,
            )  # comment out for the ILP to provide explanation about failing EJR

            print("ILP STATUS = " + LpStatus[model.status])

            m = len(V[0])
            for j in range(m):
                if Y[j].value() > 0:
                    print("Witnessing candidate: {}, {}".format(j, Y[j].value()))

            for i in range(n):
                if X[i].value() > 0:
                    s = "voter %d: " % i
                    for j in range(m):
                        if Y[j].value() > 0:
                            s += "c%d: %d  " % (j, V[i][j])
                    print(s)

            S = []
            for i in range(n):
                if X[i].value() > 0:
                    s = ""
                    for j in W:
                        s += "V[%d][%d] = %d  " % (i, j, V[i][j])
                    print(s)
                    S += [i]
            print(f"Failing voters: {S}")
            print(f"W: {W}")
            print(f"ell: {ell}")

            return (False, unhappy_group, ell)

    #  print "is EJR"
    return (True, [], 0)


def isJR(V, W):
    n = len(V)
    k = len(W)
    for c in W:
        V = removeVoters(V, c)

    if len(V) == 0:
        return True

    (c, M) = mostPopular(V)
    if M >= float(n) / float(k):
        return False
    return True


def xJRChecking(V, W):
    """This functions checks whether a committee is ERJ, PJR, and JR.
    It returns a boolean-valued triplet (JR, EJR, PJR) where an entry
    is True when the committee meets a respeective xJR"""
    JRFlag = isJR(V, W)
    if not JRFlag:
        return (False, False, False)
    A = isEJR_ilp(V, W, len(W))
    if A:
        return (True, True, True)
    A = isPJR_ilp(V, W, len(W))
    if A:
        return (True, True, False)
    return (True, False, False)
