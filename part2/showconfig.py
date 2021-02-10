#!/usr/bin/env python

# Decrypt and decompress Sagemcon Configuration file and dump some useful data.

import sys
import gzip
from xml.etree import ElementTree as ET
from gsdf import decrypt
import json
import argparse


def loadconfig(file):
    ''' Read configuration file. Must be json. 
    Return dict or terminate program. '''
    try:
        with open(file) as configfile_h:
            config = json.load(configfile_h)
    except:
        print("Cannot read configuration file %s or it is damaged." % file)
        sys.exit(1)

    return config


def parse_cmdline():
    ''' No parameters. Return Parser object. Exit and display help on error.'''
    parser = argparse.ArgumentParser(
        description='Decrypts Sagemcom F@ST 5657 configuration file '
        ' and display relevant fields.')

    parser.add_argument('infile', help='Encrypted configuration file')
    parser.add_argument('outfile', nargs='?',
                        help='Output XML file (optional)')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    return args


def show_interesting_fields(xml, paths):
    tree = ET.ElementTree(ET.fromstring(xml))
    root = tree.getroot()

    for p in paths:
        node = root.find(p['xpath'])
        if node is None:
            value = "Not found"
        else:
            value = node.text

        print("%s: %s" % (p['friendlyname'], value))


def main():
    configfile = "showconfig.json"
    args = parse_cmdline()
    config = loadconfig(configfile)

    try:
        ciphertext = open(args.infile, "rb").read()
    except:
        print("Cannot read %s." % args.infile)
        sys.exit(1)

    try:
        xml_gz = decrypt(ciphertext)
        xml = gzip.decompress(xml_gz)
    except:
        print("Decryption failed. Invalid router backup file.")
        sys.exit(1)

    show_interesting_fields(xml, config['paths'])

    if args.outfile is not None:
        open(args.outfile, "wb").write(xml)
        print("Whole XML saved in %s." % args.outfile)


if __name__ == "__main__":
    main()
