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
import multiprocessing
import os
import subprocess
import sys
import genhub

buildcmds = ['list', 'download', 'format', 'prepare', 'stats', 'cluster',
             'cleanup']
sources = ['refseq', 'ncbi_flybase', 'beebase', 'crg', 'pdom', 'tair', 'am10']
dbtype = {'refseq': genhub.refseq.RefSeqDB,
          'ncbi_flybase': genhub.ncbi_flybase.FlyBaseDB,
          'beebase': genhub.beebase.BeeBaseDB,
          'crg': genhub.crg.CrgDB,
          'pdom': genhub.pdom.PdomDB,
          'tair': genhub.tair.TairDB,
          'am10': genhub.am10.Am10DB}


def getdb(label, config, args):
    assert 'source' in config
    assert config['source'] in sources
    constructor = dbtype[config['source']]
    db = constructor(label, config, workdir=args.workdir)
    return db


def list_configs(registry):
    print('===== Genome configurations =====')
    for label, config in registry.list_genomes():
        print(label, config['species'], sep='\t', end='')
        if 'common' in config:
            print('\t', config['common'], end='')
        print('')
    print('')

    print('===== Batch configurations =====')
    for label, batch in registry.list_batches():
        print(label, '\t', ','.join(batch))


def run_build(builddata):
    label, config, args = builddata
    db = getdb(label, config, args)

    if 'download' in args.task:
        db.download()
    if 'format' in args.task:
        db.format()
    if 'prepare' in args.task:
        genhub.iloci.prepare(db, delta=args.delta, ilcformat=args.format)
        genhub.proteins.prepare(db)
        genhub.mrnas.prepare(db)
        genhub.exons.prepare(db)
    if 'stats' in args.task:
        genhub.stats.compute(db)
    if 'cleanup' in args.task:
        db.cleanup(args.keep, args.fullclean)

    print('[GenHub: %s] build complete!' % db.config['species'],
          file=sys.stderr)


def cluster_proteins(dbs, np=1):
    print('[GenHub] aggregating representative proteins', file=sys.stderr)
    protmap = dict()
    with open('GenHub.prot.fa', 'w') as outstream:
        for db in dbs:
            protfile = '%s/%s.prot.fa' % (db.dbdir, db.label)
            with open(protfile, 'r') as instream:
                for line in instream:
                    print(line, end='', file=outstream)
            for protid, locid in db.get_prot_map():
                protmap[protid] = locid

    print('[GenHub] clustering representative proteins', file=sys.stderr)
    command = ('cd-hit -i GenHub.prot.fa -o GenHub.prot -T %d -d 0 '
               '-c 0.50 -s 0.65 -p 1 -n 3 -aL 0.75 -aS 0.85 -g 1' % np).split()
    subprocess.check_call(command)

    with open('GenHub.prot.clstr', 'r') as infile, \
            open('GenHub.hiloci.tsv', 'w') as outfile:
        for clusterid, clusterseqs in genhub.cdhit.parse_clusters(infile):
            iloci = [protmap[prot.accession] for prot in clusterseqs]
            species = set([prot.species for prot in clusterseqs])
            print(len(iloci), len(species), ','.join(iloci), ','.join(species),
                  sep='\t', file=outfile)


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
    parser.add_argument('-p', '--numprocs', metavar='P', type=int, default=1,
                        help='number of processors to use when processing '
                        'multiple genomes; default is 1')
    parser.add_argument('-d', '--delta', type=int, metavar='DLT', default=500,
                        help='iLocus extension parameter; default is 500')
    parser.add_argument('--keep', metavar='PTN', nargs='+',
                        help='keep files matching the specified pattern PTN '
                        'when running the `cleanup` build task')
    parser.add_argument('--fullclean', action='store_true',
                        help='when running the `cleanup` build task, delete '
                        'original (downloaded) data files as well as processed'
                        ' data files')
    parser.add_argument('-f', '--format', metavar='PFX', default='{}ILC-%05lu',
                        help='format for assigning serial labels to iLoci; '
                        'must include the placeholder {} for the species '
                        'label, as well as a printf-style placeholder for a '
                        'serial number; default is "{}ILC-%%05lu"')
    confargs = parser.add_mutually_exclusive_group()
    confargs.add_argument('-g', '--genome', default=None, metavar='LBL',
                          help='Label (or comma-separated set of labels) '
                          'specifying the genome(s) to process; use the'
                          '`list` task to show all available genomes')
    confargs.add_argument('-b', '--batch', default=None, metavar='LBL',
                          help='Label of a batch of genomes to process; use '
                          'the `list` task to show all available '
                          'batches')
    parser.add_argument('task', nargs='+', choices=buildcmds, metavar='task',
                        help='Build task(s) to execute; options include '
                        '"%s"' % '", "'.join(buildcmds))
    return parser


def main(args):
    registry = genhub.registry.Registry()
    if args.cfgdir:
        for cfgdirpath in args.cfgdir.split(','):
            registry.update(cfgdirpath)

    if 'list' in args.task:
        list_configs(registry)
        sys.exit(0)

    if args.genome:
        labels = args.genome.split(',')
        conf = registry.genomes(labels)
        assert conf is not None, 'unknown genome label(s) "%s"' % args.genome
    elif args.batch:
        conf = registry.batch(args.batch)
        assert conf is not None, 'unknown batch label "%s"' % args.batch
    else:
        message = ('must specify a genome or batch of genomes to process, '
                   'or `list` to show available genomes')
        raise ValueError(message)

    builds = list()
    for label in sorted(conf):
        builddata = (label, conf[label], args)
        builds.append(builddata)
    pool = multiprocessing.Pool(processes=args.numprocs)
    results = [pool.apply_async(run_build, args=(b,)) for b in builds]
    _ = [p.get() for p in results]

    if 'cluster' in args.task:
        dbs = [getdb(label, conf[label], args) for label in sorted(conf)]
        cluster_proteins(dbs, args.numprocs)

    print('[GenHub] all builds complete!', file=sys.stderr)


if __name__ == '__main__':
    main(get_parser().parse_args())
