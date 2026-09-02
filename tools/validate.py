#!/usr/bin/env python3
"""Static checks for the mod. Catches the failures that are silent in-game."""
import re, sys, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOD  = ROOT / "ark_of_destruction"
errs, warns = [], []

def strip(line):
    """Remove comments and quoted strings so braces inside them don't count."""
    line = re.sub(r'"[^"]*"', '""', line)
    return line.split('#', 1)[0]

txt_files = sorted(MOD.rglob("*.txt"))
for f in txt_files:
    depth, raw = 0, f.read_text(encoding="utf-8", errors="replace")
    for n, line in enumerate(raw.splitlines(), 1):
        s = strip(line)
        if s.count('"') % 2:
            errs.append(f"{f.relative_to(ROOT)}:{n}  odd number of quotes")
        depth += s.count('{') - s.count('}')
        if depth < 0:
            errs.append(f"{f.relative_to(ROOT)}:{n}  closing brace with nothing open")
            depth = 0
    if depth:
        errs.append(f"{f.relative_to(ROOT)}  ends with {depth} unclosed brace(s)")

# localisation: BOM is mandatory, and the :0 form is easy to get wrong
for f in sorted(MOD.rglob("*.yml")):
    b = f.read_bytes()
    if not b.startswith(b"\xef\xbb\xbf"):
        errs.append(f"{f.relative_to(ROOT)}  missing UTF-8 BOM (silent failure)")
    body = b.decode("utf-8-sig", errors="replace").splitlines()
    if not body or not body[0].strip().endswith(":"):
        errs.append(f"{f.relative_to(ROOT)}  first line must be a language tag")
    for n, line in enumerate(body[1:], 2):
        t = line.strip()
        if not t or t.startswith("#"):
            continue
        if not re.match(r'^[A-Za-z0-9_.\-]+:\d*\s+".*"$', t):
            errs.append(f"{f.relative_to(ROOT)}:{n}  not KEY:0 \"value\"  ->  {t[:48]}")

blob = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in txt_files)

# every scripted effect/trigger that is CALLED should be DEFINED
defined = set()
for f in txt_files:
    if "scripted_effects" in str(f) or "scripted_triggers" in str(f):
        defined |= set(re.findall(r'^([a-z_][a-z0-9_]*)\s*=\s*\{', f.read_text(encoding="utf-8"), re.M))
called = set(re.findall(r'\b([a-z_][a-z0-9_]*)\s*=\s*yes\b', blob))
known_vanilla = {
    'hide_window','is_triggered_only','always','exists','is_machine_empire','is_robotic',
    'has_ship_flag','has_fleet_flag','has_country_flag','has_component','enabled',
    'is_space_station','is_civilian','is_designable','components_add_to_cost','custom_name',
    'has_advisor','initialized',
}
missing = sorted(c for c in called - defined - known_vanilla if c.startswith("ark_"))
for m in missing:
    errs.append(f"called but never defined: {m} = yes")

# on_actions must point at events that exist
declared = set(re.findall(r'\bid\s*=\s*(\w+\.\d+)', blob))
referenced = set(re.findall(r'events\s*=\s*\{([^}]*)\}', blob))
refs = {e for grp in referenced for e in grp.split()}
for r in sorted(refs - declared):
    errs.append(f"on_action references a missing event: {r}")

print(f"scanned {len(txt_files)} script files, {len(list(MOD.rglob('*.yml')))} localisation files")
print(f"defined scripted objects: {len(defined)}   events declared: {len(declared)}")
for e in errs:  print("  FAIL ", e)
for w in warns: print("  warn ", w)
print(("\nFAILED: %d" % len(errs)) if errs else "\nAll checks passed.")
sys.exit(1 if errs else 0)
