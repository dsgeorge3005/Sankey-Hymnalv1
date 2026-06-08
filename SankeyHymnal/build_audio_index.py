import os
import json
import re

ROOT = "SANKEY Learning files"

audio_index = {}

for folder in os.listdir(ROOT):

    folder_path = os.path.join(ROOT, folder)

    if not os.path.isdir(folder_path):
        continue

    match = re.match(r"(\d+)-", folder)

    if not match:
        continue

    hymn_number = match.group(1)

    audio_index[hymn_number] = {}

    for file in os.listdir(folder_path):

        if not file.endswith(".mp3"):
            continue

        if "-SATB-" in file:
            part = "SATB"
        elif "-S-" in file:
            part = "S"
        elif "-A-" in file:
            part = "A"
        elif "-T-" in file:
            part = "T"
        elif "-B-" in file:
            part = "B"
        else:
            continue

        audio_index[hymn_number][part] = f"{folder}/{file}"

with open("audio_index.json", "w", encoding="utf-8") as f:
    json.dump(audio_index, f, indent=2)

print("Indexed", len(audio_index), "hymns")