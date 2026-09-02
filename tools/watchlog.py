#!/usr/bin/env python3
"""
Watch Stellaris logs for this mod's output. Stdlib only, no install, no network.

    python3 tools/watchlog.py                  # auto-locate the log folder
    python3 tools/watchlog.py --dir "C:/path/to/Stellaris/logs"
    python3 tools/watchlog.py --all            # don't filter to ark_ lines

Why this exists: game.log carries thousands of lines from the base game and
every other mod. Finding ours by eye does not scale. This is the whole of it -
about a hundred lines, no dependencies, nothing that touches the network.
"""
import argparse, os, re, sys, time
from pathlib import Path

RED, GREEN, YELLOW, DIM, RESET = "\033[31m", "\033[32m", "\033[33m", "\033[2m", "\033[0m"
if os.name == "nt":                       # enable ANSI on Windows terminals
    os.system("")

DEFAULT_PATTERN = r"\[ARK|ark_|arktest"

def candidate_dirs():
    home = Path.home()
    yield home / "Documents" / "Paradox Interactive" / "Stellaris" / "logs"
    yield home / "OneDrive" / "Documents" / "Paradox Interactive" / "Stellaris" / "logs"
    yield home / ".local" / "share" / "Paradox Interactive" / "Stellaris" / "logs"
    yield (home / "Documents" / "Paradox Interactive" / "Stellaris" / "logs")

def find_logs(explicit):
    if explicit:
        d = Path(explicit)
        if not d.is_dir():
            sys.exit(f"not a directory: {d}")
        return d
    for d in candidate_dirs():
        if d.is_dir():
            return d
    sys.exit("could not find the Stellaris logs folder - pass --dir")

def colour(line):
    low = line.lower()
    if "fail" in low or "error" in low:            return RED + line + RESET
    if "pass" in low:                              return GREEN + line + RESET
    if "warn" in low or "deprecat" in low:         return YELLOW + line + RESET
    return line

class Tail:
    """Follows one file, surviving the truncation Stellaris does on launch."""
    def __init__(self, path, label):
        self.path, self.label, self.pos, self.inode = path, label, 0, None
        if path.exists():
            self.pos = path.stat().st_size          # start at the end
            self.inode = path.stat().st_ino

    def read(self):
        if not self.path.exists():
            return []
        st = self.path.stat()
        if self.inode is not None and (st.st_ino != self.inode or st.st_size < self.pos):
            self.pos, self.inode = 0, st.st_ino     # rotated or truncated
            print(f"{DIM}-- {self.label} restarted --{RESET}")
        self.inode = st.st_ino
        if st.st_size == self.pos:
            return []
        with self.path.open("r", encoding="utf-8", errors="replace") as f:
            f.seek(self.pos)
            data = f.read()
            self.pos = f.tell()
        return data.splitlines()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir")
    ap.add_argument("--all", action="store_true", help="show every line, not just ours")
    ap.add_argument("--pattern", default=DEFAULT_PATTERN)
    a = ap.parse_args()

    logs = find_logs(a.dir)
    rx = None if a.all else re.compile(a.pattern, re.I)
    tails = [Tail(logs / "game.log", "game.log"), Tail(logs / "error.log", "error.log")]

    print(f"{DIM}watching {logs}{RESET}")
    print(f"{DIM}filter: {'everything' if a.all else a.pattern}{RESET}")
    print(f"{DIM}reminder: launch Stellaris with -logall or repeat lines are swallowed{RESET}\n")

    counts = {"PASS": 0, "FAIL": 0}
    try:
        while True:
            for t in tails:
                for line in t.read():
                    if rx and not rx.search(line):
                        continue
                    tag = "err" if t.label == "error.log" else "log"
                    print(f"{DIM}[{tag}]{RESET} {colour(line)}")
                    if "PASS" in line: counts["PASS"] += 1
                    if "FAIL" in line: counts["FAIL"] += 1
            time.sleep(0.4)
    except KeyboardInterrupt:
        print(f"\n{GREEN}PASS {counts['PASS']}{RESET}  {RED}FAIL {counts['FAIL']}{RESET}")
        if counts["PASS"] == 0 and counts["FAIL"] == 0:
            print(f"{YELLOW}nothing matched - check -logall is set and the suite actually ran{RESET}")

if __name__ == "__main__":
    main()
