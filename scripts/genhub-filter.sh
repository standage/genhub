#!/usr/bin/env bash
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------
set -eo pipefail

infile=$1
outfile=$2
filterstr=$3

filtercmd="cat"
if [ "$filterstr" != "nofilter" ]; then
    filtercmd="grep -Ev $filterstr"
fi

gunzip -c $infile \
    | $filtercmd \
    | tidygff3 \
    | python scripts/genhub-format-gff3.py - \
    | gt gff3 -sort -tidy -o $outfile -force
