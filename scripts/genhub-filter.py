#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------
from __future__ import print_function
import argparse
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-x', '--exclude', metavar='XFILE', default=None,
                    help='file containing text patterns for identifying '
                    'features to exclude (a la `grep -vf`')
parser.add_argument('-t', '--fixtrna', action='store_true', help='NCBI FlyBase'
                    ' annotations do not have ID/Parent relationship properly '
                    'defined between tRNA features and the corresponding gene '
                    'features; use this option to fix these data')
parser.add_argument('-m', '--fixtrans', action='store_true', help='convert '
                    '`transcript` features to `mRNA` features')
parser.add_argument('-n', '--namedup', action='store_true', help='preprocess '
                    'with namedup')
parser.add_argument('-p', '--prefix', default=None, help='string to prepend to'
                    ' every sequence ID in the input')
parser.add_argument('-f', '--fixseq', metavar='GDNA', default=None,
                    help='genomic DNA file for correcting `##sequence-region` '
                    'pragmas')
parser.add_argument('-d', '--debug', action='store_true', help='debug mode')
parser.add_argument('infile')
parser.add_argument('outfile')
args = parser.parse_args()

cmds = list()
cmds.append('gunzip -c %s' % args.infile)
if args.exclude:
    cmds.append('grep -vf %s' % args.exclude)
if args.fixtrna:
    cmds.append('genhub-fix-trna.py')
if args.namedup:
    cmds.append('genhub-namedup.py')
if args.fixtrans:
    cmds.append("sed $'s/\ttranscript\t/\tmRNA\t/'")
cmds.append('tidygff3')
if args.prefix:
    cmds.append('genhub-format-gff3.py --prefix %s -' % args.prefix)
else:
    cmds.append('genhub-format-gff3.py -')
if args.fixseq:
    cmds.append('seq-reg.py - %s' % args.fixseq)
cmds.append('gt gff3 -sort -tidy -o %s -force' % args.outfile)

commands = ' | '.join(cmds)
if args.debug:
    print('[GenHub::genhub-filter.py] running command: %s' % commands,
          file=sys.stderr)

subprocess.check_call(commands, shell=True)
