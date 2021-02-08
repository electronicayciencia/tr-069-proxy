#!/usr/bin/env python

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util import Counter
from binascii import hexlify, unhexlify
import sys


def hex_to_int(i):
    return int(hexlify(i), 16)


def int_to_hex(i, l):
    h = hex(i).strip("L")[2:]
    if len(h) % 2 != 0:
        h = "0" + h
    s = unhexlify(h)
    return "\x00" * (l - len(s)) + s


key = "\x7d\xa2\x58\x13\xdd\x9d\x7a\x15\x3e\x60\xa0\x28\xba\xdd\xb2\x88"
key += "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

# Decryption routine - does no verification of input data.
# Be careful!


def decrypt(ciphertext):
    iv = hex_to_int(ciphertext[16:32])
    ctr = Counter.new(128, initial_value=iv)

    crypto = AES.new(key, AES.MODE_CTR, counter=ctr)

    tag_len = hex_to_int(ciphertext[12:16])
    data = ciphertext[48+tag_len:]
    cleartext = crypto.decrypt(data)

    return cleartext

# Encryption routine - creates libgsdf.so.1.0.0 compatible ciphertext


def encrypt(data, tag):

    iv = hex_to_int(b"\x00"*16)
    ctr = Counter.new(128, initial_value=iv)

    crypto = AES.new(key, AES.MODE_CTR, counter=ctr)

    data_ciphertext = crypto.encrypt(data)
    tag_length = len(tag)
    total_length = 0x30+tag_length+len(data_ciphertext)

    ciphertext = b"AEAD 10\x00"
    ciphertext += int_to_hex(total_length, 4)
    ciphertext += int_to_hex(tag_length, 4)
    ciphertext += int_to_hex(iv, 16)
    ciphertext += key[0:16]  # Note: key placed in MAC location, for AEAD
    ciphertext += tag
    ciphertext += data_ciphertext

    h = SHA256.new()
    h.update(ciphertext)
    mac = h.digest()

    ciphertext = b"AEAD 10\x00"
    ciphertext += int_to_hex(total_length, 4)
    ciphertext += int_to_hex(tag_length, 4)
    ciphertext += int_to_hex(iv, 16)
    ciphertext += mac[0:16]
    ciphertext += tag
    ciphertext += data_ciphertext

    return ciphertext

# Main function reads from stdin, performs operation and prints to stdout


def main():
    msg = "Usage: %s e|d < file.in > file.out\n\te) Encryption\n\td) Decryption" % sys.argv[0]
    if len(sys.argv) == 1:
        print msg
        return

    tag = "default"

    mode = sys.argv[1]
    if mode == 'e' or mode == 'encrypt':
        sys.stdout.write(encrypt(sys.stdin.read(), tag))
    elif mode == 'd' or mode == 'decrypt':
        sys.stdout.write(decrypt(sys.stdin.read()))
    else:
        print msg


if __name__ == "__main__":
    main()
