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
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import rc

rc("font", family="serif", serif="Times")
rc("text", usetex=True)
rc("text.latex", preamble=r"\usepackage{amsmath}")
plt.rc("axes", labelsize=27)
plt.rcParams["font.size"] = 21


def getArgumentsParser():
    ap = argparse.ArgumentParser()
    ap.add_argument("-if", "--input_file", required=True, help="Drawer input file")
    ap.add_argument(
        "-of", "--output_file", required=False, help="Generated pdf " "chart filename"
    )
    ap.add_argument(
        "-re",
        "--real_election",
        required=False,
        help="Data input file for real " "elections to present as scatter plot",
    )
    return ap


def materialize_figure(fig=plt.gcf(), filename=None):
    if filename:
        fig.savefig(filename)
    else:
        plt.show()


def collect_files_to_print(path):
    path = Path(path)
    if not path.exists():
        raise ValueError(f"{path} does not exist!")
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory!")

    all_files = [f for f in path.iterdir() if f.is_file()]
    out_files = [f for f in all_files if f.parts[-1].endswith(".out")]
    return out_files


def read_non_gaussian_file(file_path):
    data = pd.read_csv(
        file_path,
        sep="\s+",
        usecols=[2, 5, 7, 9],
        names=["apprPerVoter", "JR", "PJR", "EJR"],
        skipinitialspace=True,
        skiprows=0,
    )
    return data


def read_gaussian_file(file_path):
    data = pd.read_csv(
        file_path,
        sep="\s+",
        usecols=[3, 6, 8, 10],
        names=["apprPerVoter", "JR", "PJR", "EJR"],
        skipinitialspace=True,
        skiprows=0,
    )
    return data


def read_real_election_file(file_path):
    data = pd.read_csv(
        file_path,
        sep="\s+",
        usecols=[8, 11, 13, 15],
        names=["apprPerVoter", "JR", "PJR", "EJR"],
        skipinitialspace=True,
        skiprows=0,
    )
    return data


def is_non_gaussian_file(file_path):
    file_name = file_path.parts[-1]
    return (
        file_name.find("1D") == -1
        and file_name.find("2D") == -1
        and file_name.find("IC") == -1
    )


def plot_core_parties_distribs(file_path, plot_ax):
    data = pd.read_csv(
        file_path,
        sep="\s+",
        usecols=[2, 4, 8, 11, 13, 15],
        names=["parties", "commsize", "apprPerVoter", "JR", "PJR", "EJR"],
        skipinitialspace=True,
        skiprows=0,
    )

    print(data)
    partData = data.loc[data["parties"] == 2]
    partSecData = data.loc[data["parties"] == 0]

    partData = partData.melt(
        id_vars=["apprPerVoter", "commsize", "parties"],
        var_name="Concept",
        value_name="Ratio",
    )
    partSecData = partSecData.melt(
        id_vars=["apprPerVoter", "commsize", "parties"],
        var_name="Concept",
        value_name="Ratio",
    )
    print(data)
    plot_ax = sns.lineplot(
        ax=plot_ax,
        data=partData,
        x="apprPerVoter",
        y="Ratio",
        hue="Concept",
        errorbar=None,
    )
    print(partSecData)
    plot_ax = sns.scatterplot(
        data=partSecData,
        x="apprPerVoter",
        y="Ratio",
        hue="Concept",
        errorbar=None,  # style='parties' ,
        ax=plot_ax,
    )


def plot_standard_synthetic_distribs(filename, plot_ax):
    if is_non_gaussian_file(filename):
        data = read_non_gaussian_file(filename)
    else:
        data = read_gaussian_file(filename)
    data = data.melt(id_vars=["apprPerVoter"], var_name="Concept", value_name="Ratio")
    sns.lineplot(
        ax=plot_ax,
        data=data,
        x="apprPerVoter",
        y="Ratio",
        style="Concept",
        errorbar=None,
    )


def plot_real_election_overlay_scatter(plot_ax, data):
    """
    We assume it is the case that the probability of JR/PJR/EJR is exactly the same,
    hence we draw onyl JR --- so far it has always been the case for the real data
    we used.

    Alternatively, the following line could be of use
      data = data.melt(id_vars = ['apprPerVoter'], var_name="Concept", value_name='Ratio')
    """
    sns.scatterplot(data=data, x="apprPerVoter", y="JR", ax=plot_ax)


def main(args):
    files_to_print = collect_files_to_print(args.input_file)
    coreParties = False

    rows = 1
    cols = 1
    fig, axs = plt.subplots(
        rows, cols, figsize=(7.5, 7.25), gridspec_kw={"hspace": 0.25}, sharey="row"
    )

    counter = 0
    real_election_data = None
    for file_path in files_to_print:
        if rows == 1 and cols == 1:
            plotAx = axs
        else:
            plotAx = axs[counter // cols, counter % cols]
        counter += 1
        plotAx.set_xlabel("Avg. number of approval per agent")
        plotAx.set_ylabel("Ratio of drawn xJR committees")
        plotAx.set_ylim(bottom=0.0, top=1.0)
        plotAx.set_xlim(left=0, right=50)
        # plotAx.set_title(file_path.parts[-1])
        if coreParties:
            plot_core_parties_distribs(file_path)
        else:
            plot_standard_synthetic_distribs(file_path, plotAx)

        if args.real_election:
            if not real_election_data:
                real_election_data = read_real_election_file(args.real_election)
            plot_real_election_overlay_scatter(plotAx, real_election_data)

    materialize_figure(fig, filename=args.output_file)


if __name__ == "__main__":
    args = getArgumentsParser().parse_args()
    main(args)
