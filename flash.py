import subprocess
from pathlib import Path

projectFiles = [
    "main.py",
    "settings.json",
    "settings.py",
    "epd.py"
]

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
    try:
        subprocess.run(
            ["mpremote", "cp", file, ":/"+file],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(e.output)

### Write books

subprocess.run(
    ["mpremote", "mkdir", "books"],
    check=True
)

dir_path = Path("books/")
files = [f.name for f in dir_path.iterdir() if f.is_file()]

for file in files:
    if ".txt" not in file:
        continue

    try:
        subprocess.run(
            ["mpremote", "cp", "books/"+file, ":/books/"+file],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(e.output)