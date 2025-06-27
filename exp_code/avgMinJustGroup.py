#!/usr/bin/env -S python3  -u

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

import traceback
import random
from numpy import mean
from itertools import *

# from distributions import UrnModel, MallowsModel, PabulibElectionBasedDistribution, PreflibElectionBasedDistribution, PabulibElectionBasedDistribution
import argparse
import os
import core.baseProgram as baseProgram
import csv
from pathlib import Path
import multiprocessing as mproc
import signal
import sys
import math
import enum
import logging
from functools import reduce

import candidates as cands
import distribs
import discore
from distribs import (
    OneDDistribution,
    TwoDDistribution,
    ImpartialCulture,
    GaussianMixture1D,
)
import isxJRChecker as xJRTools
import core.mylog as mylog

logger = mylog.get_logger()
import lcgroups
import tools.pblib as pbtools


class Axioms(enum.Enum):
    JR = "JR"
    PJR = "PJR"
    EJR = "EJR"


class CsvHeaders(enum.Enum):
    MODEL = "Model"
    PARAM1 = "Model Parameterization1"
    PARAM2 = "Model Parameterization2"
    COMM_SIZE = "Committee Size"
    MIN_JR_JG = "Minimum JR Just. Group"
    MIN_PJR_JG = "Minimum PJR Just. Group"
    MIN_EJR_JG = "Minimum EJR Just. Group"


def experiment_trial(
    distribution,
    committee_size,
    voters_count,
    trials,
    requested_axioms,
    trials_seed,
    candidates_count,
    elections_from_file,
):
    random.seed(trials_seed)
    logger.info(
        f"Started computing --> k: {committee_size}, trials count:"
        f" {trials}, seed: {trials_seed}"
    )
    jg_sizes_per_comm_size = {}
    try:
        jrcsizes = []
        report_step = max(1, trials // 4)
        for trial_nr, _ in enumerate(range(trials)):
            logger_msg = f"Comm. size {committee_size}, tr. {trial_nr + 1}/{trials}"
            if elections_from_file:
                long_desc = distribution.get_description()
                short_desc = long_desc[long_desc.rfind("/") + 1 :]
            else:
                short_desc = distribution[1]
            logger_msg += f" ({short_desc})"
            if trial_nr % report_step == 0:
                logger.info(logger_msg)
            if elections_from_file:
                election = distribution.generate(voters_count)
            else:
                election = distribution[0].generate(
                    range(candidates_count), voters_count
                )
            jrcsizes.append(
                compute_minimum_xjr_justifying_group(
                    election, committee_size, requested_axioms
                )
            )
        jg_sizes_per_comm_size[committee_size] = jrcsizes
    except Exception as e:
        logger.error(traceback.format_exc().strip())
        raise
    return jg_sizes_per_comm_size


def write_to_file(outfilename, distribution, jg_sizes_per_comm_size):
    def to_int_or_None(val):
        return int(val) if (val is not None) else None

    short_desc = (
        distribution[1]
        if isinstance(distribution, tuple)
        else distribution.get_short_description()
    )
    with open(outfilename, "a", newline="") as outfile:
        writer = build_csv_writer(outfile)
        for committeesize, jrcsizes in jg_sizes_per_comm_size.items():
            for jr_min_jg, pjr_min_jg, ejr_min_jg in jrcsizes:
                writer.writerow(
                    {
                        CsvHeaders.MODEL.value: short_desc,
                        CsvHeaders.PARAM1.value: None,  # distribution.parameters()[0],
                        CsvHeaders.PARAM2.value: None,  # distribution.parameters()[1],
                        CsvHeaders.COMM_SIZE.value: committeesize,
                        CsvHeaders.MIN_JR_JG.value: to_int_or_None(jr_min_jg),
                        CsvHeaders.MIN_PJR_JG.value: to_int_or_None(pjr_min_jg),
                        CsvHeaders.MIN_EJR_JG.value: to_int_or_None(ejr_min_jg),
                    }
                )


def report_failure(distribution, exception):
    logger.error(f" skipped due to {exception}")


class initializer(object):
    def __call__(self, *args, **kwargs):
        if sys.platform == "win32":
            import win32api  # ignoring the signal

            win32api.setconsolectrlhandler(none, true)


__distributions_collection = {
    "1D": (
        OneDDistribution(discore.DistributionParameters(approval_radius=0.06)),
        "1D-0.06",
        111111111111111111,
    ),
    "2D": (
        TwoDDistribution(discore.DistributionParameters(approval_radius=0.2)),
        "2D-0.02",
        111111111111111129,
    ),
    "IC": (
        ImpartialCulture(discore.DistributionParameters(approval_probability=0.1)),
        "IC-0.1",
        0,
    ),
    "GA": (
        GaussianMixture1D(
            discore.DistributionParameters(
                probabilities=(1, 0, 0),
                centers=(0.5, 0, 0),
                standard_deviations=(0.1, 0, 0),
                approval_radius=0.05,
            )
        ),
        "Gaussian",
        1002,
    ),
}


def main(args):
    logger.setLevel(logging.INFO)
    random.seed(args.seed)

    outfilename = args.outputFile

    axioms_to_compute = set()
    for axiom in args.axioms:
        axioms_to_compute.add(eval(f"Axioms.{axiom}"))
    logger.info(axioms_to_compute)
    seedsperdistro = int(args.trialsCount)
    max_poolsize = int(args.processesCount)
    logger.info(f"Trials: {seedsperdistro}")
    logger.info(f"Max processes: {max_poolsize}")

    elections_from_pabulib = args.elections_directory != None
    if elections_from_pabulib:
        print(f"Distributions from: {args.elections_directory}")
        distros = pbtools.get_election_based_distributions(
            args.elections_directory, args.ignoredFiles
        )
    else:
        distros = [__distributions_collection[args.distribution]]

    candidatesnr = args.candidates_count
    votersnr = args.voters_count

    committeesizes = range(2, 16)

    write_csv_header(outfilename)

    def parallel_run():

        total_trials = len(distros) * len(committeesizes) * seedsperdistro
        trials_per_process = 12
        poolsize = min(max_poolsize, int(total_trials / trials_per_process))

        def get_short_desc(distribution):
            short_desc = (
                distribution[1]
                if isinstance(distribution, tuple)
                else distribution.get_short_description()
            )
            return short_desc

        logger.info("\n".join([get_short_desc(d) for d in distros]))

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

        pool = mproc.Pool(processes=poolsize, initializer=initializer())

        def terminatepool(*args, **kwargs):
            pool.terminate()
            exit(1)

        if sys.platform == "win32":
            import win32api

            win32api.setconsolectrlhandler(terminatepool, true)
        else:
            signal.signal(signal.SIGINT, terminatepool)

        trials_per_process_division = 8
        trials_batch = seedsperdistro // trials_per_process_division

        for distro in distros:
            logger.info(f"Adding tasks for distro: {distro}")
            for comm_size in committeesizes:
                logger.info(f" Adding tasks for committee size: {comm_size}")
                counter = 0
                while counter < seedsperdistro:
                    curr_trials_batch = counter
                    counter = min(counter + trials_batch, seedsperdistro)
                    curr_trials_batch = counter - curr_trials_batch
                    logger.info(f"  Adding tasks for trials count: {curr_trials_batch}")
                    pool.apply_async(
                        experiment_trial,
                        (
                            distro,
                            comm_size,
                            votersnr,
                            curr_trials_batch,
                            axioms_to_compute,
                            random.getrandbits(32),
                            candidatesnr,
                            elections_from_pabulib,
                        ),
                        {},
                        lambda output, distro=distro: write_to_file(
                            outfilename, distro, output
                        ),
                        lambda exception, distro=distro: report_failure(
                            distro, exception
                        ),
                    )

        pool.close()
        pool.join()

    def notparallel_run():
        for distro in distros:
            for comm_size in committeesizes:
                try:
                    output = experiment_trial(
                        distro,
                        comm_size,
                        votersnr,
                        seedsperdistro,
                        axioms_to_compute,
                        random.getrandbits(32),
                        candidatesnr,
                        elections_from_pabulib,
                    )
                    write_to_file(outfilename, distro, output)
                except Exception as e:
                    report_failure(distro, e)

    parallel = max_poolsize > 1
    if parallel:
        parallel_run()
    else:
        notparallel_run()


def getArgumentsParser():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-of", "--outputFile", required=True, help="Output file for experiment data"
    )
    ap.add_argument(
        "-ig",
        "--ignoredFiles",
        required=False,
        help="A path to a" "file with ignored files listed each in a separate line",
    )
    ap.add_argument(
        "-a", "--axioms", nargs="+", choices=[ax.value for ax in Axioms], default=["JR"]
    )
    ap.add_argument(
        "-t",
        "--trialsCount",
        required=True,
        help="Number of " "experiment trials for one distribution",
    )
    ap.add_argument(
        "-pc",
        "--processesCount",
        type=int,
        default=1,
        help="Maximum number of "
        "processess used in parallelization (excluding ILP solvers)",
    )
    ap.add_argument(
        "-n",
        "--voters_count",
        required=True,
        help="Number of " "voters in a single election",
        type=int,
    )
    ap.add_argument(
        "-m",
        "--candidates_count",
        required=True,
        help="Number of " "candidates in a single election",
        type=int,
    )
    ap.add_argument(
        "-ed",
        "--elections_directory",
        required=False,
        help="Directory with election files that should be used as distributions",
    )
    ap.add_argument(
        "-s",
        "--seed",
        required=False,
        help="Seed for the generation and other RNG's operation",
        type=int,
    )
    ap.add_argument(
        "-d", "--distribution", required=True, choices=__distributions_collection.keys()
    )
    return ap


def build_csv_writer(fileHook):
    writer = csv.DictWriter(
        fileHook,
        [
            CsvHeaders.MODEL.value,
            CsvHeaders.PARAM1.value,
            CsvHeaders.PARAM2.value,
            CsvHeaders.COMM_SIZE.value,
            CsvHeaders.MIN_JR_JG.value,
            CsvHeaders.MIN_PJR_JG.value,
            CsvHeaders.MIN_EJR_JG.value,
        ],
    )
    return writer


def write_csv_header(fileName):
    with open(fileName, "w", newline="") as outFile:
        build_csv_writer(outFile).writeheader()


################# TEMP FUNCTIONS ######################
##def large_cohesive_groups_analysis(election, comm_size):
##  cohesive_groups = dict()
##  usable_cands_per_group_size = dict()
##  n_over_k = len(election.votes)/comm_size
##  for group_size in range(1, comm_size + 1):
##    current_usable_cands = set()
##    largeness_threshold = group_size * n_over_k
##    for group_inducing_cands in combinations([c.ordinal_number for c in
##      election.candidates], group_size):
##      supporting_voters = {v for v in election.votes \
##        if len(set(group_inducing_cands) & v.approvals) == group_size}
##      if len(supporting_voters) >= largeness_threshold:
##        cohesive_groups.setdefault(group_size, []).append([v.approvals for v in
##        supporting_voters])
##        max_large_cohesive_group = group_size
##        current_usable_cands |= reduce(lambda acc, v: acc | v.approvals, supporting_voters, set())
##    if len(cohesive_groups) == 0 or max(cohesive_groups.keys()) < group_size:
##      break
##    usable_cands_per_group_size[group_size] = current_usable_cands
##  max_lc_group_size = max(cohesive_groups.keys()) if len(cohesive_groups) > 0 \
##    else 0
##  return (max_lc_group_size, usable_cands_per_group_size, cohesive_groups)
##
##
#####################################################


def build_cand_hints(maximal_lc_groups, comm_size):
    cand_hints = []
    for g_size, groups in (
        entry for entry in maximal_lc_groups.items() if entry[0] > 1
    ):
        for group in groups:
            cand_hints.append((group["approved_by_all_group_members"], g_size))
    return cand_hints


def new_build_cand_hints(all_lc_groups, comm_size):
    cand_hints = []
    for lc_group in all_lc_groups:
        cand_hints.append((lc_group["approved_by_all_group_members"], lc_group["ell"]))
    return cand_hints


def compute_minimum_xjr_justifying_group(election, committee_size, requested_axioms):
    if Axioms.JR not in requested_axioms:
        raise ValueError(
            "Currently, for simplicity, we require JR to be within the "
            "axioms to compute justifying groups"
        )
    # logger.warning(election)

    pjr_requested = Axioms.PJR in requested_axioms
    ejr_requested = Axioms.EJR in requested_axioms

    candidates = election.candidates
    voters = election.votes

    logger.debug(f"Starting LC group analysis")
    lc_groups_data = lcgroups.large_cohesive_groups_analysis(election, committee_size)
    max_lc_group_size = lc_groups_data["max_ell_in_lc_groups"]
    usable_cands_per_g_size = lc_groups_data["usable_cands_per_g_size"]
    maximal_lc_groups = lc_groups_data["maximal_lc_groups"]
    logger.debug(f"#Maximal lc Groups: {len(maximal_lc_groups)}")

    logger.debug(f"Getting Min JR")
    min_jr_just_group = 0
    if max_lc_group_size > 0:
        min_jr_just_group = get_minimum_jr_justifying_group(
            candidates, voters, committee_size
        )
    if (not pjr_requested) and (not ejr_requested):
        return (min_jr_just_group, None, None)
    if max_lc_group_size <= 1:
        return (
            min_jr_just_group,
            min_jr_just_group if pjr_requested else None,
            min_jr_just_group if ejr_requested else None,
        )

        ### logger.debug(f"Extracting all LC groups")
        ### bigger_lc_groups = lcgroups.extract_all_lc_groups(maximal_lc_groups, \
        ###   committee_size, voters, min_ell = 2)
        ### #one_lc_groups = lcgroups.extract_all_lc_groups(maximal_lc_groups, \
        ### #  committee_size, voters, min_ell = 1, max_ell = 1)

        ### logger.debug(f"#at-least-2 lc-groups: {len(bigger_lc_groups)}")
    # for lc_group in bigger_lc_groups:
    #   logger.warning(f"{lc_group}")

    pjr_ejr_relevant_cands = reduce(
        lambda acc, usable: acc | usable,
        [item[1] for item in usable_cands_per_g_size.items() if item[0] > 1],
        set(),
    )
    logger.debug(
        f"All candidates: {len(candidates)}; usable candidates: {len(pjr_ejr_relevant_cands)}"
        f"; Ratio: {int(len(pjr_ejr_relevant_cands)/len(candidates)*100)}%"
    )

    # logger.warning(f"\n{pjr_ejr_relevant_cands}\n{candidates}")

    rel_cand = remove_redundant_candidates(
        # bigger_lc_groups
        # + one_lc_groups
        #                              ,
        map(lambda c: c.ordinal_number, candidates),
        election,
        committee_size,
    )
    logger.debug(
        f"All cands.: {len(candidates)}; relevant candidates: {len(rel_cand)}"
        f"; Ratio: {int(len(rel_cand)/len(candidates)*100)}%"
    )
    # logger.warning(f"\n{rel_cand}")

    min_pjr_just_group = min_ejr_just_group = None
    cand_hints = build_cand_hints(maximal_lc_groups, committee_size)
    # cand_hints = new_build_cand_hints(bigger_lc_groups, committee_size)
    logger.debug(
        "Min. PJR and/or EJR just. groups have to be computed as they're not "
        "equivalent to min. JR just. groups because there are ell-large and "
        f"ell-cohesive groups with ell >= {max_lc_group_size} "
        f"(cand hints: {len(cand_hints)})"
    )
    for expected_group_size in range(min_jr_just_group, committee_size + 1):
        groups = get_all_min_jr_just_groups(
            election,
            committee_size,
            expected_group_size,
            cand_hints,
            verif_cands=rel_cand,
        )
        counter = 0
        for group in groups:
            counter += 1
            binary_profile = election.get_binary_representation()
            if pjr_requested and min_pjr_just_group is None:
                min_pjr_just_group = (
                    expected_group_size
                    if xJRTools.isPJR_ilp(
                        binary_profile, group, committee_size, pjr_ejr_relevant_cands
                    )
                    else None
                )
            if ejr_requested and min_ejr_just_group is None:
                min_ejr_just_group = (
                    expected_group_size
                    if xJRTools.isEJR_ilp(
                        binary_profile, group, committee_size, pjr_ejr_relevant_cands
                    )
                    else None
                )
            if (not ejr_requested or min_ejr_just_group is not None) and (
                not pjr_requested or min_pjr_just_group is not None
            ):
                logger.debug(f"Tried {counter} groups")
                return (min_jr_just_group, min_pjr_just_group, min_ejr_just_group)
    return (min_jr_just_group, min_pjr_just_group, min_ejr_just_group)


def remove_redundant_candidates(
    # all_lc_groups,
    usable_cands,
    election,
    committee_size,
):
    # lc_relevant_voters = reduce(lambda acc, lc_g: acc | set(list(lc_g["voters"]))
    #                            , all_lc_groups, set())
    lc_relevant_voters = set(range(len(election.votes)))
    # logger.warning(f"Init voters: {len(election.votes)}; filtered voters: {len(lc_relevant_voters)}")
    # logger.warning(f"relevant voters: {lc_relevant_voters}")
    usable_cands = set(usable_cands)
    cand_support_map = election.get_candidate_support_map()
    covered_cands = set()
    for cand_a in usable_cands:
        for cand_b in usable_cands:
            if cand_a >= cand_b:
                continue
            cand_a_sup = cand_support_map[cand_a] & lc_relevant_voters
            cand_b_sup = cand_support_map[cand_b] & lc_relevant_voters
            if cand_a_sup - cand_b_sup == set():
                covered_cands.add(cand_a)
            elif cand_b_sup - cand_a_sup == set():
                covered_cands.add(cand_b)
    covered_cands = sorted(
        list(covered_cands),
        key=lambda c: len(cand_support_map[c] & lc_relevant_voters),
        reverse=True,
    )
    # logger.warning(f"Cov candidates: {covered_cands}")
    new_usable_cands = set(usable_cands)
    while covered_cands:
        c = covered_cands.pop()
        coverage_counter = 0
        for other in new_usable_cands:
            if c == other:
                continue
            c_sup = cand_support_map[cand_a] & lc_relevant_voters
            other_sup = cand_support_map[cand_b] & lc_relevant_voters
            if (c_sup - other_sup) == set():
                coverage_counter += 1
        if coverage_counter >= committee_size:
            new_usable_cands.remove(c)
    # logger.warning(f"{len(usable_cands)} --> {len(new_usable_cands)}")
    return new_usable_cands


def get_minimum_jr_justifying_group(candidates, voters, committee_size):
    votersCount = len(voters)
    candidatesCount = len(candidates)
    if isinstance(voters, list):
        voters = dict(
            (index_voter[0], index_voter[1].approvals)
            for index_voter in enumerate(voters)
        )
    if isinstance(candidates, list) and isinstance(candidates[0], cands.Candidate):
        candidates = [c.ordinal_number for c in candidates]
    _, jrcSize, _, _ = baseProgram.compute(
        candidates,
        voters,
        0,
        votersCount * candidatesCount,
        0,
        votersCount,
        committee_size,
        baseProgram.CORE_MIN,
        True,
    )
    return jrcSize


def get_all_min_jr_just_groups(
    election, committee_size, forced_size=None, cand_hints=None, verif_cands=None
):
    """
    cand_hinds is a list of tuples; each tuple consists of a set of
    a set of candidates and a number specifying how many of them have to
    be selected in a final committee
    """
    candidates = election.candidates
    voters = election.votes
    votersCount = len(voters)
    candidatesCount = len(candidates)

    all_combinations = 0
    correct_combinations = 0
    all_potential_candidates, max_combs = reduce(
        lambda acc, hint: (acc[0] | hint[0], acc[1] + hint[1]), cand_hints, (set(), 0)
    )
    # logger.info(f"All potential candidates count: {len(all_potential_candidates)}")
    # logger.info(f"All potential candidates: {all_potential_candidates}")
    # for group_size in range(2, max_combs + 1):
    #   if all_combinations != 0:
    #     logger.info(f"Correct {correct_combinations}/{all_combinations}")
    #   logger.info(f"Checking group size: {group_size}")
    #   all_combinations = 0
    #   correct_combinations = 0
    #   for group in combinations(all_potential_candidates, group_size):
    #     all_combinations += 1
    #     binary_profile = election.get_binary_representation()
    #     if not xJRTools.isPJR_ilp(binary_profile, group, committee_size):
    #       continue
    #     correct_combinations += 1
    #     logger.info("Am here")
    #     temp_cand_hints = [(set(group), group_size)]
    # temp_cand_hints = cand_hints
    if isinstance(voters, list):
        voters = dict(
            (index_voter[0], index_voter[1].approvals)
            for index_voter in enumerate(voters)
        )
    if isinstance(candidates, list) and isinstance(candidates[0], cands.Candidate):
        candidates = [c.ordinal_number for c in candidates]
    generator = baseProgram.enumerate_specific_jr_groups_comp_hints(
        candidates, voters, committee_size, forced_size, cand_hints, verif_cands
    )
    for succeded, result in generator:
        if not succeded:
            break
        solution = result[3]
        yield solution


if __name__ == "__main__":
    args = getArgumentsParser().parse_args()
    main(args)
