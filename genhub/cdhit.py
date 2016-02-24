#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2016   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Module for handling cd-hit output."""

from __future__ import print_function
import re


class ClusterSeq(object):
    """Object representing a sequence entry in a cd-hit cluster."""

    def __init__(self, line):
        self.rawdata = line.rstrip()
        values = re.compile("\s+").split(self.rawdata)
        self.index = int(values[0])
        self.length = int(values[1][:-3])
        self.defline = values[2]

    @property
    def accession(self):
        """
        Parse accession number from commonly supported formats.

        If the defline does not match one of the following formats, the entire
        description (sans leading caret) will be returned.

        * >gi|572257426|ref|XP_006607122.1|
        * >gnl|Tcas|XP_008191512.1
        * >lcl|PdomMRNAr1.2-10981.1
        """
        if self.defline.startswith('>gi|'):
            acc = re.match('>gi\|\d+\|[^\|]+\|([^\|\n]+)', self.defline) \
                        .group(1)
        elif self.defline.startswith('>gnl|'):
            acc = re.match('>gnl\|[^\|]+\|([^\|\n]+)', self.defline).group(1)
        elif self.defline.startswith('lcl|'):
            acc = re.match('>lcl\|([^\|\n]+)', self.defline).group(1)
        else:
            acc = self.defline[1:]

        if acc.endswith('...'):
            acc = acc[:-3]
        return acc

    def __len__(self):
        return self.length

    def __str__(self):
        return self.rawdata

    def __repr__(self):
        return self.accession


def parse_clusters(filehandle):
    """
    Iterate over clusters from a CD-HIT output file.

    Yields the cluster ID (a numeric string) and a list of sequence objects.
    """
    clusterid = None
    clusterseqs = list()
    for line in filehandle:
        if line.startswith('>'):
            if clusterid is not None:
                yield clusterid, clusterseqs
            clusterid = line.rstrip()[9:]  # Strip '>Cluster ' from front
            clusterseqs = list()
        else:
            seqinfo = ClusterSeq(line)
            clusterseqs.append(seqinfo)

    yield clusterid, clusterseqs
