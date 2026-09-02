#!/usr/bin/env python3
"""
Register this repo as a LOCAL Stellaris mod.

    python3 tools/install_local_mod.py            # show what it would do
    python3 tools/install_local_mod.py --write    # actually write the .mod file

Why this is needed: the files you see in Documents/Paradox Interactive/Stellaris/mod/
named ugc_<id>.mod are Workshop POINTERS. The mod content itself lives under
steamapps/workshop/content/281990/<id>/. A local mod needs its own hand-written
pointer, and that is what this writes.

It points at the repo in place, so edits here are live in-game with no copying.
"""
import argparse, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MOD_DIR_NAME = "ark_of_destruction"
MOD_SRC = REPO / MOD_DIR_NAME

def stellaris_user_dir():
    home = Path.home()
    for c in (
        home / "Documents" / "Paradox Interactive" / "Stellaris",
        home / "OneDrive" / "Documents" / "Paradox Interactive" / "Stellaris",
        home / ".local" / "share" / "Paradox Interactive" / "Stellaris",
    ):
        if c.is_dir():
            return c
    return None

def check_mod_source():
    problems = []
    if not MOD_SRC.is_dir():
        problems.append(f"mod folder missing: {MOD_SRC}")
        return problems
    if not (MOD_SRC / "descriptor.mod").is_file():
        problems.append("descriptor.mod missing from inside the mod folder")
    if not any(MOD_SRC.rglob("*.txt")):
        problems.append("no script files found")
    for y in MOD_SRC.rglob("*.yml"):
        if not y.read_bytes().startswith(b"\xef\xbb\xbf"):
            problems.append(f"{y.name} has no UTF-8 BOM (localisation will fail silently)")
    return problems

def pointer_text(path_value):
    return (
        'name="Ark of Destruction"\n'
        'version="0.1.0"\n'
        f'path="{path_value}"\n'
        'supported_version="4.4.*"\n'
        'tags={\n\t"Gameplay"\n\t"Events"\n\t"Military"\n}\n'
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--stellaris-dir", help="override auto-detection")
    a = ap.parse_args()

    print(f"repo:        {REPO}")
    print(f"mod source:  {MOD_SRC}")

    problems = check_mod_source()
    for p in problems:
        print(f"  PROBLEM  {p}")
    if problems:
        sys.exit("\nfix the above first")
    print("  mod source looks well-formed")

    sd = Path(a.stellaris_dir) if a.stellaris_dir else stellaris_user_dir()
    if sd is None:
        print("\nCould not find the Stellaris user directory.")
        print("Re-run with --stellaris-dir \"<path to Paradox Interactive/Stellaris>\"")
        print("\nThe file to create by hand, if you prefer:")
        print(f"  <that dir>/mod/{MOD_DIR_NAME}.mod\n")
        print(pointer_text(MOD_SRC.as_posix()))
        sys.exit(1)

    modroot = sd / "mod"
    target = modroot / f"{MOD_DIR_NAME}.mod"
    # Clausewitz wants forward slashes even on Windows.
    text = pointer_text(MOD_SRC.as_posix())

    print(f"stellaris:   {sd}")
    print(f"mod folder:  {modroot}  ({'exists' if modroot.is_dir() else 'MISSING'})")
    ugc = len(list(modroot.glob('ugc_*.mod'))) if modroot.is_dir() else 0
    print(f"             {ugc} Workshop pointer(s) already there - those are not mod data")
    print(f"\nwould write: {target}\n")
    print(text)

    if not a.write:
        print("dry run. re-run with --write to create it.")
        return

    modroot.mkdir(parents=True, exist_ok=True)
    if target.exists():
        print(f"note: overwriting existing {target.name}")
    target.write_text(text, encoding="utf-8")
    print(f"written: {target}")
    print("\nNow, in the Paradox launcher:")
    print("  1. Close the launcher completely first, then reopen it.")
    print("  2. Playsets -> your playset -> Add mods. It should appear as 'Ark of Destruction'.")
    print("  3. If it does not appear, the launcher cached its mod list; see docs/TESTING.md.")

if __name__ == "__main__":
    main()
