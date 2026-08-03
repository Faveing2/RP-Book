import subprocess
from pathlib import Path

import cv2
from PIL import Image
import numpy as np
import deflate

from tools import *

import struct

WIDTH = 122
HEIGHT = 250

import argparse

parser = argparse.ArgumentParser(description="Flasher program for PicoBook")

parser.add_argument("bookPath", type=str, help="The path to the desired book to flash")
parser.add_argument("coverPath", type=str,help="The path to the cover for the desired book to flash")

parser.add_argument("--nodither", "-nd", action="store_true", help="Disable dithering of the cover")
parser.add_argument("--nowrite", "-nw", action="store_true", help="Do not wipe or write to the pico")

#parser.add_argument("only", type=str, help=)

projectFiles = [
    "pico/main.py",
    "pico/settings.json",
    "pico/settings.py",
    "pico/epd.py",
    "pico/lowpower.py",
    "pico/cover.bin",
    "pico/book.txt"
]

args = parser.parse_args()

bookPath = args.bookPath
coverPath = args.coverPath
nodither = args.nodither
nowrite = args.nowrite

### Encode the cover image
print("Encoding cover")
buffer = encode_cover(WIDTH, HEIGHT, coverPath, nodither)

with open("pico/cover.bin", "wb") as f:
    f.write(deflate.zlib_compress(buffer))

### Rencode the book
book = encode_book(bookPath)
print(book)

with open("pico/book.txt", "w") as f:
    f.write(book)
    f.close()

#### Wipe the Internal Storage of the Pico
if not nowrite:
    print("Erasing Virtual Filesystem")
    try:
        subprocess.run(
            ["mpremote", "rm", "-rf", ":/"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            print("Erased Virtual Filesystem")
        else:
            print(e.output)

    #### Write Project files
    for file in projectFiles:

        suffix = file.split("/")[-1]
        try:
            subprocess.run(
                ["mpremote", "cp", file, ":/"+suffix],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(e.output)

    # ### Write books

    # print("Copying book to the Pico")
    # subprocess.run(
    #     ["mpremote", "mkdir", "books"],
    #     check=True
    # )
    # try:
    #     subprocess.run(
    #         ["mpremote", "cp", bookPath, ":/books/"+bookPath], check=True
    #     )
    # except subprocess.CalledProcessError as e:
    #     print(e.output)

else:
    print("Skipping erasing virtual filesystem and copying files")
