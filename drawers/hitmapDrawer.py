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

from PIL import Image, ImageDraw, ImageFont
import PIL.ImageOps
import os
import sys
import argparse
import hitmap_reader as hmapreader

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

FONTSIZE = 12
rc("font", **{"family": "serif", "serif": ["Computer Modern"]})
plt.rcParams.update(
    {"text.usetex": True, "font.size": FONTSIZE, "font.family": "serif"}
)


def getArgumentsParser():
    ap = argparse.ArgumentParser()
    ap.add_argument("-if", "--inputFile", required=True, help="File .outhit")
    #  ap.add_argument("-ll", "--logLevel", choices = ["INFO", "DEBUG", "WARNING",
    #    "ERROR", "CRITICAL"], required = False, help="Logging level",
    #    default = "WARNING")
    ap.add_argument(
        "-of",
        "--outFile",
        required=True,
        help="Name of the pdf file with output---excluding extension",
    )
    ap.add_argument(
        "-c",
        "--coverage_resolution",
        required=True,
        help="Coverage resolution",
        type=int,
    )
    ap.add_argument(
        "-a",
        "--approval_score_resolution",
        required=True,
        help="Approval score resolution",
        type=int,
    )
    ap.add_argument(
        "-lb",
        "--label_down",
        required=False,
        default=False,
        help="Put seq. phrag and pav labels below the points",
        type=bool,
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


def color_to_draw(cell):
    data_priority = ["p", "v", "e", "r", "x", "s", ".", "u", "h"]
    symbols_colors = {
        "s": "#f9dada",
        #      'x': "#ff9999",
        #      'r': "#ff6666",
        "x": "#ff8484",
        "r": "#d03232",
        "e": "#981111",
        "p": "#981111",
        "v": "#981111",
    }
    most_important = sorted(cell, key=lambda x: data_priority.index(x))[0]
    return symbols_colors[most_important]


def parse_exp_output(data_filename, out_filename, args):
    data, cc_coverage, app_satisfaction = hmapreader.parse_hitmap_output(data_filename)

    sq_len = 30
    vertical_cells = args.coverage_resolution
    horizontal_cells = args.approval_score_resolution
    line_width = 0
    font_point_size = 60
    point_to_pixels_ratio = 1.4
    description_lines = 12
    description_gap = 20

    label_size = 6
    frame_ticks_linewidth = 0.05

    mesh_color = "black"
    desc_color = "black"
    bg_color = "white"

    diagram_ext = "pdf"

    diagram_size_x = horizontal_cells * sq_len + line_width * (horizontal_cells + 1)
    diagram_size_y = vertical_cells * sq_len + line_width * (vertical_cells + 1)
    img = Image.new(
        "RGB",
        (diagram_size_x, diagram_size_y)
        #    +description_gap+description_lines*int(font_point_size*point_to_pixels_ratio))
        ,
        color=bg_color,
    )
    pen = ImageDraw.Draw(img)
    #  for i in range(verticalCells+1):
    #    pen.line(((0,i*(sq_len+line_width)),(diagram_size_x,i*(sq_len+line_width))),
    #       fill=mesh_color, width=line_width)
    #  for i in range(horizontal_cells+1):
    #    pen.line(((i*(sq_len+line_width), 0),(i*(sq_len+line_width),diagram_size_y)),
    #        fill=mesh_color, width=line_width)

    import random

    pav_coords = None
    for rn, line in enumerate(data):
        for cn, cell in enumerate(line):
            if cell == tuple("."):
                continue
            y1 = sq_len * (rn + 1) - 1
            y2 = sq_len * rn
            tmp = y1
            y1 = y2
            y2 = tmp
            pen.rectangle(
                ((sq_len * cn, y1), ((cn + 1) * sq_len - 1, y2)),
                fill=color_to_draw(cell),
            )
            if "v" in cell:
                pav_coords = (cn, rn)
            if "p" in cell:
                phragmen_coords = (cn, rn)
    #      pen.rectangle(
    #          ((line_width + (sq_len+line_width)*cn,(sq_len+line_width)*(rn+1)-line_width),
    #          ((line_width+sq_len)*(cn+1)-line_width,line_width + (line_width+sq_len)*rn))
    #        ,fill=symbols_colors[cell]) #  fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', font_point_size)
    #  pen.text((0,diagram_size_y+description_gap), description, font=fnt, fill=desc_color)
    #  img.save("blah70.png")

    if not pav_coords:
        pav_coords = phragmen_coords

    dpi = 600
    image_width_inches = diagram_size_x / dpi
    image_height_inches = diagram_size_y / dpi
    scaling = 2

    fig, ax = plt.subplots(
        dpi=dpi, figsize=(image_width_inches / scaling, image_height_inches / scaling)
    )
    ax.imshow(img, aspect="equal")

    def transfer_coords(x_y_coords):
        return (
            (x_y_coords[0] + 0.5) / float(horizontal_cells),
            1 - ((x_y_coords[1] + 0.5) / float(vertical_cells)),
        )

    jr_label_col = horizontal_cells / 4
    non_jr_label_col = horizontal_cells * 0.05

    def locate_baloon(label_col, data_point_marker):
        # scan vertically first and then horizontally
        for test_col in range(int(label_col + 3), horizontal_cells + 1):
            for test_row in range(vertical_cells - 1, 0, -1):
                if data_point_marker in data[test_row][test_col]:
                    return (test_col, test_row)

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

    ax.tick_params(
        axis="both", which="major", labelsize=label_size, width=frame_ticks_linewidth
    )
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

    #  ax.set_xlabel(u"satisfaction", size = 8)
    # ax.set_title(description, fontsize=label_size)
    ax.grid(visible=False)
    for edge, spine in ax.spines.items():
        spine.set_linewidth(frame_ticks_linewidth)

    ##  col_phrag = "blue"
    ##  col_pav = "green"
    ##  phragy = phragmen_coords[1]*sq_len+sq_len/2
    ##  phragx = phragmen_coords[0]*sq_len+sq_len/2
    ##  phrag_circle_bl_edge = matplotlib.patches.Circle((phragx, phragy), radius = 63,
    ##                                           fill = False, linewidth = .2,
    ##                                           edgecolor = "black")
    ##  phrag_circle_edge = matplotlib.patches.Circle((phragx, phragy), radius = 55,
    ##                                           fill = False, linewidth = .4,
    ##                                           edgecolor = col_phrag)
    ##  phrag_circle_out = matplotlib.patches.Circle((phragx, phragy), radius = 42,
    ##                                           fill = False, linewidth = .55,
    ##                                           edgecolor = col_phrag, alpha = 0.4)
    ##  phrag_circle_in = matplotlib.patches.Circle((phragx, phragy), radius = 27,
    ##                                           fill = False, linewidth = .4,
    ##                                           edgecolor = "black", alpha = 0.25)
    ##
    ##  ax.add_artist(phrag_circle_bl_edge)
    ##  ax.add_artist(phrag_circle_edge)
    ##  ax.add_artist(phrag_circle_out)
    ##  ax.add_artist(phrag_circle_in)
    ##
    ##  pavy = pav_coords[1]*sq_len+sq_len/2
    ##  pavx = pav_coords[0]*sq_len+sq_len/2
    ##  poly_vert = 4
    ##  pav_poly_bl_edge = matplotlib.patches.RegularPolygon((pavx, pavy), poly_vert,
    ##                                                    radius = 70,
    ##                                           fill = False, linewidth = .2,
    ##                                           edgecolor = "black")
    ##  pav_poly_edge = matplotlib.patches.RegularPolygon((pavx, pavy), poly_vert,
    ##                                                    radius = 60,
    ##                                           fill = False, linewidth = .4,
    ##                                           edgecolor = col_pav)
    ##  pav_poly_out = matplotlib.patches.RegularPolygon((pavx, pavy), poly_vert,
    ##                                                   radius = 43,
    ##                                           fill = False, linewidth = .5,
    ##                                           edgecolor = col_pav, alpha = 0.4)
    ##  pav_poly_in = matplotlib.patches.RegularPolygon((pavx, pavy), poly_vert,
    ##                                                  radius = 24,
    ##                                           fill = False, linewidth = .35,
    ##                                           edgecolor = "black", alpha = 0.25)
    ##
    ##  ax.add_artist(pav_poly_bl_edge)
    ##  ax.add_artist(pav_poly_edge)
    ##  ax.add_artist(pav_poly_out)
    ##  ax.add_artist(pav_poly_in)

    ## ax.annotate(r'$\textrm{non-JR}$',
    ##     transfer_coords(locate_baloon(non_jr_label_col, 's')),
    ##     xytext=transfer_coords((non_jr_label_col, vertical_cells*1.13)),
    ##     arrowprops=dict(edgecolor = None, linewidth=0.0625, width=0,
    ##       headwidth=1.3, headlength=1.2, color='black'), horizontalalignment='center',
    ## xycoords='axes fraction')

    ## ax.annotate(r'$\textrm{JR}$', transfer_coords(locate_baloon(jr_label_col, 'x')),
    ##     xytext=transfer_coords((jr_label_col, vertical_cells*1.13)),
    ##     arrowprops=dict(edgecolor = None, linewidth=0.0625, width=0,
    ##       headwidth=1.3, headlength=1.2, color='black'), horizontalalignment='center',
    ##     xycoords='axes fraction')

    ## ax.annotate(r'$\textrm{AV}$', transfer_coords((app_satisfaction, -2)),
    ## xycoords='axes fraction', horizontalalignment='center')

    ## ax.annotate(r'$\textrm{CC}$', transfer_coords((501, cc_coverage)),
    ## xycoords='axes fraction', verticalalignment='center')

    pav_label_y_move = -10
    phragmen_label_y_move = -2

    pav_data_coords = (
        pav_coords[0] * sq_len + sq_len / 2,
        pav_coords[1] * sq_len + sq_len / 2,
    )
    pavx, pavy = pav_data_coords

    phragmen_data_coords = (
        phragmen_coords[0] * sq_len + sq_len / 2,
        phragmen_coords[1] * sq_len + sq_len / 2,
    )
    phragmenx, phragmeny = phragmen_data_coords

    if phragmeny < pavy:
        pav_label_y_move, phragmen_label_y_move = (
            phragmen_label_y_move,
            pav_label_y_move,
        )

    phragmen_label_x_move = 37
    pav_label_x_move = 37

    if args.label_down:
        phragmen_label_x_move, pav_label_x_move = -20, -20
        pav_label_y_move = -30
        phragmen_label_y_move = -40

    pav_poly_in = matplotlib.patches.Circle(
        (pavx, pavy), radius=20, linewidth=0, color="black", alpha=0.5
    )
    ax.add_artist(pav_poly_in)

    pav_text_coords = (
        pavx + sq_len * pav_label_x_move,
        pavy + sq_len * pav_label_y_move,
    )
    ax.annotate(
        r"$\textrm{PAV}$",
        pav_data_coords,
        xycoords="data",
        arrowprops=dict(
            edgecolor=None,
            linewidth=0.0625,
            width=0,
            headwidth=2.5,
            headlength=3,
            color="black",
        ),
        xytext=pav_text_coords,
    )

    phragmen_poly_in = matplotlib.patches.Circle(
        (phragmenx, phragmeny), radius=20, linewidth=0, color="black", alpha=0.5
    )
    ax.add_artist(phragmen_poly_in)

    phragmen_text_coords = (
        phragmenx + sq_len * phragmen_label_x_move,
        phragmeny + sq_len * phragmen_label_y_move,
    )
    ax.annotate(
        r"$\textrm{Seq.\,Phr.}$",
        phragmen_data_coords,
        xycoords="data",
        arrowprops=dict(
            edgecolor=None,
            linewidth=0.0625,
            width=0,
            headwidth=2.5,
            headlength=3,
            color="black",
        ),
        xytext=phragmen_text_coords,
    )

    fig.tight_layout(pad=0)
    fig.savefig(out_filename, dpi=dpi)


def main(input_file, output_filename, args):
    experiment_data_file = input_file
    # result_files = [f for f in os.listdir(outputs_dir) if f.endswith(".outhit")]
    # result_stems = sorted(list(set(map(lambda f: "_".join(f.split("_")[:-1]), result_files))))
    # files_counter = 0
    # for result_file_stem in result_stems:
    #   files_counter = files_counter + 1
    # print "{} ({}/{})".format(result_file_stem, files_counter, len(result_stems))
    parse_exp_output(experiment_data_file, output_filename, args)


if __name__ == "__main__":
    args = getArgumentsParser().parse_args()
    out_file = args.outFile
    in_file = args.inputFile
    main(in_file, out_file, args)
