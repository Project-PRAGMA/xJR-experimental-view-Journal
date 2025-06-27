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

import random
import math
import csv

import core.mylog as mylog

logger = mylog.get_logger()
import discore
import elections
import candidates as cands


class PreflibElectionBasedDistribution(discore.Distribution):
    def __init__(self, base_election_path):
        self._base_election_path = base_election_path
        self._candidates = []

    def generate(self, votes_count, candidates=None):
        if candidates:
            raise ValueError(
                f"Distribution {self.get_description()} cannot take a "
                "list of candidates to base on"
            )
        election_candidates_raw, all_votes = self._parsePreflibElections()
        votes = []
        if len(all_votes) < votes_count:
            raise ValueError(f"Too small elections to draw {votes_count} votes")
        for vote in random.sample(all_votes, votes_count):
            votes.append(elections.ApprovalPreference(set(vote)))

        candidates = [cands.Candidate(c) for c in election_candidates_raw]
        candidates = cands.Candidates(candidates)
        return elections.ApprovalElection(votes, candidates)

    def get_description(self):
        return f"Preflib based distribution from: {self._base_election_path}"

    def _parsePreflibElections(self):
        cand_name_id = {}
        votes = []
        with open(
            self._base_election_path, "r", newline="", encoding="utf-8"
        ) as electionFile:
            line_counter = 0
            votes = []
            candidates = []
            for line in (line.strip() for line in electionFile if not line[0] == "#"):
                line_counter += 1
                if line_counter == 1:
                    candidates_count = int(line)
                    continue
                if line_counter <= candidates_count + 1:
                    candidates.append(int(line.split(",")[0]))
                    continue
                if line_counter == candidates_count + 2:
                    unique_rankings = int(line.split(",")[2].strip())
                    continue
                copies, ranking = line.split(", {")
                ranking = list(eval("{" + ranking))
                ranking = [int(r) for r in ranking]
                for _ in range(int(copies)):
                    votes.append(ranking[:])
        return candidates, votes


class PabulibElectionBasedDistribution(discore.Distribution):

    def __init__(self, baseElectionPath, draw_candidates=False):
        self._baseElectionPath = baseElectionPath
        self._draw_candidates = draw_candidates

    def generate(self, votesCount, candidates=None):
        election_candidates_raw, allVotes = self._parsePabulibElections()

        votes = []
        if len(allVotes) < votesCount:
            raise ValueError(f"Too small elections to draw {votesCount} votes")
        raw_votes = list(random.sample(allVotes, votesCount))

        candidates_to_remain = sorted(election_candidates_raw)
        if self._draw_candidates:
            if not candidates:
                logger.error(
                    "Expected drawing candidates but the number of cands not provided."
                )
                assert False
            random.shuffle(candidates_to_remain)
            candidates_to_remain = candidates_to_remain[:candidates]
        candidates_mapping = dict(
            list(map(lambda t: (t[1], t[0]), enumerate(candidates_to_remain)))
        )
        for vote in raw_votes:
            transformed_vote = set(
                [
                    candidates_mapping[app]
                    for app in vote
                    if app in candidates_mapping.keys()
                ]
            )
            votes.append(elections.ApprovalPreference(transformed_vote))

        considered_cands = [cands.Candidate(c) for c in candidates_mapping.values()]
        considered_cands = cands.Candidates(considered_cands)

        return elections.ApprovalElection(votes, considered_cands)

    def get_description(self):
        return f"Pabulib based distribution from: {self._baseElectionPath}"

    def get_short_description(self):
        return f"Pabulib: {self._baseElectionPath} 0 commsize: NA"
        "remprob NA"

    def _parsePabulibElections(self):
        cand_name_id = {}
        votes = []
        with open(self._baseElectionPath, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            for row in reader:
                if str(row[0]).strip().lower() in ["meta", "projects", "votes"]:
                    section = str(row[0]).strip().lower()
                    header = next(reader)
                elif section == "meta":
                    pass
                elif section == "projects":
                    cand_name_id[row[0]] = len(cand_name_id)
                elif section == "votes":
                    try:
                        vote_index = header.index("vote")
                    except ValueError:
                        vote_index = header.index("votes")
                    vote = row[vote_index].strip().split(",")
                    votes.append([cand_name_id[cand] for cand in vote])
        return sorted(cand_name_id.values()), votes


class PabulibElectionCompositeDistribution(discore.Distribution):
    def __init__(self, pabulib_election_distros, name="default"):
        self._pabulib_election_distros = pabulib_election_distros
        self._name = name

    def generate(self, votesCount, candidates=None):
        """Right now candidatesCount is ignored"""
        selected_distro = random.choice(self._pabulib_election_distros)
        return selected_distro.generate(votesCount, candidates)

    def get_description(self):
        return f"Pabulib based compositional distribution '{self._name}'"

    def get_short_description(self):
        return f"Pabulib compositional '{self._name}'"


class GaussianMixture1D(discore.ParameterizedDistribution):

    def _get_required_parameters(self):
        return ["probabilities", "centers", "standard_deviations", "approval_radius"]

    def __init__(self, distribution_parameters):
        super().__init__(distribution_parameters)
        assert len(self._probabilities) == len(self._centers)
        assert len(self._probabilities) == len(self._standard_deviations)
        assert math.isclose(sum(self._probabilities), 1.0)
        self._probabilities_intervals = [0]
        for c_prob in self._probabilities:
            self._probabilities_intervals.append(
                self._probabilities_intervals[-1] + c_prob
            )
        self._probabilities_intervals = self._probabilities_intervals[1:-1] + [1.0]

    def generate(self, candidates, votersnr):
        candidates_positions = [random.uniform(0, 1) for _ in range(len(candidates))]
        probs_intervals = []
        voters_positions = []
        for i in range(votersnr):
            gauss_selection_var = random.uniform(0, 1)
            center_index = 0
            for upper_bound in self._probabilities_intervals:
                if gauss_selection_var > upper_bound:
                    center_index += 1
                break
            center = self._centers[center_index]
            stdev = self._standard_deviations[center_index]
            voters_positions.append(max(0, min(random.gauss(center, stdev), 1)))
        votes = []
        for i in range(votersnr):
            vote = set()
            maxApproved = voters_positions[i] + self._approval_radius
            minApproved = voters_positions[i] - self._approval_radius
            for c in range(len(candidates)):
                if (
                    candidates_positions[c] <= maxApproved
                    and candidates_positions[c] >= minApproved
                ):
                    vote.add(c)
            votes.append(vote)
        votes = [elections.ApprovalPreference(vote) for vote in votes]
        candidates = [cands.Candidate(c) for c in candidates]
        candidates = cands.Candidates(candidates)
        return elections.ApprovalElection(votes, candidates)

    def get_description(self):
        probs, cents, stds = self._format_params()
        outstring = f"{round(self._approval_radius, 3)}-1D-Gauss: probabilities:{probs} centers:{cents}"
        f"standard deviations:{stds}"
        return outstring

    def get_short_description(self):
        probs, cents, stds = self._format_params()
        return (
            f"{round(self._approval_radius, 3)}-1D-G:_pr:{probs}_c:{cents}_stds:{stds}"
        )

    def _format_params(self):
        def round_n_str(x):
            return str(round(x, 2))

        probs = "/".join(map(round_n_str, self._probabilities))
        cents = "/".join(map(round_n_str, self._centers))
        stds = "/".join(map(round_n_str, self._standard_deviations))
        return probs, cents, stds


class ImpartialCulture(discore.ParameterizedDistribution):
    def _get_required_parameters(self):
        return ["approval_probability"]

    def __init__(self, distribution_parameters):
        super().__init__(distribution_parameters)

    def generate(self, candidates, votersnr):
        votes = []
        for i in range(votersnr):
            vote = set()
            for c in candidates:
                if random.random() < self._approval_probability:
                    vote.add(c)
            votes.append(vote)
        votes = [elections.ApprovalPreference(vote) for vote in votes]
        candidates = [cands.Candidate(c) for c in candidates]
        candidates = cands.Candidates(candidates)
        return elections.ApprovalElection(votes, candidates)

    def get_description(self):
        return "Impartial, probability: {}".format(round(self._approval_probability, 4))

    def get_short_description(self):
        return f"IC: {round(self._approval_probability, 4)}"


class OneDDistribution(discore.ParameterizedDistribution):
    def _get_required_parameters(self):
        return ["approval_radius"]

    def __init__(self, distribution_parameters):
        super().__init__(distribution_parameters)

    def generate(self, candidates, votersnr):
        votersPositions = []
        candidatesPositions = []
        for i in range(votersnr):
            votersPositions.append(random.uniform(0, 1))
        for i in range(len(candidates)):
            candidatesPositions.append(random.uniform(0, 1))
        votes = []
        for i in range(votersnr):
            vote = set()
            maxApproved = votersPositions[i] + self._approval_radius
            minApproved = votersPositions[i] - self._approval_radius
            for c in range(len(candidates)):
                if (
                    candidatesPositions[c] <= maxApproved
                    and candidatesPositions[c] >= minApproved
                ):
                    vote.add(c)
            votes.append(vote)
        votes = [elections.ApprovalPreference(vote) for vote in votes]
        candidates = [cands.Candidate(c) for c in candidates]
        candidates = cands.Candidates(candidates)
        return elections.ApprovalElection(votes, candidates)

    def get_description(self):
        return "1D, radius: {}".format(round(self._approval_radius, 4))

    def get_short_description(self):
        return f"1D: {self._approval_radius}"


class TwoDDistribution(discore.ParameterizedDistribution):
    def _get_required_parameters(self):
        return ["approval_radius"]

    def __init__(self, distribution_parameters):
        super().__init__(distribution_parameters)

    def generate(self, candidates, votersnr):
        votersPositions = []
        candidatesPositions = []
        for i in range(votersnr):
            votersPositions.append((random.uniform(0, 1), random.uniform(0, 1)))
        for i in range(len(candidates)):
            candidatesPositions.append((random.uniform(0, 1), random.uniform(0, 1)))
        votes = []
        for i in range(votersnr):
            vote = set()
            vx = votersPositions[i][0]
            vy = votersPositions[i][1]
            for c in range(len(candidates)):
                cx = candidatesPositions[c][0]
                cy = candidatesPositions[c][1]
                if math.hypot(vx - cx, vy - cy) <= self._approval_radius:
                    vote.add(c)
            votes.append(vote)
        votes = [elections.ApprovalPreference(vote) for vote in votes]
        candidates = [cands.Candidate(c) for c in candidates]
        candidates = cands.Candidates(candidates)
        return elections.ApprovalElection(votes, candidates)

    def get_description(self):
        return "2D, radius: {}".format(round(self._approval_radius, 4))

    def get_short_description(self):
        return f"2D: {self._approval_radius}"


class LineVotersDistribution(discore.ParameterizedDistribution):
    def _get_required_parameters(self):
        return [
            "groups_count",
            "candidates",
            "overlapping_ratio",
            "votes_count",
            "voter_group_probabilities",
        ]

    def __init__(self, distribution_parameters):
        super().__init__(distribution_parameters)
        if len(self._candidates) % self._groups_count != 0:
            raise ValueError(
                "Number of groups does not divide the number of " "candidates"
            )
        if len(self._voter_group_probabilities) != self._votes_count:
            raise ValueError(
                "Probability map size does not match the requested " "vote count"
            )
        for group_probabilities in self._voter_group_probabilities:
            if len(group_probabilities) != self._groups_count:
                raise ValueError(
                    "Probability map size does not match the requested "
                    "number of groups"
                )
        if self._overlapping_ratio < 0 or self._overlapping_ratio > 1:
            raise ValueError(
                "Overlapping ratio must be between 0 and 1, both ends " "inclusive"
            )
        candidates_per_group = len(self._candidates) / self._groups_count
        group_border_jump = int((1.0 - self._overlapping_ratio) * candidates_per_group)
        self._groups = []
        for group_index in range(self._groups_count):
            start_index = group_index * group_border_jump
            end_index = start_index + group_border_jump
            self._groups.append(
                [c.ordinal_number for c in self._candidates[start_index:end_index]]
            )

    def generate(self, votes_count, candidates=None):
        """The current implementation totally ignores the given parameters because
        the distibution needs them from the very beginning"""
        votes = []
        for voter_index in range(self._votes_count):
            approvals = set()
            for group_index in range(self._groups_count):
                drew = random.random()
                if drew <= self._voter_group_probabilities[voter_index][group_index]:
                    approvals.update(self._groups[group_index])
            votes.append(approvals)
        votes = [elections.ApprovalPreference(vote) for vote in votes]
        return elections.ApprovalElection(votes, self._candidates)

    def get_description(self):
        return f"Line voters distribution, parameters: {str(self._parameters)}"

    def get_short_description(self):
        return f"Line voters, groups:  {self._groups_count}"


class PartyListWithCoreLinRemainder(discore.ParameterizedDistribution):
    def _get_required_parameters(self):
        return [
            "parties_count",
            "committee_size",
            "remaining_prob",
            "min_cand_count",
            "min_votes_count",
        ]

    def __init__(self, distribution_parameters):
        super().__init__(distribution_parameters)
        self._inner_distribution = self._compute_valid_line_voters_distribution(
            self._parties_count, self._committee_size, self._remaining_prob
        )

    def generate(self, votes_count, candidates=None):
        """The current implementation totally ignores the given parameters because
        the distibution needs them from the very beginning"""
        return self._inner_distribution.generate(votes_count, candidates)

    def get_description(self):
        return (
            f"Party list with core distribution\nparameters:\n{str(self._parameters)}"
        )

    def get_short_description(self):
        return f"PLwC parties: {self._parties_count} commsize: {self._committee_size} \
    remprob {self._remaining_prob}"

    def _compute_valid_line_voters_distribution(
        self, parties_count, committee_size, remaining_prob
    ):

        cand_count = math.ceil(self._min_cand_count / parties_count) * parties_count
        candidates_per_party = int(cand_count / parties_count)

        voters_count = math.ceil(self._min_votes_count / parties_count) * parties_count
        voters_per_party = int(voters_count / parties_count)

        one_large_size = int(voters_count / committee_size)

        party_size = int(cand_count / parties_count)

        max_cohesive_group_size = int(party_size / one_large_size)

        core_in_party_size = max_cohesive_group_size

        voter_per_parties_borders = zip(
            range(0, voters_count, voters_per_party),
            range(voters_per_party, voters_count + 1, voters_per_party),
        )

        candidates_per_parties_borders = list(
            zip(
                range(0, self._min_cand_count, candidates_per_party),
                range(candidates_per_party, cand_count + 1, candidates_per_party),
            )
        )

        voters_to_cands_mapping = zip(
            voter_per_parties_borders, candidates_per_parties_borders
        )

        candidates_probabilities = []
        for voter_index in range(voters_count):
            supp_candidates_borders = candidates_per_parties_borders[
                int(voter_index / voters_per_party)
            ]
            supp_candidates = set(
                range(supp_candidates_borders[0], supp_candidates_borders[1])
            )
            party_approval_pattern = [
                int(c in supp_candidates) for c in range(cand_count)
            ]
            remaining_candidates_count = party_size - core_in_party_size
            for i in range(core_in_party_size, party_size):
                remaining_candidate_number = i - core_in_party_size

                lin_probability_coeff = (
                    remaining_candidates_count - remaining_candidate_number
                ) / remaining_candidates_count

                sqrt_probability_coeff = math.sqrt(lin_probability_coeff)
                sq_probability_coeff = 1 - math.pow(lin_probability_coeff, 2)
                cub_probability_coeff = 1 - math.pow(lin_probability_coeff, 3)
                fourth_probability_coeff = 1 - math.pow(lin_probability_coeff, 3)

                # probability_coeff = lin_probability_coeff
                # probability_coeff = cub_probability_coeff
                probability_coeff = fourth_probability_coeff

                # 2#probability_coeff = 1
                # 3#probability_coeff = (remaining_candidates_count - \
                # 3#(remaining_candidate_number/2))/remaining_candidates_count
                party_approval_pattern[i + supp_candidates_borders[0]] = (
                    probability_coeff * remaining_prob
                )
            candidates_probabilities.append(party_approval_pattern)

        candidates = [cands.Candidate(c) for c in range(cand_count)]
        candidates = cands.Candidates(candidates)
        return LineVotersDistribution(
            discore.DistributionParameters(
                candidates=candidates,
                overlapping_ratio=0,
                groups_count=cand_count,
                votes_count=voters_count,
                voter_group_probabilities=candidates_probabilities,
            )
        )
