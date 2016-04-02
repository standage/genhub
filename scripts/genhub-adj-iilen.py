#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2016   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2016   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

from __future__ import division
import argparse
import matplotlib.pyplot as plt
import numpy
import pandas
import seaborn
from collections import deque
import genhub


def check_float(x):
    f = float(x)
    if f < 0.0 or f > 1.0:
        message = x + ' not in the range [0.0, 1.0]'
        raise argparse.ArgumentTypeError(message)
    return f


def cli():
    """Define the command-line interface of the program."""
    desc = 'Summarize iLocus content of the specified genome(s)'
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
    parser.add_argument('-n', '--nrange', metavar='X Y', type=int, nargs=2,
                        default=[1, 10], help='range of n values to consider; '
                        'default is "1 10"')
    parser.add_argument('-m', '--maxlenqnt', metavar='M', type=check_float,
                        default=0.95, help='quantile at which outliers in the '
                        'long tail of the iiLocus length distribution will be '
                        'discarded; default is 0.95; set to 0 to disable the '
                        'filter')
    parser.add_argument('-x', '--xrange', type=int, nargs=2, metavar='MN MX',
                        default=None, help='restrict the x-axis of the plotted'
                        ' histograms to the specified range')
    parser.add_argument('species', help='species label(s)')
    return parser


def len_consec_iiloci(data, n=2, filt=None):
    """
    Compute combined lengths for each set of n consecutive iiLoci.

    Iterate over iiLoci, accumulating sets of n consecutive iiLoci in a deque
    and yield the aggregate length of each set of n. Reset the deque when a new
    sequence is encountered.

    `data` is a pandas.DataFrame object, each row corresponding to a single
    iiLocus.

    `filt` is an (optional) maximum length threshold. If set, iiLoci whose
    length exceeds the thredhold will be discarded.
    """
    iiloci = deque()
    for index, row in data.iterrows():
        if filt and row['Length'] > filt:
            continue
        if len(iiloci) > 0 and iiloci[0]['SeqID'] != row['SeqID']:
            iiloci = deque()
        iiloci.append(row)
        if len(iiloci) == n:
            aggregate_length = sum([ilocus['Length'] for ilocus in iiloci])
            yield aggregate_length
            iiloci.popleft()


def make_hist(data, log10=False, bins=40, xlab=None, ylab=None,
              xlim=None, ylim=None, title=None, color='grey'):
    if xlim:
        data = [dat for dat in data if dat < xlim[1]]
    if log10:
        plot = plt.hist(numpy.log10(data), bins=bins, color=color)
    else:
        plot = plt.hist(data, bins=bins, color=color)
    seaborn.despine(left=True)
    if xlab is not None:
        _ = plt.xlabel(xlab, fontsize=18)
    if ylab is not None:
        _ = plt.ylabel(ylab, fontsize=18)
    if xlim is not None:
        _ = plt.xlim(xlim[0], xlim[1])
    if ylim is not None:
        _ = plt.ylim(ylim[0], ylim[1])
    if title:
        plt.title(title, fontsize=20)
    if filename:
        plot.savefig(filename)
    else:
        plt.show()


def main(args):
    registry = genhub.registry.Registry()
    if args.cfgdir:
        for cfgdirpath in args.cfgdir.split(','):
            registry.update(cfgdirpath)
    conf = registry.genomes(args.species)

    config = conf[args.species]
    db = genhub.genomedb.GenomeDB(args.species, config, workdir=args.workdir)
    data = pandas.read_table(db.ilocustable)
    iiloci = data.loc[data.LocusClass == 'iiLocus']
    maxlen = 0
    if args.maxlenqnt:
        maxlen = int(iiloci['Length'].quantile(args.maxlenqnt))
        print('Max iiLocus length: {} bp'.format(maxlen))
    print(iiloci.head())

    for k in range(args.nrange[0], args.nrange[1] + 1):
        title = '{} Consecutive iiLoci ({})'.format(k, args.species)
        filename = '{}.{}.png'.format(args.species, k)
        agglens = [x for x in len_consec_iiloci(iiloci, n=k, filt=maxlen)]
        make_hist(agglens, xlab='Aggregate Length (bp)', ylab='Frequency',
                  title=title, xlim=xrange, filename=filename)


if __name__ == '__main__':
    main(args=cli().parse_args())
