#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2016   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

from __future__ import print_function
from __future__ import division
import argparse
import re
import sys
import genhub


def cli():
    """Define the command-line interface of the program."""
    desc = 'Calculate measures of "compactness" for the specified genome(s).'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-v', '--version', action='version',
                        version='GenHub v%s' % genhub.__version__)
    parser.add_argument('-c', '--cfgdir', default=None, metavar='DIR',
                        help='directory (or comma-separated list of '
                        'directories) from which to load user-supplied genome '
                        'configuration files')
    parser.add_argument('-w', '--workdir', metavar='WD', default='./species',
                        help='working directory for data files; default is '
                        '"./species"')
    parser.add_argument('-l', '--length', metavar='LEN', type=int,
                        default=1000000, help='minimum length threshold; '
                        'default is 1000000 (1Mb)')
    parser.add_argument('species', nargs='+', help='species label(s)')
    return parser


def ilocus_type(record):
    typematch = re.search('iLocus_type=([^;\n]+)', record)
    assert typematch
    return typematch.group(1)


def seq_info(db):
    with open(db.ilocusfile) as infile:
        seqlengths = dict()
        gilocus_counts = dict()
        for line in infile:
            if line.startswith('##sequence-region'):
                seqreg = re.search('##sequence-region\s+(\S+)\s+(\d+)\s+(\d+)',
                                   line)
                assert seqreg
                seqid = seqreg.group(1)
                start = int(seqreg.group(2))
                end = int(seqreg.group(3))
                assert start == 1
                seqlengths[seqid] = end
            elif '\tlocus\t' in line:
                values = line.split('\t')
                assert len(values) == 9
                assert values[2] == 'locus'
                seqid = values[0]
                attrs = values[8]
                locustype = ilocus_type(attrs)
                if locustype in ['siLocus', 'ciLocus', 'niLocus']:
                    if seqid not in gilocus_counts:
                        gilocus_counts[seqid] = 0
                    gilocus_counts[seqid] += 1

    return seqlengths, gilocus_counts


def milocus_info(db):
    with open(db.milocusfile) as infile:
        milocus_occ = dict()
        singleton_count = dict()
        for line in infile:
            values = line.split('\t')
            assert len(values) == 9
            assert values[2] == 'locus'
            seqid = values[0]
            start = int(values[3]) - 1
            end = int(values[4])
            attrs = values[8]
            locustype = ilocus_type(attrs)
            if locustype == 'miLocus':
                length = end - start
                if seqid not in milocus_occ:
                    milocus_occ[seqid] = 0
                milocus_occ[seqid] += length
            elif locustype in ['siLocus', 'ciLocus', 'niLocus']:
                if seqid not in singleton_count:
                    singleton_count[seqid] = 0
                singleton_count[seqid] += 1
    return milocus_occ, singleton_count


def main(args):
    print('Species', 'SeqID', 'Sigma', 'Phi', sep='\t')

    registry = genhub.registry.Registry()
    if args.cfgdir:
        for cfgdirpath in args.cfgdir.split(','):
            registry.update(cfgdirpath)
    conf = registry.genomes(args.species)

    for species in args.species:
        config = conf[species]
        db = genhub.genomedb.GenomeDB(species, config, workdir=args.workdir)
        seqlengths, gilocus_counts = seq_info(db)
        milocus_occ, singleton_count = milocus_info(db)
        for seqid in seqlengths:
            length = seqlengths[seqid]
            if length < args.length:
                continue
            milocus_space = milocus_occ[seqid]
            giloci = gilocus_counts[seqid]
            nonsingletons = giloci - singleton_count[seqid]
            sigma = milocus_occ[seqid] / length
            phi = nonsingletons / giloci

            print(species, seqid, sigma, phi, sep='\t')

if __name__ == '__main__':
    main(args=cli().parse_args())
