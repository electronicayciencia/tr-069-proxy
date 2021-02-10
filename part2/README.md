# Sagemcom F@ST 5657 configuration decryptor



## Prerequisites

This scripts runs in Python3 environment.

Yoy will need a Crypto.AES module, provided by pycryptodome, pycrypto, cryptodomex  or whatever Crypto library you like.

    pip install pycryptodome

If you are using Windows, your Crypto library may be not recognized until you remane its directory from `crypto` to `Crypto` (uppercase). Read [this](https://github.com/pycrypto/pycrypto/issues/156).

Or you may prefer to use compiled binary from `dist` directory.

## Showconfig usage

Decrypts Sagemcom F@ST 5657 configuration file and display relevant fields.

    showconfig.py infile [outfile]

- infile: Encrypted configuration file like `device.cfg`
- outfile: Output XML file if you want to save it.

The file `showconfig.json` must be in the same directory.

## gsdf usage

This is a raw encrypt/decrypt routine I copied from NoConroy's posts
[Sagemcom F@ST5355 Reverse Engineering - Part 2](https://web.archive.org/web/20180129221204/https://noconroy.net/sagemcom-fast5355-re-p2.html)
and
[Sagemcom F@ST5355 Reverse Engineering - Part 3](https://web.archive.org/web/20180129221204/https://noconroy.net/sagemcom-fast5355-re-p3.html).

The only changes I made are:

- updated key
- ported to python3

To decrypt:

    python gsdf.py d < device.cfg | gunzip > device.xml

To encrypt:

    gzip -nc device.xml | python gsdf.py e > device.cfg


## Create windows executable

    pyinstaller.exe --onefile .\showconfig.py
