#!/usr/bin/env python3

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


from random import *
from numpy import mean
from itertools import *
import sys
import argparse
from pathlib import Path
from functools import reduce
import operator
import tqdm

import isxJRChecker as xJRTools
import distribs
import discore
import tools.pblib as pbtools

seed(123)


def get_argument_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-of", "--outputFile", required=True, help="Output file for experiment data"
    )
    ap.add_argument(
        "-ed",
        "--elections_directory",
        required=False,
        help="Directory with election files that should be used as distributions",
    )
    ap.add_argument(
        "-ig",
        "--ignoredFiles",
        required=False,
        help="A path to a " "file with ignored files listed each in a separate line",
    )
    ap.add_argument(
        "-k", "--committeeSize", required=True, help="Size of the " "committee to draw"
    )
    ap.add_argument(
        "-t",
        "--trialsCount",
        required=True,
        help="Number of " "experiment trials for one distribution",
    )
    ap.add_argument(
        "-n",
        "--voters_count",
        required=True,
        help="Number of " "voters in a single election",
    )
    ap.add_argument(
        "-m",
        "--candidates_count",
        required=True,
        help="Number of " "candidates in a single election",
    )
    ap.add_argument(
        "-v", "--verbose", action="store_true", required=False, help="Show progress bar"
    )
    ap.add_argument(
        "-d", "--distribution", required=True, choices=EXPERIMENTS_DISTROS.keys()
    )
    return ap


def write_result_line(
    approvalsCount,
    jrCount,
    pjrCount,
    ejrCount,
    votCount,
    trialsCount,
    preamble,
    file=sys.stdout,
):
    def get_ratio(succeededCount):
        return float(succeededCount) / trials

    to_print = f"{preamble}, approvals: {float(app)/(votCount*trialsCount)} -->\
  JR: {get_ratio(jrCount)}   PJR: {get_ratio(pjrCount)}   EJR:    \
  {get_ratio(ejrCount)}"

    print(to_print, file=file, flush=True)


EXPERIMENTS_DISTROS = {
    #  "gaussian": [ distribs.GaussianMixture1D(
    #                  discore.DistributionParameters(
    #                    probabilities = (.6, .2, .2),
    #                    centers = (.5, .2, .8),
    #                    standard_deviations = (.1, .05, .05),
    #                    approval_radius = (rad * 0.00625)
    #                  )
    #                ) for rad in range(1, 50) ],
    #  "gaussian_more_peak": [ distribs.GaussianMixture1D(
    #                  discore.DistributionParameters(
    #                    probabilities = (.8, .1, .1),
    #                    centers = (.5, .2, .8),
    #                    standard_deviations = (.1, .05, .05),
    #                    approval_radius = (rad * 0.00625)
    #                  )
    #                ) for rad in range(1, 50) ],
    #  "gaussian_less_peak": [ distribs.GaussianMixture1D(
    #                  discore.DistributionParameters(
    #                    probabilities = (.4, .3, .3),
    #                    centers = (.5, .2, .8),
    #                    standard_deviations = (.1, .05, .05),
    #                    approval_radius = (rad * 0.00625)
    #                  )
    #                ) for rad in range(1, 50) ],
    #  "gaussian_farther": [ distribs.GaussianMixture1D(
    #                  discore.DistributionParameters(
    #                    probabilities = (.6, .2, .2),
    #                    centers = (.5, .1, .9),
    #                    standard_deviations = (.1, .05, .05),
    #                    approval_radius = (rad * 0.00625)
    #                  )
    #                ) for rad in range(1, 50) ],
    #  "gaussian_closer1": [ distribs.GaussianMixture1D(
    #                  discore.DistributionParameters(
    #                    probabilities = (.6, .2, .2),
    #                    centers = (.5, .3, .7),
    #                    standard_deviations = (.1, .05, .05),
    #                    approval_radius = (rad * 0.00625)
    #                  )
    #                ) for rad in range(1, 50) ],
    #  "gaussian_closer2": [ distribs.GaussianMixture1D(
    #                  discore.DistributionParameters(
    #                    probabilities = (.6, .2, .2),
    #                    centers = (.5, .4, .6),
    #                    standard_deviations = (.1, .05, .05),
    #                    approval_radius = (rad * 0.00625)
    #                  )
    #                ) for rad in range(1, 50) ],
    #  "gaussian_assymetric_prob": [ distribs.GaussianMixture1D(
    #                  discore.DistributionParameters(
    #                    probabilities = (.6, .3, .1),
    #                    centers = (.5, .2, .8),
    #                    standard_deviations = (.1, .05, .05),
    #                    approval_radius = (rad * 0.00625)
    #                  )
    #                ) for rad in range(1, 50) ],
    #  "single_gaussian_wide": [ distribs.GaussianMixture1D(
    #                  discore.DistributionParameters(
    #                    probabilities = (1, 0, 0),
    #                    centers = (.5, 0, 0),
    #                    standard_deviations = (.2, 0, 0),
    #                    approval_radius = (rad * 0.00625)
    #                  )
    #                ) for rad in range(1, 50) ],
    "GA": [
        distribs.GaussianMixture1D(
            discore.DistributionParameters(
                probabilities=(1, 0, 0),
                centers=(0.5, 0, 0),
                standard_deviations=(0.1, 0, 0),
                approval_radius=(rad * 0.00625),
            )
        )
        for rad in range(1, 50)
    ],
    #  "single_gaussian_slim": [ distribs.GaussianMixture1D(
    #                  discore.DistributionParameters(
    #                    probabilities = (1, 0, 0),
    #                    centers = (.5, 0, 0),
    #                    standard_deviations = (.05, 0, 0),
    #                    approval_radius = (rad * 0.00625)
    #                  )
    #                ) for rad in range(1, 50) ],
    "1D": [
        distribs.OneDDistribution(
            discore.DistributionParameters(approval_radius=rad * 0.01)
        )
        for rad in range(1, 27)
    ],
    "2D": [
        distribs.TwoDDistribution(
            discore.DistributionParameters(approval_radius=rad * 0.02)
        )
        for rad in range(1, 26)
    ],
    "IC": [
        distribs.ImpartialCulture(
            discore.DistributionParameters(approval_probability=rad * 0.015)
        )
        for rad in range(1, 28)
    ],
}

if __name__ == "__main__":
    args = get_argument_parser().parse_args()
    trials = int(args.trialsCount)
    k = int(args.committeeSize)
    n = int(args.voters_count)
    m = int(args.candidates_count)

    elections_from_pabulib = args.elections_directory != None

    if elections_from_pabulib:
        print(f"Distributions from: {args.elections_directory}")
        distros = pbtools.get_election_based_distributions(
            args.elections_directory, args.ignoredFiles
        )
    else:
        distros = EXPERIMENTS_DISTROS[args.distribution]

    distributions_to_consider = tqdm.tqdm(distros) if args.verbose else distros
    for distro in distributions_to_consider:
        print(distro)
        print(distro.get_description())
        app = 0
        jr = 0
        pjr = 0
        ejr = 0

        for i in range(trials):
            if elections_from_pabulib:
                app_election = distro.generate(n)
            else:
                app_election = distro.generate(list(range(m)), n)
            # print(app_election)
            binary_profile = app_election.get_binary_representation()
            app += reduce(
                operator.add,
                [
                    reduce(operator.add, binary_pref, 0)
                    for binary_pref in binary_profile
                ],
                0,
            )

            W = sample(app_election.candidates, k)
            W = [cand.ordinal_number for cand in W]

            JRFlag, PJRFlag, EJRFlag = xJRTools.xJRChecking(binary_profile, W)

            ejr = ejr + int(EJRFlag)
            pjr = pjr + int(PJRFlag)
            jr = jr + int(JRFlag)

        with open(Path(args.outputFile), "a") as outFile:
            write_result_line(
                app,
                jr,
                pjr,
                ejr,
                n,
                trials,
                distro.get_short_description(),
                file=outFile,
            )
