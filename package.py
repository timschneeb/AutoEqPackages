# -*- coding: utf-8 -*_

import json
import os
import re
import shutil
import subprocess
import tarfile
import time
import urllib.parse
from datetime import datetime


def main():
    if not os.path.isfile("results/INDEX.md"):
        print("Wrong working directory")
        exit(1)

    # Parse INDEX.md
    indices = []
    with open("results/INDEX.md") as file:
        for line in file:
            result = re.search(r'\[([^\[\]]+)]\(([^()]+)\)\s+by\s+(.+)', line, re.IGNORECASE)
            if result:
                # Name, relative path, source
                indices.append([result.group(1), urllib.parse.unquote(result.group(2)), result.group(3)])

    # Copy important files
    for index in indices:
        src = os.path.normpath(os.path.join("results", index[1]))
        dest = os.path.normpath(os.path.join("export", index[0], index[2]))
        src_csv = os.path.join(src, index[0] + ".csv")
        src_graphic = os.path.join(src, index[0] + " GraphicEQ.txt")

        os.makedirs(dest, exist_ok=True)

        if os.path.isfile(src_graphic):
            shutil.copy(src_graphic,
                        os.path.join(dest, "graphic.txt"))
        else:
            print("[GraphicEQ] File missing: " + src_graphic)

        if os.path.isfile(src_csv):
            shutil.copy(src_csv,
                        os.path.join(dest, "raw.csv"))
        else:
            print("[CSV] File missing: " + src_csv)

    # Group source by headphone name
    group = {}
    for name, uri, source in indices:
        group[name] = [source] if name not in group.keys() else group[name] + [source]

    # Recommended order (high to low)
    rank_order = ["oratory1990", "Crinacle", "Innerfidelity", "Rtings", "Headphone.com", "Reference Audio Analyzer"]

    # Collect additional data and rank
    table = []
    for name in group.keys():
        ranks = [x for x in rank_order for y in group[name] if y.startswith(x)]

        for source in group[name]:
            rank = -1
            for index, item in enumerate(ranks):
                if source.startswith(item):
                    rank = index + 1
                    break

            entry = {
                "n": name,
                "s": source,
                "r": rank
            }
            table.append(entry)

    # Create index.json
    with open('export/index.json', 'w') as outfile:
        json.dump(table, outfile)

    # Create version.json
    entry = {
        "commit": subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip(),
        "commit_time": datetime.utcfromtimestamp(int(subprocess.check_output(['git', 'log', '-1', '--format=%at'], text=True).strip())).strftime('%Y/%m/%d %H:%M:%S'),
        "package_time": time.strftime('%Y/%m/%d %H:%M:%S')
    }
    with open('export/version.json', 'w') as outfile:
        json.dump(entry, outfile)

    # Compress using GZIP
    with tarfile.open("archive.tar.gz", "w:gz") as tar:
        for fn in os.listdir("export"):
            p = os.path.join("export", fn)
            tar.add(p, arcname=fn)


if __name__ == '__main__':
    main()
