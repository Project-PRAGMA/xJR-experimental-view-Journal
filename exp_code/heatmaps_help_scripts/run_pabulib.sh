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


RESULTSDIR="../../exp_results/heatmap/results"
PABUDIR="../../pabulib/"
ALLFILES=(\
  "poland_warszawa_2020_bialoleka.pb"\
  "poland_warszawa_2021_bielany.pb"\
  "poland_warszawa_2020_mokotow.pb"\
  "poland_warszawa_2021_ursynow.pb"\
  "poland_warszawa_2020_praga-poludnie.pb"\
  "poland_warszawa_2021_wawer.pb"\
  "poland_warszawa_2020_ursynow.pb"\
  "poland_warszawa_2021_wola.pb"\
  "poland_warszawa_2020_wawer.pb"\
  "poland_warszawa_2022_bielany.pb"\
  "poland_warszawa_2021_bialoleka.pb"\
  "poland_warszawa_2022_wawer.pb"\
  "poland_warszawa_2021_praga-poludnie.pb"\
)

EXP_EXEC="../heatmapRunner.py"

if [ ! -d ${RESULTSDIR} ]; then
  echo "Directory" ${RESULTSDIR} "does not exist."
	exit 1
fi

for FILE in ${ALLFILES[@]}; do
	if [[ $FILE == poland_warszawa_2021_wola.pb ]]; then
		XLIM=300
	else
		XLIM=250
	fi
    ${EXP_EXEC} -m100 -n100 -k10 -t 100000 -c100 -a${XLIM} \
		-d GA -ll DEBUG \
		-if ${PABUDIR}/${FILE} \
	  -of ${RESULTSDIR}/${FILE%%.*}".heatmap"
done
