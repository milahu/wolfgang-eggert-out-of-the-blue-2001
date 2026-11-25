#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Out of the blue",
    "--doc-subtitle", "Spuren des Terrors in Amerika. Fundamentalisten - Messianisten - Geheimdienste: Hintergründe, Profiteure und mögliche Drahtzieher des Anschlags vom 11. September 2001",
    # "--doc-subject", "",
    "--doc-date", "2001-10-01",
    "--doc-edition", "1",
    "--doc-extent", "128 pages",
    "--color-image-pages", "129,130",
    "--doc-author", "Wolfgang Eggert",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    "--doc-publisher", "CHRONOS-MEDIEN-Vertrieb",
    "--doc-language", "de", # german
    # "--doc-language", "en", # english
    "--doc-isbn", "9783935845045",
    # "--doc-isbn-10", "3935845049", # TODO
    "--doc-cover-image", "075-level/129.tiff",
    "--canonical-url-base", "https://milahu.github.io/wolfgang-eggert-out-of-the-blue-2001/",
    "--doc-description", """
Professor August Pradetto von der Bundeswehr-Hochschule Hamburg
erklärte am 19. September in einem Interview mit der Tageszeitung *Die Welt*
Bin Laden sei bestenfalls ein Bestandteil des Terror-Kommandos,
aber kein wesentlicher:
"Bin Laden ist ein Topterrorist, der eine Reihe von Verbrechen begangen hat.
Das steht außer Zweifel.
Allerdings wird Bin Laden seit Jahren von westlichen Geheimdiensten gejagt...
Um aber die jüngste Anschlagsserie vorzubereiten und die Logistik aufzubauen,
benötigt man eine jahrelange Vorbereitung.
Das geht nicht von Afghanistan aus."
Auf die Frage, wen er fir die Drahtzieher halte, antwortete er:
"Seit dem Ende der Sowjetunion beobachten wir eine Anarchisierung der Weltpolitik.
Früher wurden antiamerikanische, antiwestliche und antikapitalistische Einstellungen
durch die Sowjetideologie gebunden - jetzt nicht mehr.
Ich halte es für gut möglich,
daß sich ehemalige Geheimdienstler aus diesem Umfeld mit anderen Kräften verbunden haben."

*Die Welt*: Welche Ziele sollten diese Terroristen verfolgen?
*Pradetto*: "Dahinter steckt keine blinde Zerstörungswut, sondern Kalkül.
Die Angriffe auf die wichtigsten Symbole der einzigen Supermacht sind eine gezielte Provokation.
Geheimdienste wissen die Reaktion des Gegners vorherzusehen.
Das Ziel könnte sein, die NATO in einen Krieg gegen die islamische Welt zu ziehen.
Und wir sind dabei, in eine ungeheure Falle zu tappen."
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
