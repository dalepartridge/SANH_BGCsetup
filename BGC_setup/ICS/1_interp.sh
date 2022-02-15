#!/usr/bin/env bash

cd pelagic
ln -s $RAWDATA/global/*.nc .
ln -s $DOMAINFILE .
python interp.py
cd ..

