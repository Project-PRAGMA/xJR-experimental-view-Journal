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
ALLFILES=(\
  "poland_warszawa_2021_bialoleka.outhit"\
	"poland_warszawa_2020_bialoleka.outhit"\
 	"poland_warszawa_2021_bielany.outhit"\
  "poland_warszawa_2020_mokotow.outhit"\
 	"poland_warszawa_2021_ursynow.outhit"\
  "poland_warszawa_2020_praga-poludnie.outhit"\
	"poland_warszawa_2021_wawer.outhit"\
  "poland_warszawa_2020_ursynow.outhit"\
	"poland_warszawa_2021_wola.outhit"\
  "poland_warszawa_2020_wawer.outhit"\
	"poland_warszawa_2022_bielany.outhit"\
	"poland_warszawa_2022_wawer.outhit"\
)

DRAWER_EXEC="../../drawers/hitmapDrawer.py"

PICSDIR="pics"

if [ ! -d ${PICSDIR} ]; then
  echo "Directory" ${PICSDIR} "does not exist."
	exit 1
fi

for FILE in ${ALLFILES[@]}; do
	if [[ $FILE == poland_warszawa_2021_wola.outhit ]]; then
		XLIM=300
	else
		XLIM=250
	fi
	if [[ $FILE == poland_warszawa_2021_bialoleka.pb ]]; then
		LABELSDOWN="True"
	else
		LABELSDOWN="False"
	fi
	echo ${FILE}
	${DRAWER_EXEC} -lb ${LABELSDOWN} -ms True\
		-c100 -a${XLIM} -if ${FILESDIR}/${FILE} -of ${PICSDIR}/${FILE%%.*}".pdf"
done

