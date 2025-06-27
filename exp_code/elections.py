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

from functools import reduce


class ApprovalPreference(object):
    """A single approval preference"""

    def __init__(self, approvals):
        if not isinstance(approvals, set):
            raise ValueError("Approved candidates must be represented by a set")
        self._approvals = approvals

    def validate(self, candidates):
        approved_candidate_existence = [
            candidates.candidate_exists(c) for c in self._approvals
        ]
        return reduce(lambda acc, x: acc and x, approved_candidate_existence, True)

    def get_binary_representation(self, candidates):
        binary_vote = [
            1 if c.ordinal_number in self._approvals else 0 for c in candidates
        ]
        return binary_vote

    def approves_all_of(self, candidates):
        return len(set(candidates) & self.approvals) == len(candidates)

    @property
    def approvals(self):
        return set(self._approvals)

    def __str__(self):
        return "{" + ", ".join(map(str, sorted(self._approvals))) + "}"

    def __iter__(self):
        return iter(self._approvals)


class ApprovalElection(object):
    """Single, immutable, approval-validated approval election"""

    def __init__(self, votes, candidates):
        self._candidates = candidates
        for vote in votes:
            if not vote.validate(self._candidates):
                raise ValueError(
                    "There is a vote that approves a nonexistent candidate"
                )
        self._votes = votes

    @property
    def votes(self):
        return self._votes[:]

    @property
    def candidates(self):
        return self._candidates[:]

    def get_binary_representation(self):
        return [vote.get_binary_representation(self.candidates) for vote in self.votes]

    def get_candidate_support_map(self):
        candidates_support = {}
        ordered_voters = list(enumerate(self.votes))
        for c in self.candidates:
            candidates_support[c.ordinal_number] = set(
                [
                    ord_vot[0]
                    for ord_vot in ordered_voters
                    if (c.ordinal_number in ord_vot[1])
                ]
            )
        return candidates_support

    def get_vote(self, vote_id):
        return self._votes[vote_id]

    def __str__(self):
        first_line = (
            f"Election with {len(self._candidates)} "
            + f"candidates\n{self._candidates}\nand {len(self._votes)} voters\n"
        )
        second_line = "\n".join(map(str, self._votes))
        return first_line + second_line
