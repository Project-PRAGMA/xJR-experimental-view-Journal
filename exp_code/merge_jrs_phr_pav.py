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


def copy_phr_pav_to_general_map(
    general_map_file, phragmen_map_file, pav_map_file, outcome_dir, instance_name
):
    try:
        with open(phragmen_map_file, "r") as phr:
            with open(pav_map_file, "r") as pav:
                phr_content = phr.readlines()
                pav_content = pav.readlines()
                for i in range(10, len(phr_content)):
                    if (c := phr_content[i].find("p")) > 0:
                        phr_place = (i, c)
                for i in range(10, len(pav_content)):
                    if (c := pav_content[i].find("v")) > 0:
                        pav_place = (i, c)

                with open(general_map_file, "r") as gen:
                    gen_content = gen.readlines()

                print(phr_place)
                print(pav_place)
                print(len(gen_content))
                gen_content[phr_place[0]] = (
                    gen_content[phr_place[0]][: phr_place[1]]
                    + "p"
                    + gen_content[phr_place[0]][phr_place[1] + 1 :]
                )
                gen_content[pav_place[0]] = (
                    gen_content[pav_place[0]][: pav_place[1]]
                    + "v"
                    + gen_content[pav_place[0]][pav_place[1] + 1 :]
                )

                with open(outcome_dir + "/" + instance_name + ".outhit", "w") as gen:
                    gen.writelines(gen_content)
                # Read and write character by character
            ## while True:
            ##   char = source.read(1)  # Read one character
            ##   if not char:  # If end of file is reached
            ##     break
            ##   destination.write(char)  # Write the character to destination file
    ## print("File copied successfully!")
    except FileNotFoundError as e:
        print("File not found!")
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Copy PHR and PAV results to " "general map"
    )
    parser.add_argument("-i", "--instance_name", help="Path to the general map")
    parser.add_argument(
        "-o", "--outcome_dir", required=True, help="Directory for outcomes"
    )
    args = parser.parse_args()

    outcome_dir = args.outcome_dir

    base = "../temporary-hitmaps/"

    gen_file = base + args.instance_name + "_xJR.outhit"
    phr_file = base + args.instance_name + "_PHR.outhit"
    pav_file = base + args.instance_name + "_PAV.outhit"

    copy_phr_pav_to_general_map(
        gen_file, phr_file, pav_file, outcome_dir, args.instance_name
    )
