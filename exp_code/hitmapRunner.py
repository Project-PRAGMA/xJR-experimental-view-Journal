#!/usr/bin/env -S python3 -u

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
import core.cfg as cfg
import argparse
import random
from tools.tools import Mesh2, CellsFeatures
import pathlib
import os
import rules
from distribs import (
    OneDDistribution,
    TwoDDistribution,
    ImpartialCulture,
    GaussianMixture1D,
)
from rules import JRCommittee, AnyCommittee
from rules import MaxApprovalCommittee
from rules import PJRCommittee, EJRCommittee, SinglePAV, SingleSequentialPhragmen


import elstats as statistics
import core.baseProgram as baseProgram
import sys

import discore
import distribs


# OLD SEEDS
# 1D: 111111111111111111
# 2D: 111111111111111129
# IC: 0
# GA: 1002
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


def run_experiments(out_dir, out_name, args):
    out_dir = os.path.relpath(out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    votersnr = args.voters_count
    committee_size = args.committee_size
    coverage_resolution = args.coverage_resolution
    seed = args.seed
    if args.input_file:
        distribution = distribs.PabulibElectionBasedDistribution(args.input_file, False)
        if not seed:
            seed = 100
        random.seed(seed)
        election = distribution.generate(votersnr)
    else:
        distribution = __distributions_collection[args.distribution]
        if not seed:
            seed = distribution[2]
        candidates = range(args.candidates_count)
        random.seed(seed)
        election = distribution[0].generate(candidates, votersnr)
        distribution = distribution[0]

    voters = election.votes
    candidates = election.candidates
    candidatesnr = len(candidates)
    # We need to make candidates a range object
    candidates = range(candidatesnr)
    if not args.input_file:
        assert candidatesnr == args.candidates_count

    if not coverage_resolution:
        coverage_resolution = votersnr
    approval_score_resolution = args.approval_score_resolution
    if not approval_score_resolution:
        approval_score_resolution = votersnr * committee_size
    resolution = (coverage_resolution, approval_score_resolution)
    logger.info(
        f"Candidates: {candidatesnr}, Voters: {votersnr}, "
        f"Commitee: {committee_size}"
    )
    logger.info(f"Mesh resolution (coverage x approval score): " f"{resolution}")
    logger.info(f"Distribution: {distribution.get_short_description()}, Seed: {seed}")

    stats = statistics.Statistics(candidates, voters, committee_size)
    stats.compute()
    logger.debug(stats)
    mesh = Mesh2(
        candidatesnr,
        votersnr,
        committee_size,
        resolution[0],
        resolution[1],
        stats.minCov,
        stats.maxCov,
        stats.minApp,
        stats.maxApp,
    )

    import functools

    procedures = [
        # Justified Representation-related procedures
        (
            AnyCommittee(),
            CellsFeatures.EXISTS,
            CellsFeatures.EMPTY,
            CellsFeatures.UNKNOWN,
        ),
        (JRCommittee(), CellsFeatures.JR, None, CellsFeatures.EXISTS),
        (PJRCommittee(), CellsFeatures.PJR, None, CellsFeatures.JR),
        (EJRCommittee(), CellsFeatures.EJR, None, CellsFeatures.PJR),
        # Computes Single PAV
        (SinglePAV(), CellsFeatures.PAV, CellsFeatures.EMPTY, CellsFeatures.UNKNOWN),
        # Computes Single Phragmen
        (
            SingleSequentialPhragmen(),
            CellsFeatures.PHR,
            CellsFeatures.EMPTY,
            CellsFeatures.UNKNOWN,
        ),
    ]

    predefined_procedure_sets = {
        "PHR": [procedures[-1]],
        "PAV": [procedures[-2]],
        "xJR": procedures[:4],
    }
    procedures_to_use = predefined_procedure_sets["PHR"]
    if args.rule_set:
        procedures_to_use = predefined_procedure_sets[args.rule_set]
    for procedure in procedures_to_use:
        algorithm, feature, fail_feature, necessary_feature = procedure
        logger.info(f"Started computing: {algorithm.description()}")
        mesh.set_computation_area_by_feature(necessary_feature)
        functor = functools.partial(
            algorithm.compute_once, candidates, voters, committee_size
        )
        mesh.fill_with(functor, feature, fail_feature)

    with open(os.path.join(out_dir, out_name + ".outhit"), "w") as out_file:
        stats.show(out_file)
        mesh.depict(out_file)


def getArgumentsParser():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-od", "--outDir", required=True, help="Directory to output experiment data"
    )
    ap.add_argument(
        "-ll",
        "--logLevel",
        choices=["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"],
        required=False,
        help="Logging level",
        default="WARNING",
    )
    ap.add_argument(
        "-of",
        "--outFile",
        required=True,
        help="name of the file with output---excluding extension",
    )
    ap.add_argument(
        "-k",
        "--committee_size",
        required=True,
        help="Size of the " "committee to draw",
        type=int,
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
        "-c",
        "--coverage_resolution",
        required=False,
        help="Coverage resolution",
        type=int,
    )
    ap.add_argument(
        "-a",
        "--approval_score_resolution",
        required=False,
        help="Approval score resolution",
        type=int,
    )
    ap.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        required=False,
        help="Show a few live notifications about computing",
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
    ap.add_argument(
        "-if",
        "--input_file",
        required=False,
        help="Pabulib source distribution",
        type=pathlib.PurePath,
    )
    ap.add_argument(
        "-r",
        "--rule_set",
        required=True,
        help="Set of rules to apply",
        choices=["PAV", "PHR", "xJR"],
    )
    return ap


if __name__ == "__main__":
    args = getArgumentsParser().parse_args()
    cfg.is_verbose = args.verbose
    outDir = args.outDir
    out_file = args.outFile
    logger.setLevel(args.logLevel)
    run_experiments(outDir, out_file, args)
