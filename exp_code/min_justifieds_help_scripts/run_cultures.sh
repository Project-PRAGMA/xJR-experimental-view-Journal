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


CULTURES=( "GA" "IC" "1D" "2D" )

EXP_EXEC="../avgMinJustGroup.py"

RESULTS_DIR="../../exp_results/min_justified"

if [ ! -d ${RESULTS_DIR} ]; then
  echo "Directory" ${RESULTS_DIR} "does not exist."
	exit 1
fi

for CULTURE in ${CULTURES[@]}; do
  OUTPATH="${RESULTS_DIR}/${CULTURE}_output_k2-15.minjr"

	${EXP_EXEC} -m15 -n10 -t 1 \
    -a JR PJR EJR -d ${CULTURE} \
 	  -of ${OUTPATH} 
done
