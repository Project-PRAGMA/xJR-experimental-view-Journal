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


FILESDIR="results"
SEEDS=( 44 77 88 )
CULTURES=( "GA" "IC" "1D" "2D" )

DRAWER_EXEC="../../drawers/hitmapDrawer.py"

PICSDIR="pics"

if [ ! -d ${PICSDIR} ]; then
  echo "Directory" ${PICSDIR} "does not exist."
	exit 1
fi

for SEED in ${SEEDS[@]}; do
	for CULTURE in ${CULTURES[@]}; do
		if [[ $CULTURE == GA ]]; then
			XLIM=450
		else
			XLIM=250
		fi
  	echo ${DRAWER_EXEC} -c100 -a1000 -if ${FILESDIR}/${FILE} -of ${PICSDIR}/${FILE%%.*}".png"
  	${DRAWER_EXEC} -c100 -a${XLIM} \
		-if ${FILESDIR}/s${SEED}_cultures/${CULTURE}_c10_s${SEED}.outhit \
	 	-of ${PICSDIR}/${CULTURE}_c10_s${SEED}.pdf
	done
done

