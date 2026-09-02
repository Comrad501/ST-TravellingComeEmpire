# Ark of Destruction — working notes for whoever picks this up

A Stellaris 4.4.6 mod: a travelling comet empire that carries captured worlds and can
only be killed through a staged sequence. **Design lives in `docs/architecture-map.html`**
(25 sections, 22 diagrams, every decision and why). This file is operational only — read
the map before changing design, read this before changing code.

---

## Do this first

Re-run the suite. The last recorded run cannot be trusted - the harness was corrupting
its own output (see rule 6). Deselect everything, then:

```
event arktest.1
```

Search `game.log` for `ARK TEST` - **not** `[ARK TEST]`, which never appears.

**The variable-scope probe is answered.** `arktest.5` reported `COUNTRY`, `PLANET` and
`SYSTEM` all holding a variable, and `>= 7` matching on a scope known to work. So
solar-system storage is sound and equality works: **the caching design in the map stands
unchanged, and the containment counter keeps its home.** The failing assertions were the
harness, not the design.

Root cause, confirmed against vanilla and `error.log`: square brackets in a log string.
Inside `common/` the metascript parser reads `[X]` as the opening of a `[[PARAM] ... ]`
block and eats the bracket plus one character - hence five `Invalid macro entry in
ark_debug_reset: RK DEBUG` errors at load, `ark_debug_log_inhibitors` logging nothing at
all, and T3 producing no verdict. Fixed: prefixes are plain `ARK TEST |` text and the one
real command is escaped `\\[This.GetName]`. `tools/validate.py` now fails on a bare one.

Also fixed in the same pass, all verified against vanilla: `cost = 40` is not a key of
`utility_component_template` (it broke the block mid-parse, which is what cascaded into
`Invalid component set`), `ship_size_military_5` is not a sprite, `generic_01` is not a
graphical culture, and the two static modifiers had no localisation keys.

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
6. **No bare `[` in a string under `common/`.** The metascript parser claims it and
   silently swallows the rest of the effect. Escape a real command as `\\[This.GetName]`;
   for literal text drop the brackets entirely - the localisation layer eats those too, so
   a `[TAG]` prefix prints as nothing. Bare `[` is fine in `events/`.

---

## Loop

```
py tools/validate.py          # before every commit (python3 is not on PATH on Windows; use py)
py tools/watchlog.py          # while testing, tails both logs filtered to ark_
py tools/install_local_mod.py --write   # registers the repo as a local mod
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
