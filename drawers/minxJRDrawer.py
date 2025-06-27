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
import math

import matplotlib.pyplot as plt
from matplotlib import rc

rc("font", family="serif", serif="Times")
rc("text", usetex=True)
rc("text.latex", preamble=r"\usepackage{amsmath}")
plt.rc("axes", labelsize=20)
plt.rcParams["font.size"] = 18


def getArgumentsParser():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-if",
        "--inputFile",
        required=True,
        help="Drawer input file",
        type=pathlib.PurePath,
    )
    ap.add_argument(
        "-of",
        "--outputFile",
        required=False,
        help="Generated pdf chart filename",
        type=pathlib.PurePath,
    )
    ap.add_argument("-m", "--model", required=False, help="Plot only  this model")
    return ap


def outputFig(fig=plt.gcf(), filename=None):
    if filename:
        fig.savefig(filename, bbox_inches="tight")
    else:
        plt.show()


def main(args):
    inputFilename = args.inputFile
    data = pd.read_csv(inputFilename, skipinitialspace=True)
    data = data.drop(columns=["Model Parameterization2"])
    data = data.drop(columns=["Model Parameterization1"])
    ######################################
    # UNNECESSARY AS SNS DOES IT AUTOMATICALLY
    # data = data.groupby(["Model", "Committee Size"], as_index=False).mean()
    ######################################

    def crop_path_model_names(path):
        path = path.strip()
        left_cropped = path[path.rfind("/") + 1 :]
        return left_cropped.split(" ")[0]

    data["Model"] = data["Model"].map(crop_path_model_names)
    # print(data)
    data = data.melt(
        id_vars=["Model", "Committee Size"],
        value_vars=[
            "Minimum JR Just. Group",
            "Minimum PJR Just. Group",
            "Minimum EJR Just. Group",
        ],
        value_name="Minimum",
        var_name="Concept",
    )
    concepts_mapping = {
        "Minimum JR Just. Group": "Min. just. group: JR",
        "Minimum PJR Just. Group": "Min. just. group: PJR",
        "Minimum EJR Just. Group": "Min. just. group: EJR",
    }
    data["Concept"] = data["Concept"].map(lambda conc: concepts_mapping[conc])
    # print(data)

    models = set(data["Model"])
    models_count = len(models)

    xlabel = "Committee size"
    ylabel = "Avg. min. justifying group"

    model = None
    if args.model:
        model = args.model
        if not model in models:
            print(f"The specified model {args.model} is not in the data file!")
            print(f"All models: {models}")
            exit(1)
        models_count = 1

    if models_count > 1:
        columns = 3
        rows = math.ceil(models_count / columns)
        fig, ax = plt.subplots(
            nrows=rows,
            ncols=columns,
            sharey=True,
            sharex=True,
            figsize=(14, 16),
            layout="constrained",
        )
        fig.supxlabel(xlabel)
        fig.supylabel(ylabel)
        for i, model in enumerate(models):
            toplot = data.loc[data["Model"] == model]
            plotAx = sns.lineplot(
                data=toplot,
                x="Committee Size",
                y="Minimum",
                style="Concept",
                ax=ax[i // columns][i % columns],
            )
            if i > 0:
                plotAx.legend([], [], frameon=False)
            else:
                sns.move_legend(plotAx, "upper left")
            plotAx.set_xlabel("")
            plotAx.set_ylabel("")
            plotAx.set_ylim([0, 8])
            plotAx.set_xlim([0, 15])
            plotAx.axline((0, 0), (15, 15), color="black", ls="--", lw="0.5")
            plotAx.set_title(model)
    else:
        if not model:
            model = list(models)[0]
        fig, ax = plt.subplots(figsize=(10, 5))
        toplot = data.loc[data["Model"] == model]
        print(model)
        print(toplot)
        plotAx = sns.lineplot(
            data=toplot,
            x="Committee Size",
            y="Minimum",
            style="Concept",
            ax=ax,
            errorbar=None,
            # , errorbar="sd"
        )
        plotAx.axline((0, 0), (15, 15), color="black", ls="--", lw="0.5")
        ## REVERSE LEGEND ENTRIES
        handles, labels = plotAx.get_legend_handles_labels()
        handles, labels = handles[::-1], labels[::-1]
        plotAx.legend(handles, labels, fontsize=16, loc="upper left")
        ##
        plotAx.set_ylim([0, 8])
        plotAx.set_xlim([0, 15])
        plotAx.set_xlabel(xlabel)
        plotAx.set_ylabel(ylabel)
    outputFig(fig, filename=args.outputFile)


if __name__ == "__main__":
    args = getArgumentsParser().parse_args()
    main(args)
