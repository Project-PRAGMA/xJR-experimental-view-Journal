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
import pathlib
import rules
from distribs import (
    OneDDistribution,
    TwoDDistribution,
    ImpartialCulture,
    GaussianMixture1D,
)
import isxJRChecker as xjrcheck
import discore
import distribs
from tqdm import tqdm


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


def run_experiments(out_name, args):
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

    voters = election.votes
    candidates = election.candidates
    V = []
    app = 0
    for voter in voters:
        binary_repr = voter.get_binary_representation(candidates)
        V.append(binary_repr)
        app += sum(binary_repr)

    heat_data = sampling(
        V,
        app,
        approval_score_resolution,
        coverage_resolution,
        committee_size,
        args.trials,
    )

    save_heatmap(heat_data, args.outFile)


def save_heatmap(MAP, outfile):
    with open(outfile, "w") as out_file:
        for i in sorted(range(1, len(MAP)), reverse=True):
            out_file.write(" ".join(map(str, MAP[i])) + "\n")
        out_file.write(" ".join(map(str, MAP[0])))


def avScore(V, W):
    score = 0
    for v in V:
        for c in W:
            score += v[c]
    return score


def ccScore(V, W):
    score = 0
    for v in V:
        add_score = 0
        for c in W:
            if v[c] == 1:
                add_score = 1
        score += add_score
    return score


def sampling(V, app, max_approval, max_coverage, k, trials):
    MAP = [[0 for _ in range(max_approval + 1)] for i in range(max_coverage + 1)]

    n = len(V)
    m = len(range(len(V[0])))

    logger.info(f"AVG APPROVAL: {float(app)/(n)}")
    EXP = trials
    if not EXP:
        EXP = 100000  # int(argv[3])

    counter = 0
    of_which_ejr = 0
    for x in tqdm(range(EXP)):
        if x % 1000 == 0:
            logger.info(x)

        W = random.sample(range(m), k)
        if not xjrcheck.isJR(V, W):
            continue
        counter += 1

        av = avScore(V, W)
        cc = ccScore(V, W)
        #    try:
        MAP[cc][av] += 1
        #    except IndexError:
        #      pass
        if xjrcheck.isEJR_ilp(V, W, len(W)):
            of_which_ejr += 1
    print(f"Found {counter} JR committees of which {of_which_ejr} are EJR")
    return MAP


def getArgumentsParser():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-ll",
        "--logLevel",
        choices=["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"],
        required=False,
        help="Logging level",
        default="WARNING",
    )
    ap.add_argument(
        "-of", "--outFile", required=True, help="name of the file with output"
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
    ap.add_argument("-t", "--trials", required=False, help="Number of trials", type=int)
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
    return ap


if __name__ == "__main__":
    args = getArgumentsParser().parse_args()
    cfg.is_verbose = args.verbose
    out_file = args.outFile
    logger.setLevel(args.logLevel)
    run_experiments(out_file, args)
