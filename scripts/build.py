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

buildcmds = 'download format datatypes stats cleanup'.split(' ')


def download_task(conf, workdir='.', logstream=sys.stderr):
    for label in sorted(conf):
        config = conf[label]
        subprocess.call(['mkdir', '-p', workdir + '/' + label])
        assert 'source' in config, \
            'data source unspecified for genome "%s"' % label
        source = config['source']
        assert source in ['ncbi', 'ncbi_flybase', 'custom'], \
            'unrecognized data source "%s"' % source

        if source == 'ncbi':
            if 'scaffolds' in config:
                genomefunc = genhub.ncbi.download_scaffolds
            elif 'chromosomes' in config:
                genomefunc = genhub.ncbi.download_chromosomes
            else:
                raise Exception('genome sequence configured incorrectly for '
                                'genome "%s"' % label)
            genomefunc(label, config, workdir=workdir, logstream=logstream)
            genhub.ncbi.download_annotation(label, config, workdir=workdir,
                                            logstream=logstream)
            genhub.ncbi.download_proteins(label, config, workdir=workdir,
                                          logstream=logstream)
        elif source == 'custom':
            mod = importlib.import_module('genhub.' + config['module'])
            mod.download(label, config, workdir=workdir, logstream=logstream)
        else:
            raise NotImplementedError('handling of "%s" genomes not yet '
                                      'implemented' % source)


def format_task(conf, workdir='.', logstream=sys.stderr):
    for label in sorted(conf):
        config = conf[label]
        specdir = '%s/%s' % (workdir, label)
        assert os.path.isdir(specdir), \
            'directory for %s has not yet been initialized' % label

        genhub.format.gdna(label, config, workdir=workdir, logstream=logstream)
        genhub.format.proteins(label, config, workdir=workdir,
                               logstream=logstream)


def get_parser():
    desc = 'Run the main GenHub build process.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-w', '--workdir', metavar='WD', default='./species',
                        help='working directory for data files; default is '
                        '"./species"')
    confargs = parser.add_mutually_exclusive_group()
    confargs.add_argument('-c', '--cfg', default=None, metavar='CFG',
                          type=argparse.FileType('r'), help='Provide all '
                          'genome configurations in a single file')
    confargs.add_argument('--cfgdir', default=None, metavar='DIR', help='Load '
                          'genome configs from all .yml files in a directory')
    parser.add_argument('cmd', nargs='+', choices=buildcmds, metavar='cmd',
                        help='Build command(s) to execute; options include '
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

    if 'download' in args.cmd:
        download_task(conf, workdir=args.workdir)
    if 'format' in args.cmd:
        format_task(conf, workdir=args.workdir)


if __name__ == '__main__':
    main()
