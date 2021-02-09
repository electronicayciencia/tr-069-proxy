#!/usr/bin/env python

# Decrypt and decompress Sagemcon Configuration file and dump some useful data.

import sys
import gzip
from xml.etree import ElementTree as ET
from gsdf import decrypt
import json
import argparse


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

    parser = argparse.ArgumentParser(
        description='Decrypts Sagemcom F@ST 5657 configuration file.')

    parser.add_argument('infile', help='Encrypted configuration file')
    parser.add_argument('outfile', nargs='?', help='Output XML file')
    args = parser.parse_args()

    with open(configfile) as configfile_h:
        config = json.load(configfile_h)

    if config is None:
        print("Cannot load config from %s" % configfile)
        return

    ciphertext = open(args.infile, "rb").read()
    xml_gz = decrypt(ciphertext)
    xml = gzip.decompress(xml_gz)

    show_interesting_fields(xml, config['paths'])

    if args.outfile is not None:
        open(args.outfile, "wb").write(xml)
        print("Whole XML saved in %s." % args.outfile)


if __name__ == "__main__":
    main()
