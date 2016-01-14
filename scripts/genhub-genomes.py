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
import genhub


def print_genome(label, config):
    print(label, config['species'], sep='\t', end='')
    if 'common' in config:
        print('\t', config['common'], end='')
    print('')


def get_parser():
    desc = 'Explore genomes available with GenHub.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-v', '--version', action='version',
                        version='GenHub v%s' % genhub.__version__)
    parser.add_argument('-c', '--cfgdir', default=None, metavar='DIR',
                        help='Directory (or comma-separated list of '
                        'directories) from which to load user-supplied genome '
                        'configuration files')
    parser.add_argument('-g', '--genomesonly', action='store_true',
                        help='Show individual genomes only')
    parser.add_argument('-l', '--listsonly', action='store_true',
                        help='Show genome lists only')
    return parser


def main(args):
    if args.cfgdir:
        args.cfgdir = args.cfgdir.split(',')

    if not args.listsonly:
        print('===== Genomes =====')
        for label, config in genhub.conf.find_genomes(args.cfgdir):
            print_genome(label, config)
        print('')

    if not args.genomesonly:
        print('===== Genome lists =====')
        for label in genhub.conf.find_lists(args.cfgdir):
            print(label)


if __name__ == '__main__':
    main(get_parser().parse_args())
