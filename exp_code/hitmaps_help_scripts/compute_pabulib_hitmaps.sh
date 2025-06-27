#!/usr/bin/env bash

################################################################################
#Copyright 2025 Andrzej Kaczmarczyk<droodev@gmail.com>
#
#The MIT License
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the “Software”), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#the Software, and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
################################################################################



OUTDIR="../temporary-hitmaps"
K=10 # Committee size
M=0 # Candidates
N=100 # Voters
VERBOSE="-v"
LOGLEVEL="INFO"
METHOD="PAV"

methods=("PAV" "PHR" "xJR")
datasets=(\
    "poland_warszawa_2020_bialoleka"\
    "poland_warszawa_2021_bielany"\
    "poland_warszawa_2020_mokotow"\
    "poland_warszawa_2021_ursynow"\
    "poland_warszawa_2020_praga-poludnie"\
    "poland_warszawa_2021_wawer"\
    "poland_warszawa_2020_ursynow"\
    "poland_warszawa_2021_wola"\
    "poland_warszawa_2020_wawer"\
    "poland_warszawa_2022_bielany"\
    "poland_warszawa_2021_bialoleka"\
    "poland_warszawa_2022_wawer"\
    "poland_warszawa_2021_praga-poludnie"\
)

for dataset in "${datasets[@]}"; do
    for method in "${methods[@]}"; do
        outfile="${dataset}_${method}"
        infile="../../pabulib/${dataset}.pb"
        ../hitmapRunner.py -od "$OUTDIR" -k"$K" -m"$M" -n"$N" $VERBOSE -ll "$LOGLEVEL" -d "IC" -of "$outfile" -r "$method" -i "$infile" 
    done
done
