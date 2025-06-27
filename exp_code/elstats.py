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

import core.mylog

logger = core.mylog.get_logger()
import core.baseProgram as baseProgram
from core.baseProgram import (
    APPROVAL_MAX,
    APPROVAL_MIN,
    COVERAGE_MAX,
    COVERAGE_MIN,
    CORE_MIN,
)


def dummyStats(cands, voters, commSize):
    logger.debug("Using dummy stats")
    stats = Statistics(cands, voters, commSize)
    stats.avgApp = 26.17
    stats.maxApp = 805
    stats.maxJRApp = 133
    stats.minApp = 100
    stats.minJRApp = 64
    stats.maxCov = 805
    stats.maxJRCov = 139
    stats.minCov = 100
    stats.minJRCov = 87
    stats.justifiedCore = 2
    return stats


class Statistics(object):

    def __init__(self, candidates, voters, committeeSize):
        self.avgApp = None
        self.maxApp = None
        self.maxJRApp = None
        self.minApp = None
        self.minJRApp = None
        self.maxCov = None
        self.maxJRCov = None
        self.minCov = None
        self.minJRCov = None
        self.justifiedCore = None
        self.candidatesNr = len(candidates)
        self.candidates = candidates
        self.votersNr = len(voters)
        self.voters = voters
        self.committeeSize = committeeSize

    def _computeHelper(self, goal, requireJR):
        compute_result = baseProgram.compute(
            self.candidates,
            self.voters,
            0,
            self.votersNr * self.candidatesNr,
            0,
            self.votersNr,
            self.committeeSize,
            goal,
            requireJR,
        )
        return compute_result[0], compute_result[1]

    def show(self, outFile):
        # formatStrings = [
        #     "Avg approvals by each voter: {}\n",
        #     "Max approval: {}\n",
        #     "Min approval: {}\n",
        #     "Max coverage: {}\n",
        #     "Min coverage: {}\n",
        #     "Max JR approval: {}\n",
        #     "Min JR approval: {}\n",
        #     "Max JR coverage: {}\n",
        #     "Min JR coverage: {}\n",
        #     "Justified Core: {}\n",
        #     ]
        # statisticsDataOrdered = [
        #     self.avgApp,
        #     self.maxApp,
        #     self.minApp,
        #     self.maxCov,
        #     self.minCov,
        #     self.maxJRApp,
        #     self.minJRApp,
        #     self.maxJRCov,
        #     self.minJRCov,
        #     self.justifiedCore
        #     ]
        # for formatString, value in zip(formatStrings, statisticsDataOrdered):
        outFile.write(str(self))

    def __str__(self):
        fieldsInStrings = [
            f"Avg approvals by each voter: {self.avgApp}\n",
            f"Max approval: {self.maxApp}\n",
            f"Min approval: {self.minApp}\n",
            f"Max coverage: {self.maxCov}\n",
            f"Min coverage: {self.minCov}\n",
            f"Max JR approval: {self.maxJRApp}\n",
            f"Min JR approval: {self.minJRApp}\n",
            f"Max JR coverage: {self.maxJRCov}\n",
            f"Min JR coverage: {self.minJRCov}\n",
            f"Justified Core: {self.justifiedCore}\n",
        ]
        return "".join(fieldsInStrings)

    def compute(self):
        self.avgApp = (
            float(sum([len(vot.approvals) for vot in self.voters])) / self.votersNr
        )
        success, self.maxApp = self._computeHelper(APPROVAL_MAX, False)
        success, self.minApp = self._computeHelper(APPROVAL_MIN, False)
        success, self.maxCov = self._computeHelper(COVERAGE_MAX, False)
        success, self.minCov = self._computeHelper(COVERAGE_MIN, False)
        success, self.maxJRApp = self._computeHelper(APPROVAL_MAX, True)
        success, self.minJRApp = self._computeHelper(APPROVAL_MIN, True)
        success, self.maxJRCov = self._computeHelper(COVERAGE_MAX, True)
        success, self.minJRCov = self._computeHelper(COVERAGE_MIN, True)
        success, self.justifiedCore = self._computeHelper(CORE_MIN, True)
