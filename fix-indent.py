#!/usr/bin/env python3
"""Convert leading-space indentation to tabs.

Only the indentation at the start of each line is touched; spaces used for
column alignment further along a line (e.g. inside the matrix `map` or keymap
`bindings` blocks) are left untouched.

Every TABWIDTH leading spaces become one tab. Any leftover spaces that don't
make a full tab stop are preserved as spaces (handles odd/misaligned indents
without silently shifting code). Existing leading tabs are kept.

Usage:
    python3 fix-indent.py [-w WIDTH] FILE [FILE ...]
    python3 fix-indent.py --check FILE      # show what would change, write nothing
"""
import argparse
import sys

def convert_line(line: str, width: int) -> str:
    i = 0
    cols = 0          # visual column of the indentation seen so far
    tabs = 0          # tabs already present in the leading run
    # Walk the leading whitespace run, tracking visual columns.
    while i < len(line) and line[i] in " \t":
        if line[i] == "\t":
            tabs += 1
            cols += width - (cols % width)
        else:
            cols += 1
        i += 1
    rest = line[i:]
    # cols = total visual indentation. Rebuild as tabs + remainder spaces.
    full_tabs = cols // width
    rem = cols % width
    return "\t" * full_tabs + " " * rem + rest

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--width", type=int, default=4,
                    help="spaces per indent level (default: 4)")
    ap.add_argument("--check", action="store_true",
                    help="report files that would change; write nothing")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    changed_any = False
    for path in args.files:
        with open(path, "r", newline="") as f:
            original = f.read()
        # Preserve line endings by splitting on \n and rejoining.
        new = "\n".join(convert_line(l, args.width)
                        for l in original.split("\n"))
        if new != original:
            changed_any = True
            if args.check:
                print(f"would change: {path}")
            else:
                with open(path, "w", newline="") as f:
                    f.write(new)
                print(f"fixed: {path}")
        else:
            print(f"unchanged: {path}")
    return 1 if (args.check and changed_any) else 0

if __name__ == "__main__":
    sys.exit(main())
