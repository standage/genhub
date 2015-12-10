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
import re
import sys


def parse_args():
    """Define the command-line interface."""
    sources = ['refseq', 'ncbi_flybase', 'beebase', 'crg', 'pdom']
    desc = 'Filter features and parse accession values'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument('-p', '--prefix', default=None,
                        help='attach the given prefix to each sequence ID')
    parser.add_argument('-s', '--source', default='refseq', choices=sources,
                        help='data source; default is "refseq"')
    parser.add_argument('gff3', type=argparse.FileType('r'))
    return parser.parse_args()


def match_filter(line, source):
    if source in ['refseq', 'ncbi_flybase']:
        for filt in ['\tregion\t', '\tmatch\t', '\tcDNA_match\t', '##species']:
            if filt in line:
                return True
    return False


def pseudogenic_cds(line):
    """
    Test whether the given entry is a pseudogene-associated CDS.

    We want to ignore these!
    """
    fields = line.split('\t')
    if len(fields) != 9:
        return False

    ftype = fields[2]
    attributes = fields[8]
    if ftype == 'CDS' and 'pseudo=true' in attributes:
        return True
    return False


def parse_gene_accession(line, source, vdj_segments):
    """
    Parse accession for gene features.

    Note that for genes involved in V(D)J recombination, the CDS sub-features
    are direct children. `vdj_segments` is provided to query these
    relationships.
    """
    if '\tgene\t' not in line or source == 'beebase':
        return line

    accmatch = None
    if source in ['refseq', 'ncbi_flybase']:
        accmatch = re.search('GeneID:([^;,\n]+)', line)
    elif source == 'crg':
        accmatch = re.search('ID=([^;\n]+)', line)
    elif source == 'pdom':
        accmatch = re.search('Name=([^;\n]+)', line)
    else:
        pass
    assert accmatch, 'unable to parse gene accession: %s' % line
    accession = accmatch.group(1)

    if 'gene_biotype=V_segment' in line or \
       'gene_biotype=C_region' in line:
        geneid = re.search('ID=([^;\n]+)', line).group(1)
        vdj_segments[geneid] = accession

    return line + ';accession=' + accession


def parse_transcript_accession(line, source, rnaid_to_accession):
    """Parse accession for transcript features."""
    fields = line.split('\t')
    if len(fields) != 9:
        return line

    ftype = fields[2]
    if ftype not in ['mRNA', 'tRNA', 'rRNA', 'ncRNA', 'transcript',
                     'primary_transcript']:
        return line

    accmatch = None
    idmatch = None
    if source in ['refseq', 'ncbi_flybase']:
        accmatch = re.search('transcript_id=([^;\n]+)', line)
        idmatch = re.search('GeneID:([^;,\n]+)', line)
    elif source in ['crg', 'pdom']:
        accmatch = re.search('ID=([^;\n]+)', line)
    elif source == 'beebase':
        accmatch = re.search('Name=([^;\n]+)', line)
    else:
        pass
    assert accmatch or idmatch, \
        'unable to parse transcript accession: %s' % line

    if accmatch:
        accession = accmatch.group(1)
    else:
        accession = '%s:%s' % (idmatch.group(1), ftype)
    line += ';accession=' + accession

    rnaidmatch = re.search('ID=([^;\n]+)', line)
    if rnaidmatch:
        rnaid = rnaidmatch.group(1)
        rnaid_to_accession[rnaid] = accession
    else:
        print('Warning: RNA has no ID: %s' % line, file=sys.stderr)
    return line


def parse_vdj_features(line, rnaid_to_accession):
    """Parse accessions for features of V(D)J genes."""
    fields = line.split('\t')
    if len(fields) != 9:
        return line

    ftype = fields[2]
    if ftype not in ['V_gene_segment', 'C_gene_segment']:
        return line

    vdjid = re.search('ID=([^;\n]+)', line).group(1)
    geneid = re.search('Parent=([^;\n]+)', line).group(1)
    accession = re.search('GeneID:([^;,\n]+)', line).group(1)
    rnaid_to_accession[vdjid] = accession
    rnaid_to_accession[geneid] = accession

    return line + ';accession=' + accession


def parse_transcript_feature_accession(line, source, rnaid_to_accession,
                                       vdj_segments):
    """
    Parse accession for exons, introns, and coding sequences

    For genes involved in V(D)J recombination, exons are children of the
    V_segment or C_segment, while CDS features are direct children of the gene.
    """
    fields = line.split('\t')
    if len(fields) != 9:
        return line

    ftype = fields[2]
    if ftype not in ['exon', 'intron', 'CDS']:
        return line

    parentid = re.search('Parent=([^;\n]+)', line).group(1)
    assert ',' not in parentid, parentid
    assert parentid in rnaid_to_accession or parentid in vdj_segments, parentid
    if parentid in rnaid_to_accession:
        accession = rnaid_to_accession[parentid]
    elif parentid in vdj_segments:
        accession = vdj_segments[parentid]
    return line + ';accession=' + accession


def format_prefix(line, prefix):
    """Apply a prefix to each sequence ID."""
    if len(line.split('\t')) == 9:
        return prefix + line
    elif line.startswith('##sequence-region'):
        return re.sub('##sequence-region(\s+)(\S+)',
                      '##sequence-region\g<1>%s\g<2>' % args.prefix, line)


def format_gff3(instream, source, prefix=None):
    vdj_segments = dict()
    id2acc = dict()
    for line in args.gff3:
        line = line.rstrip()
        if match_filter(line, source):
            continue
        if pseudogenic_cds(line):
            continue

        line = parse_gene_accession(line, source, vdj_segments)
        line = parse_transcript_accession(line, source, id2acc)
        line = parse_vdj_features(line, id2acc)
        line = parse_transcript_feature_accession(line, source, id2acc,
                                                  vdj_segments)
        if args.prefix:
            line = process_prefix(line, args.prefix)

        yield line


if __name__ == '__main__':
    args = parse_args()
    for line in format_gff3(args.gff3, args.source):
        print(line, file=args.outfile)
