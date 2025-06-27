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

import argparse
import pathlib
from PIL import Image, ImageDraw
from PIL import ImageColor

import hitmap_reader as hmapreader
import PIL.ImageOps
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib import rc

FONTSIZE = 12
rc("font", **{"family": "serif", "serif": ["Computer Modern"]})
plt.rcParams.update(
    {"text.usetex": True, "font.size": FONTSIZE, "font.family": "serif"}
)


def draw_heatmap(
    MAP, max_approval, max_coverage, outfile, cc_coverage, app_satisfaction
):
    sq_len = 30
    diagram_size_x = sq_len * (max_approval - 1)
    diagram_size_y = sq_len * max_coverage
    im = Image.new("RGB", (diagram_size_x, diagram_size_y), "white")
    dr = ImageDraw.Draw(im)
    M = 0

    for y in range(max_coverage + 1):
        for x in range(max_approval):
            M = max(MAP[max_coverage - y][x], M)

    full_col_r, full_col_g, full_col_b = 152, 17, 17
    empty_col_r, empty_col_g, empty_col_b = 255, 255, 255

    for y in range(max_coverage + 1):
        for x in range(max_approval):
            val = float(MAP[max_coverage - y][x]) / M
            #        if( MAP[y][x] > 0 ):
            #            val = 1
            y1 = sq_len * (y + 1) - 1
            y2 = sq_len * y
            tmp = y1
            y1 = y2
            y2 = tmp
            fill_color_r = empty_col_r + val * (full_col_r - empty_col_r)
            fill_color_g = empty_col_g + val * (full_col_g - empty_col_g)
            fill_color_b = empty_col_b + val * (full_col_b - empty_col_b)
            fill_color = "rgb(%d,%d,%d)" % (fill_color_r, fill_color_g, fill_color_b)
            dr.rectangle(
                ((sq_len * x, y1), ((x + 1) * sq_len - 1, y2)), fill=fill_color
            )
        #    for xd in range(x*sq_len, (x+1)*sq_len):
        #      for yd in range(1+(98-y)*sq_len, 1+(99-y)*sq_len):
        #        #print((x, y))
        #        #print((xd, yd))
        #        dr.point((xd,yd), fill= "rgb(%d,%d,%d)" % (255, 255-255*val,255-255*val))

    dpi = 600
    image_width_inches = diagram_size_x / dpi
    image_height_inches = diagram_size_y / dpi

    name = outfile

    frame_ticks_linewidth = 0.05
    scaling = 2

    fig, ax = plt.subplots(
        dpi=dpi, figsize=(image_width_inches / scaling, image_height_inches / scaling)
    )
    ax.imshow(im, aspect="equal")
    ax.tick_params(axis="both", which="major", width=frame_ticks_linewidth)

    loosely_dashed_linestyle = (0, (9, 9))

    x_av_level = app_satisfaction * sq_len - sq_len / 2
    ax.plot(
        [x_av_level] * 2,
        [0, diagram_size_y],
        color="black",
        linewidth=0.0625,
        linestyle=loosely_dashed_linestyle,
    )
    ##  ax.text(x_av_level-(sq_len*54), (sq_len*4), "max.\\,satisfaction")

    y_cc_level = (cc_coverage) * sq_len - sq_len / 2
    ax.plot(
        [0, diagram_size_x],
        [y_cc_level] * 2,
        color="black",
        linewidth=0.0625,
        linestyle=loosely_dashed_linestyle,
    )
    ##  ax.text(30, y_cc_level-(sq_len*5), "max.\\,coverage")

    ax.tick_params(axis="both", which="major", width=frame_ticks_linewidth)
    yticks = list(range(0, diagram_size_y + 1, diagram_size_y // 2)) + [y_cc_level]
    ax.set_ylim(ymin=0, ymax=diagram_size_y)
    ax.set_yticks(yticks)
    ax.set_yticklabels(
        labels=list(map(lambda x: r"${}$".format(int(x / sq_len)), yticks[:-1]))
        + ["CC"],
        rotation=45,
        fontsize=FONTSIZE,
    )

    dx = 0 / 72.0
    dy = -20 / 72.0
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)
    ccticklabel = ax.yaxis.get_majorticklabels()[-1]
    ccticklabel.set_transform(ccticklabel.get_transform() + offset)

    linne = matplotlib.lines.Line2D(
        (-67, -70 * 2.75),
        (y_cc_level, y_cc_level - 11 * sq_len),
        linewidth=0.01,
        color="black",
        clip_on=False,
    )
    ax.add_line(linne)

    ax.set_xlim(xmin=0, xmax=diagram_size_x)
    xticks = list(range(0, diagram_size_x + 1, diagram_size_x // 2)) + [x_av_level]
    ax.set_xticks(xticks)
    ax.set_xticklabels(
        list(map(lambda x: r"${}$".format(int(x / sq_len)), xticks[:-1])) + ["AV"],
        fontsize=FONTSIZE,
    )

    if args.move_sat_label_left:
        dx = -20 / 72.0
        dy = 0 / 72.0
        offset = matplotlib.transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)
        avticklabel = ax.xaxis.get_majorticklabels()[-1]
        avticklabel.set_transform(avticklabel.get_transform() + offset)

        linne = matplotlib.lines.Line2D(
            (x_av_level, x_av_level - 7 * sq_len),
            (-70, -65 * 2),
            linewidth=0.01,
            color="black",
            clip_on=False,
        )
        ax.add_line(linne)

    ax.grid(visible=False)
    for edge, spine in ax.spines.items():
        spine.set_linewidth(frame_ticks_linewidth)

    fig.tight_layout(pad=0)
    fig.savefig(name, dpi=dpi)


def read_in_heatmap_data(in_path):
    heatmap_data = []
    max_y = 0
    max_x = 0
    with open(in_path, "r") as in_file:
        for line in in_file:
            if line.strip() == "":
                continue
            entries = list(map(int, line.split(" ")))
            max_x = len(entries)
            heatmap_data.append(entries)
    # count for 0, so from 0 to 100 there is 101 elements
    max_y = len(heatmap_data) - 1
    print(heatmap_data)
    return heatmap_data, max_x, max_y


def getArgumentsParser():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-of",
        "--out_file",
        required=True,
        help="name of the file with output",
        type=pathlib.PurePath,
    )
    ap.add_argument(
        "-if",
        "--input_file",
        required=True,
        help="Heatmap data, i.e., .heatmap file",
        type=pathlib.PurePath,
    )
    ap.add_argument(
        "-ch",
        "--corresponding_hitmap",
        required=True,
        help="Corresponding hitmap data file, i.e., .hitmap file",
        type=pathlib.PurePath,
    )
    ap.add_argument(
        "-ms",
        "--move_sat_label_left",
        required=False,
        default=False,
        help="Move satisfaction label to the left",
        type=bool,
    )
    return ap


if __name__ == "__main__":
    args = getArgumentsParser().parse_args()
    out_file = args.out_file
    data, max_approval, max_coverage = read_in_heatmap_data(args.input_file)
    _, cc_coverage, app_satisfaction = hmapreader.parse_hitmap_output(
        args.corresponding_hitmap
    )
    draw_heatmap(
        data, max_approval, max_coverage, out_file, cc_coverage, app_satisfaction
    )
