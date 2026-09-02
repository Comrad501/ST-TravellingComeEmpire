# Ark of Destruction — working notes for whoever picks this up

A Stellaris 4.4.6 mod: a travelling comet empire that carries captured worlds and can
only be killed through a staged sequence. **Design lives in `docs/architecture-map.html`**
(25 sections, 22 diagrams, every decision and why). This file is operational only — read
the map before changing design, read this before changing code.

---

## Do this first

An in-game probe is pending and it decides the shape of the next fix. Deselect everything,
then in the console:

```
event arktest.5
```

The first live suite run **failed every equality assertion and passed every inequality** —
the signature of a variable that was never created. `arktest.5` sets the same variable on
country, planet and solar_system scope and reports which hold it. Two opposite outcomes:

| Log line | Meaning | Fix |
| --- | --- | --- |
| `SYSTEM FAILED to hold a variable` | Variables don't persist on `solar_system` | **Design hole.** The containment counter needs a different home — country-scoped keyed by system, most likely. Not a test bug. |
| `SYSTEM holds a variable` | Storage is fine | `ark_assert_var_equals` is broken. Fix the helper, design stands. |

Do not patch anything until that line is read. The two causes need opposite work.

---

## State

- **Phase 1** (lore, situations, mechanics) — partly written. Steps 5 and 6 outstanding:
  planet capture via the base-game backing, and the situation layer targeting a carried colony.
- **Phase 2** — graphics, carried-world rendering, the aura's look. `U1` and `U2` live here.
- **Phase 3** — modelling, then the reveal chain. Author's own work.

Confirmed working in 4.4.6 by live run: `every_owned_fleet`, `random_owned_fleet`,
`log`, `country_event` fired from console, `set_country_flag`, `set_fleet_flag`.

---

## Rules that are load-bearing

Breaking these breaks the design, not just the build.

1. **Never iterate the galaxy's ships on a pulse.** The counter is *maintained*, not
   measured. The reconciler is allowed to scan only because it touches one system,
   monthly. A real save measured 3,287 fleets and 6,452 planets.
2. **Localisation keys name roles, never names** — `BUILDER_RACE_NAME`, not `ARCHELIAS`.
   The pending naming pass then changes values only and never becomes a dependency.
3. **`common/ship_sizes`, `section_templates`, `component_templates` are contested** by
   NSC3 and EFCF. Additive, `ark_`-prefixed entries only. Never overwrite their files —
   the risk is overwriting, not coexisting.
4. **The console is scope-sensitive.** Use `event`, never `effect`, and deselect first.
   `Wrong scope for effect` and `got planet expected country` are the same mistake.
5. **Localisation files need a UTF-8 BOM** or they fail silently.

---

## Loop

```
python3 tools/validate.py          # before every commit
python3 tools/watchlog.py          # while testing, tails both logs filtered to ark_
python3 tools/install_local_mod.py --write   # registers the repo as a local mod
```

Launch Stellaris with **`-logall`** or repeated log lines are swallowed and a second test
run appears silent. Full procedure in `docs/TESTING.md`.

---

## What is not verified

Field, trigger and effect names in this mod are **not all confirmed for 4.4.6**. Stellaris
skips unknown ones *silently*, so a test that never ran looks identical to one that passed.

**Ground truth is `script_documentation/` in the Stellaris data folder** — the game writes
it and it is version-accurate. Every wiki is downstream of it, and both wikis are blocked
from the cloud session this was written in.

Also: country and fleet names resolve to empty strings inside a `log` effect (their names
are localisation-composed). Solar systems print fine. Log fixed strings, not names.

---

## Still the author's to decide

- **G38** — four proper nouns need replacing. Budgeted at a day, 2–3 syllables.
- **G4** — what the reveal chain actually says. Deferred until after modelling. Note that
  without it the kill sequence is unreachable, so v0.1 is private-testing only.
- **G5** — real numbers. Ratios rather than absolutes are in map §22.
