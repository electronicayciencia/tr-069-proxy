#!/usr/bin/env python

# Decrypt and decompress Sagemcon Configuration file and dump some useful data.

import sys
import gzip
from xml.etree import ElementTree as ET
from gsdf import encrypt
import json
import argparse


def parse_cmdline():
    ''' No parameters. Return Parser object. Exit and display help on error.'''
    parser = argparse.ArgumentParser(
        description='Re-encrypts Sagemcom F@ST 5657 configuration file ')

    parser.add_argument('infile', help='Clear XML configuration file')
    parser.add_argument('outfile', help='Output cfg encrypted file')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    return args


args = parse_cmdline()

try:
    xml = open(args.infile, "rb").read()
except:
    print("Cannot read %s." % args.infile)
    sys.exit(1)

try:
    xml_gz = gzip.compress(xml)
    ciphertext = encrypt(xml_gz, b"default")
except:
    print("Encryption failed.")
    sys.exit(1)

open(args.outfile, "wb").write(ciphertext)
print("CFG filed saved in %s." % args.outfile)
