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


class Candidate(object):
    """Every candidate has a number and, optionally, a name"""

    def __init__(self, ordinal_number, name=""):
        self._name = name
        self._ordinal_number = ordinal_number

    @property
    def ordinal_number(self):
        return self._ordinal_number

    def __str__(self):
        return str(self.ordinal_number) + "" if self._name == "" else f" ({self._name})"

    def __repr__(self):
        return str(self.ordinal_number)


class Candidates(object):
    """Collection of candidates. The main reason to have it is to be sure that the
    ordinal numbers of the candidates are different, consecutive, and starting
    from 0"""

    def __init__(self, candidates_list):
        if not self._check_validity(candidates_list):
            raise ValueError(
                "Provided candidates do not have consecutive integer "
                "indices starting from 0"
            )
        self._candidates_list = sorted(
            candidates_list, key=lambda cand: cand.ordinal_number
        )

    def candidate_exists(self, candidate_index):
        return candidate_index in set((c.ordinal_number for c in self._candidates_list))

    def __len__(self):
        return len(self._candidates_list)

    def __getitem__(self, index):
        return self._candidates_list[index]

    def _check_validity(self, candidates_list):
        ordinal_numbers = sorted([c.ordinal_number for c in candidates_list])
        truth_table = [
            ord_num_index_pair[0] == ord_num_index_pair[1]
            for ord_num_index_pair in enumerate(ordinal_numbers)
        ]
        return reduce(lambda acc, x: acc and x, truth_table, True)

    def __str__(self):
        return ", ".join(map(str, self._candidates_list))
