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

import argparse
import pandas as pd
import seaborn as sns
import pathlib

##from PIL import Image, ImageDraw, ImageFont
##import PIL.ImageOps
##import os
##import sys
##
##import matplotlib
import matplotlib.pyplot as plt

rc("font", family="serif", serif="Times")
rc("text", usetex=True)
rc("text.latex", preamble=r"\usepackage{amsmath}")
# plt.rc('axes', labelsize=27)
# plt.rcParams['font.size'] = 21


def getArgumentsParser():
    ap = argparse.ArgumentParser()
    ap.add_argument("-if", "--inputFile", required=True, help="Drawer input file")
    ap.add_argument(
        "-of", "--outputFile", required=False, help="Generated pdf " "chart filename"
    )
    return ap


def outputFig(fig=plt.gcf(), filename=None):
    if filename:
        fig.savefig(filename)
    else:
        plt.show()


def main(args):
    inputFilename = args.inputFile
    data = pd.read_csv(inputFilename, skipinitialspace=True)
    data = data.drop(columns=["Model Parameterization2"])
    data = data.groupby(
        ["Model", "Model Parameterization1", "Committee Size"], as_index=False
    ).mean()
    data["Model Parameterization1"] = data["Model Parameterization1"].map(
        lambda x: round(x, 2)
    )
    data = data.pivot(
        index="Model Parameterization1",
        columns="Committee Size",
        values="Minimum Just. Group",
    )
    print(data)

    plotAx = sns.heatmap(data=data.iloc[::-1])
    plotAx.set_xlabel("Committee size")
    plotAx.set_ylabel("Probability of approving the ground truth")

    outputFig()


def draw_pabulib(args):
    inputFilename = args.inputFile
    data = pd.read_csv(inputFilename, skipinitialspace=True)
    data = data.drop(columns=["Model Parameterization1"])
    data = data.drop(columns=["Model Parameterization2"])
    data = data.groupby(["Model", "Committee Size"], as_index=False).mean()
    data["Model"] = data["Model"].map(
        lambda modname: pathlib.PurePath(modname).parts[-1]
    )
    data = data.pivot(
        index="Model", columns="Committee Size", values="Minimum Just. Group"
    )
    data.sort_index(
        ascending=False,
        inplace=True,
        key=lambda x: pd.Index([(len(y), y) for y in x.values]),
    )
    print(data)

    plotAx = sns.heatmap(data=data.iloc[::-1], vmax=10, vmin=0)
    plotAx.set_xlabel("Committee size")
    plotAx.set_ylabel("Probability of approving the ground truth")

    outputFig(filename=args.outputFile)


if __name__ == "__main__":
    args = getArgumentsParser().parse_args()
    # main(args)
    draw_pabulib(args)
