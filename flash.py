import subprocess
from pathlib import Path

import cv2
from PIL import Image
import numpy as np
import deflate


import struct

BAYER_8X8 = np.array([
    [ 0,48,12,60, 3,51,15,63],
    [32,16,44,28,35,19,47,31],
    [ 8,56, 4,52,11,59, 7,55],
    [40,24,36,20,43,27,39,23],
    [ 2,50,14,62, 1,49,13,61],
    [34,18,46,30,33,17,45,29],
    [10,58, 6,54, 9,57, 5,53],
    [42,26,38,22,41,25,37,21]
], dtype=np.uint8)

WIDTH = 122
HEIGHT = 250

import argparse

parser = argparse.ArgumentParser(description="Flasher program for PicoBook")

parser.add_argument("bookPath", type=str, help="The path to the desired book to flash")
parser.add_argument("coverPath", type=str,help="The path to the cover for the desired book to flash")


parser.add_argument("--nodither", "-nd", action="store_true", help="Disable dithering of the cover")


#parser.add_argument("only", type=str, help=)

projectFiles = [
    "pico/main.py",
    "pico/settings.json",
    "pico/settings.py",
    "pico/epd.py",
    "pico/lowpower.py",
    "pico/cover.bin",
]

args = parser.parse_args()

bookPath = args.bookPath
coverPath = args.coverPath
nodither = args.nodither

### Encode the cover image

print("Encoding image")
if WIDTH % 8 == 0:
    width = WIDTH
else :
    width = (WIDTH // 8) * 8 + 8
height = HEIGHT

buffer = bytearray(height*width // 8)

img = Image.open(coverPath)
rgb_img = img.resize((height, width), Image.Resampling.LANCZOS)
if not nodither:
    rgb_img = rgb_img.convert("L")
    gray = np.array(rgb_img, dtype=np.uint8)

    h, w = gray.shape

    thresholds = np.tile(
        BAYER_8X8,
        (h // 4 + 1, w // 4 + 1)
    )[:h, :w]

    thresholds = thresholds * 4

    bw_data = (gray > thresholds).astype(np.uint8) * 255
else:
    rgb_data = np.array(rgb_img)
    bw_data = rgb_data.mean(axis=2)>127

for x in range(HEIGHT):
    for y in range(WIDTH):
        if bw_data[y, x]:
            index = x + (y // 8) * HEIGHT
            #index = y * (width // 8) + (x // 8)
            try:
                buffer[index] |= 1 << (y & 7)
                #buffer[index] |= 0x80 >> (x & 7)
            except IndexError:
                print("Error: IndexError")
                print("Array Index:", index)
                pass

with open("pico/cover.bin", "wb") as f:
    f.write(deflate.zlib_compress(buffer))

#### Wipe the Internal Storage of the Pico
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

### Write books

print("Copying book to the Pico")
subprocess.run(
    ["mpremote", "mkdir", "books"],
    check=True
)
try:
    subprocess.run(
        ["mpremote", "cp", bookPath, ":/books/"+bookPath], check=True
    )
except subprocess.CalledProcessError as e:
    print(e.output)
