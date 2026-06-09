import argparse
import subprocess

from pathlib import Path

parser = argparse.ArgumentParser(description="Script to upload a book to your Pico-Ebook")

parser.add_argument("file", type=Path, help="File you want to upload")

args = parser.parse_args()

subprocess.run(
    ["mpremote", "cp", str(args.file), ":/books/"+str(args.file.name)],
    check=True
    )