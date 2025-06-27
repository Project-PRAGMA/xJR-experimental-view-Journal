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


./xJRProbability.py -of ../exp_results/xJR_prob/experiment_results/IC.xjrprob -k 2 -t 2 -n 10 -m 10 -d IC 

./xJRProbability.py -of ../exp_results/xJR_prob/experiment_results/1D.xjrprob -k 2 -t 2 -n 10 -m 10 -d 1D 

./xJRProbability.py -of ../exp_results/xJR_prob/experiment_results/2D.xjrprob -k 2 -t 2 -n 10 -m 10 -d 2D 

./xJRProbability.py -of ../exp_results/xJR_prob/experiment_results/GA.xjrprob -k 2 -t 2 -n 10 -m 10 -d GA 

./xJRProbability.py -of ../exp_results/xJR_prob/experiment_results/pabulib_13_sets.xjrprob -k 2 -t 2 -n 10 -m 10 -d GA -ed ../pabulib
