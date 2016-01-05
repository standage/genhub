#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""Simple module for downloading data with PycURL"""

import gzip
import pycurl


def url_download(urldata, localpath, compress=False, follow=True):
    """
    Helper function for downloading remote data files with PycURL.

    - urldata: string(s), URL or list of URLs
    - localpath: path of the filename to which output will be written
    - compress: output compression
    """
    urls = urldata
    if isinstance(urldata, str):
        urls = [urldata]

    openfunc = open
    if compress is True:
        openfunc = gzip.open

    with openfunc(localpath, 'wb') as out:
        for url in urls:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, out)
            if follow:
                c.setopt(c.FOLLOWLOCATION, True)
            c.perform()
            c.close()
