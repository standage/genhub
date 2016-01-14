#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015-2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015-2016   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

from __future__ import print_function
import argparse
import importlib
import os
import subprocess
import sys
import genhub

buildcmds = 'download format prepare stats cleanup'.split(' ')
sources = ['refseq', 'ncbi_flybase', 'beebase', 'crg', 'pdom']
dbtype = {'refseq': genhub.refseq.RefSeqDB,
          'ncbi_flybase': genhub.ncbi_flybase.FlyBaseDB,
          'beebase': genhub.beebase.BeeBaseDB,
          'crg': genhub.crg.CrgDB,
          'pdom': genhub.pdom.PdomDB}


def get_parser():
    desc = 'Run the main GenHub build process.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-v', '--version', action='version',
                        version='GenHub v%s' % genhub.__version__)
    parser.add_argument('-w', '--workdir', metavar='WD', default='./species',
                        help='working directory for data files; default is '
                        '"./species"')
    parser.add_argument('-c', '--cfgdir', default=None, metavar='DIR',
                        help='Directory (or comma-separated list of '
                        'directories) from which to load user-supplied genome '
                        'configuration files')
    confargs = parser.add_mutually_exclusive_group()
    confargs.add_argument('-g', '--genome', default=None, metavar='LBL',
                          help='Label (or comma-separated set of labels) '
                          'specifying the genome(s) to process; more '
                          'information available by executing the command '
                          '`genhub-genomes.py -h`')
    confargs.add_argument('-l', '--list', default=None, metavar='LBL',
                          help='Label of a list of genomes to process; more '
                          'information available by executing the command '
                          '`genhub-genomes.py -h`')
    parser.add_argument('task', nargs='+', choices=buildcmds, metavar='task',
                        help='Build task(s) to execute; options include '
                        '"%s"' % '", "'.join(buildcmds))
    return parser


def main(parser=get_parser()):
    args = parser.parse_args()
    if args.cfgdir:
        args.cfgdir = args.cfgdir.split(',')
    if args.genome:
        labels = args.genome.split(',')
        conf = genhub.conf.load_genomes(labels, args.cfgdir)
    elif args.list:
        conf = genhub.conf.load_genome_list(args.list, args.cfgdir)
    else:
        message = 'must specify a genome or genome list to process'
        raise ValueError(message)

    for label in sorted(conf):
        config = conf[label]
        assert 'source' in config
        assert config['source'] in sources
        constructor = dbtype[config['source']]
        db = constructor(label, config, workdir=args.workdir)

        if 'download' in args.task:
            db.download()
        if 'format' in args.task:
            db.format()
        if 'prepare' in args.task:
            genhub.iloci.prepare(db)
            genhub.proteins.prepare(db)
            genhub.mrnas.prepare(db)
            genhub.exons.prepare(db)
        if 'stats' in args.task:
            genhub.stats.compute(db)

        print('[GenHub: %s] build complete!' % config['species'],
              file=sys.stderr)


if __name__ == '__main__':
    main()
