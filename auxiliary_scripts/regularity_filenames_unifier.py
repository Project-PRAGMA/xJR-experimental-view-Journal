#!/usr/bin/env python

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

import sys
import os


def getOutputDataFiles(parentDir):
    filesList = filter(lambda x: x.endswith("out"), os.listdir(parentDir))
    return filesList


def collectParentDir():
    if len(sys.argv) != 2:
        print(
            "Usage:\n {} <PrefLibInputsDir>\n"
            "  <PrefLibInputsDir> A directory with input files\n".format(sys.argv[0])
        )
        exit(1)
    return os.path.abspath(sys.argv[1])


def renameFile(filename, parentPath):
    dataFile = os.path.join(parentPath, filename)
    with open(dataFile, "r") as dataFileHandler:
        distTypeAndParameterLine = dataFileHandler.readline().strip()
        seedLine = dataFileHandler.readline().strip()
    disType, parameterRemainder = distTypeAndParameterLine.split(",")
    if disType == "Impartial":
        disType = "imp"
    parameter = float(parameterRemainder.split(":")[1].strip())
    seed = int(seedLine.split(":")[1].strip())
    committeeType = filename.split(".")[0].split("_")[2]
    newFileName = "{}_{:3.2f}_{}_{}.out".format(disType, parameter, seed, committeeType)
    os.rename(dataFile, os.path.join(parentPath, newFileName))


def main():
    parentPath = collectParentDir()
    outFiles = getOutputDataFiles(parentPath)
    for f in outFiles:
        renameFile(f, parentPath)


if __name__ == "__main__":
    main()
