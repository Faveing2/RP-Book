from PIL import Image
import numpy as np
import deflate

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

def encode_cover(x, y, coverPath, nodither):

    WIDTH = x
    HEIGHT = y

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
        for y in range(width):
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


    return buffer

def normalize_text(text):
    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "—": "-",
        "–": "-",
        "…": "...",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text

def encode_book(bookPath):

    with open(bookPath, "r", errors="ignore") as f:
        rawdata = f.read()
        f.close()

    #newdata = normalize_text(rawdata)
    newdata = rawdata
    return newdata
    