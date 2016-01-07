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
    confargs = parser.add_mutually_exclusive_group()
    confargs.add_argument('-c', '--cfg', default=None, metavar='CFG',
                          type=argparse.FileType('r'), help='Provide all '
                          'genome configurations in a single file')
    confargs.add_argument('--cfgdir', default=None, metavar='DIR', help='Load '
                          'genome configs from all .yml files in a directory')
    parser.add_argument('task', nargs='+', choices=buildcmds, metavar='task',
                        help='Build task(s) to execute; options include '
                        '"%s"' % '", "'.join(buildcmds))
    return parser


def main(parser=get_parser()):
    args = parser.parse_args()
    if args.cfg:
        conf = genhub.conf.load_file(args.cfg)
    elif args.cfgdir:
        conf = genhub.conf.load_dir(args.cfgdir)
    else:
        print('error: must specify config file or directory', file=sys.stderr)

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
