#!/usr/bin/env python3

import re
import sys
from pathlib import Path

pattern = re.compile(r'^(\s*-\s*)&\S+\s*$')

def remove_yaml_anchors(input_file, output_file):
    input_path = Path(input_file)

    with input_path.open("r", encoding="utf-8") as f:
        text = f.read()

    new_text = re.sub(r"&id\d+\n      ", "", text)

    output_path = Path(output_file)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(new_text)

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(f"Usage: {sys.argv[0]} input.yaml")
        sys.exit(1)

    remove_yaml_anchors(
        sys.argv[1],
        sys.argv[1]+"_",
    )