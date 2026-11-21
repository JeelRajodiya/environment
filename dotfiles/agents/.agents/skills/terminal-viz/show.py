#!/usr/bin/env python3
"""Show PNGs fitted to this terminal pane (Herdr, Ghostty, kitty). Needs `kitten` (brew install kitty).
Usage: show.py a.png [b.png ...]    Enter = next image, q = quit.
Herdr hides the pane's pixel size, so pass a guessed one and use Unicode placeholders,
which Herdr scales into the cells itself."""
import shutil, subprocess, sys

CELL = (10, 22)  # ponytail: guessed cell size in px (only the ratio matters); tune if images look squashed


def show(path):
    cols, rows = shutil.get_terminal_size()
    rows -= 2  # room for the prompt
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()
    subprocess.run(["kitten", "icat", "--unicode-placeholder", "--fit=both", "--transfer-mode=stream",
                    "--use-window-size", f"{cols},{rows},{cols * CELL[0]},{rows * CELL[1]}", path])


if __name__ == "__main__":
    paths = sys.argv[1:]
    try:
        for n, p in enumerate(paths, 1):
            show(p)
            more = "Enter = next · " if n < len(paths) else ""
            if input(f"\033[2m {n}/{len(paths)} · {more}q = quit \033[0m").strip().lower() == "q":
                break
    except (KeyboardInterrupt, EOFError):
        pass
