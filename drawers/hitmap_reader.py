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


def parse_results_file(filename):
    exp_data = []
    description = []
    with open(filename, "r") as results_file:
        for _ in range(10):
            description.append(results_file.readline().strip())
        for data_line in results_file:
            tupled_line = [tuple(x) for x in data_line.strip()]
            exp_data.append(tupled_line)
    return description, reversed(exp_data)


def get_max_cc_and_app(description):
    for line in description:
        if line.startswith("Max coverage"):
            cc_coverage = int(line.split(":")[1].strip())
        if line.startswith("Max approval"):
            app_satisfaction = int(line.split(":")[1].strip())
    return cc_coverage, app_satisfaction


def parse_hitmap_output(data_filename):
    description, data = parse_results_file(data_filename)
    cc_coverage, app_satisfaction = get_max_cc_and_app(description)

    return data, cc_coverage, app_satisfaction
