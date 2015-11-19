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
import re
import sys


def process_gff3(fp):
    trnas = {}
    for line in fp:
        line = line.rstrip()
        fields = line.split("\t")
        if len(fields) != 9:
            yield line
            continue
        if fields[2] == "gene" and "gene=tRNA" in fields[8]:
            geneid = re.search("Name=tRNA:([^;\n]+)", fields[8]).group(1)
            fields[8] = "ID=gene.trna.%s;%s" % (geneid, fields[8])
            yield "\t".join(fields)
            continue
        elif fields[2] == "tRNA":
            geneid = re.search("Note=tRNA:(.+?)-RA", fields[8]).group(1)
            fields[8] = "Parent=gene.trna.%s;%s" % (geneid, fields[8])
            if geneid in trnas:
                otherfields = trnas[geneid]
                fields[3] = min(fields[3], otherfields[3])
                fields[4] = max(fields[4], otherfields[4])
            trnas[geneid] = fields
            continue
        yield line

    for geneid in trnas:
        yield "\t".join(trnas[geneid])

if __name__ == "__main__":
    for line in process_gff3(sys.stdin):
        print(line)
