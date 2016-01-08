#!/usr/bin/env bash
set -e

# Set up installation directory
mkdir -p $HOME/local/src $HOME/local/bin $HOME/local/lib $HOME/local/include

if [ ! -f "$HOME/local/tgz/master.tar.gz" ]; then
    mkdir -p $HOME/local/tgz
    wget -P $HOME/local/tgz http://genometools.org/pub/binary_distributions/gt-1.5.8-Linux_x86_64-64bit-complete.tar.gz
    wget -P $HOME/local/tgz https://github.com/standage/AEGeAn/archive/master.tar.gz
fi

# Install GenomeTools
gtdir="$HOME/local/src/gt-1.5.8-Linux_x86_64-64bit-complete"
tar -xzf $HOME/local/tgz/gt-1.5.8-Linux_x86_64-64bit-complete.tar.gz --directory $HOME/local/src
cp -r $gtdir/bin/* $HOME/local/bin/
cp -r $gtdir/include/genometools $HOME/local/include/
cp -r $gtdir/lib/* $HOME/local/lib/

# Install AEGeAn
tar -xzf $HOME/local/tgz/master.tar.gz --directory $HOME/local/src
cd $HOME/local/src/AEGeAn-master && make prefix=$HOME/local install install-scripts && cd -