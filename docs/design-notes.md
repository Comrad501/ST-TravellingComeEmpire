# Ark of Destruction — Stellaris Mod Concept Notes

Working notes from a design conversation. Goal: a Gatlantis-style travelling
comet empire — mobile capital ship, no fixed homeworld, captures and carries
planets, wrapped in a regenerating gas shell, defeatable only through a
staged sequence rather than raw HP attrition.

Target version: Stellaris 4.4.6 (Pegasus). Base install + Apocalypse,
Federations, Nemesis confirmed available. **Nomads DLC not currently owned**
— arkship mechanics referenced below assume it, or a from-scratch
reimplementation of the same primitive (colony detached from a planet).

---

## 1. Core concept

- **Ark of Destruction** — mobile capital hull, houses the empire's seat of
  government. No claimed home system.
- **Comet shell** — cosmetic + defensive layer over the hull. Regenerates.
  Must be stripped before the hull can be damaged conventionally.
- **Planet Catcher** — the Ark can capture up to ~4 worlds (canon: Zemuria +
  3 others) and carry their populations with it as attached colonies.
- **Golem** — a captured/looted superweapon, not a movement device. Kills a
  target empire's population outright when seized from the Ark's throne
  room. Separate from the Ark itself.
- **Shipborne FTL inhibitors** — Garmillan-style: ships (not starbases)
  project a containment field. The field's strength is a function of how
  many inhibitor-equipped ships are alive in-system. Field degrades as
  ships die rather than switching off.
- **Anti Wave Motion Lattice** — hypothetical device that fully disables a
  target's drive rather than just constraining movement. No vanilla
  precedent found; would need a new component from scratch.

Naming note: "Golem" (the throne-room kill-switch) and "Ark of Destruction"
(the mobile fortress with the Planet Catcher) are two separate objects in
canon — don't conflate them in implementation.

---

## 2. Why planets can't literally move (and the workaround)

Stellaris has no mechanism to relocate a `galactic_object`/planet entity.
"Planets travel" is solved instead by **decoupling the colony from the
planet** — this is literally what the Nomads DLC arkship does. The colony
(pops, jobs, districts, name) travels; the planet object never moves because
there is no planet object involved once captured.

**Capture = two operations, both with vanilla precedent:**

1. **Strip the source world** — reuse Colossus-style planet-class-change
   logic (e.g. `pc_shattered`), clearing pops from the original planet.
2. **Attach to the Ark** — transplant the world's pops/name/deposits into a
   colony slot carried by the Ark, same primitive as an arkship colony.

Neither step requires moving a planet object. This is the load-bearing
insight for the whole mod — confirm before designing anything else around
"moving" planets.

---

## 3. Visual / rendering approach

- **Layer, don't swap states.** Comet shell is a persistent additive/particle
  effect parented to the Ark entity, toggled by a flag — not a second
  `ship_size` swapped in via event. Swapping means transferring all state
  (modules, tier, damage, leaders, attached colonies) on every transition —
  fragile and expensive. Layering never destroys the ship object.
- Comet shell = shield-layer analog: very high HP, aggressive regen. Burn it
  down to expose the hull to conventional damage; leave it alone and it
  returns. This gives the "state" a mechanical cost (upkeep, presumably
  energy) rather than being purely cosmetic.
- **Planet Catcher rendering — OPEN QUESTION, unresolved:**
  - Preferred approach: model captured worlds as **section variants**
    (empty cradle / 1 / 2 / 3 / 4 planets), swapped via
    `common/section_templates` the way bow/stern loadouts already work.
    Sections are official, supported render slots (see §5).
  - **Unconfirmed: can a section be swapped by script outside a shipyard
    refit?** Normally section changes = drydock refit. Need to prototype
    this before committing — it decides whether planet capture can happen
    mid-flight or requires the Ark to dock.
  - Fallback if sections can't swap live: single mesh with all four cradles
    always modeled, planets shown/hidden via visibility flag instead of
    section swap. Uglier, but certain to work.
  - Alternative considered: `create_ambient_object` parented to the fleet.
    **Unconfirmed whether ambient objects track a moving parent fleet.**
    Untested — don't rely on this without checking first.
- Keep comet shell as a particle effect (`gfx/particles/`) rather than
  geometry, for performance — same asset category as engine trails/shield
  impacts, so there's a working precedent to copy rather than invent.

---

## 4. Combat / kill sequence design

Rejected approach: large HP pool ("boss you out-build"). Precedent from
vanilla for *why* this is wrong: the Contingency and the Blokkat-Vester are
both **stage-gated**, not attrition-gated — flatly invulnerable until a
specific non-combat objective is met.

**Three-stage kill, mapped onto show beats:**

1. **Strip the shell.** Conventional fire can't do it (regenerates). Needs
   a single massive discharge — map this onto the Nomads **Stellar Cannon**
   megastructure (ships in same DLC wave, thematically/mechanically fits).
   Opens a time-limited window with the shell down. Gives the defending
   side a real mid-game objective (build + protect the Stellar Cannon)
   since the Ark will prioritize killing it.
2. **Board it.** If captured worlds are attached colonies (§2), they
   already have an invasion surface — ground armies land and fight inward
   using the existing planetary invasion system. No new code needed. Also
   makes the Planet Catcher a liability, not just a power source: every
   captured world is another door in.
3. **The kill.** No vanilla self-destruct precedent — pick one or both:
   - **Golem as loot**: seize it via the boarding stage; functions as a
     one-use species-targeted weapon (cf. Neutron Sweep) that ends the
     Gatlantean population specifically. Rewards stage 2 directly.
   - **Wave-motion core overload**: player-side one-shot self-destruct
     component, requires the carrier to be the player's top-tier hull (or
     scale damage off carrier value) to stop people building throwaway
     hulls just to carry it.

**Losing condition needed** — a crisis you can ignore isn't a crisis. Cf.
Blokkat-Vester: at 95% harvested it deletes the rest of the galaxy outright.
Ark equivalent: if the Stellar Cannon is never built, the Ark keeps
collecting worlds indefinitely.

---

## 5. Shipborne jump inhibitor (containment) mechanic

Inverts the usual fight: defenders don't need to win, they need to
**survive in place**; the Ark doesn't need to win, it needs to **thin the
defenders below a threshold, then jump.** Counterplay is positional, not
purely attritional, on both sides.

- Component (aux or spinal slot): FTL-inhibition aura, radius R. Vanilla
  precedent: starbase inhibitors already block FTL except back the way a
  fleet came — this is the same effect, ship-mounted instead of
  base-mounted.
- Containment holds while **N inhibitor-equipped ships are alive within
  radius R** of the target (the Ark). No binary on/off — losing ships
  degrades containment strength progressively (this "emerges" for free if
  containment strength = a simple function of live-inhibitor-count).
- Ark's canonical counter to a ship-based trap = **area-effect damage**
  (supergravity in the show, hit *Andromeda* and others in one attack). A
  spinal AoE weapon is the correct tool for thinning emitters, which also
  differentiates the Ark from a normal single-target combatant.

### Implementation: counting ships without lagging the game

**Do not poll/iterate the ship list every tick.** At scale (confirmed
6,000+ ships in an actual playtest save) this is exactly the pattern that
causes late-game slowdown.

- Tag inhibitor-equipped ships with a flag on construction/component-fit,
  not inferred from components at runtime.
- Maintain a **system-scoped variable** (inhibitor count in system X)
  updated only by relevant `on_actions` — fleet enters system, fleet
  leaves system, ship destroyed — confirmed these on_action hooks exist
  (Event modding wiki: "entering of a system" etc. under On Actions).
- Situation / combat logic reads the cached variable, not a live count.
- Centralize the actual "is containment holding" test as a
  **scripted_trigger** (`common/scripted_triggers/`) so both the
  Situation's `monthly_progress` and the Ark's jump-eligibility logic call
  one shared definition instead of duplicating the check.

---

## 6. Situations — what they can and can't target

Source: `common/situations/99_README_SITUATIONS.txt` (ships with the base
game — read this file directly, it's authoritative for the installed
version). Secondary: Steam Guide id `3461023410` (German-language walkthrough
built from that same README, code blocks are useful even if prose isn't
read).

**Confirmed from README + wiki:**
- A Situation lives on a **country** scope. Its `target` is "usually a
  planet or empire."
- `modifier = {}` → applies to the country experiencing the situation.
- `target_modifier = {}` / `triggered_target_modifier = {}` → applies to
  the **target planet only**. README explicit: *"Does not work on other
  scope types!"*
- Lifecycle: `on_start`, `on_progress_complete` (progress ≥ 100),
  `on_fail` (progress < 0), `on_abort` (via `abort_trigger`). **Must call
  `destroy_situation = this`** from `on_progress_complete`/`on_fail` (or an
  event fired from there) — omitting this leaves the situation stuck
  forever.
- `monthly_progress` uses standard `common/script_values` weight syntax
  (`base`, `modifier` blocks with `add`/`factor`, each needs a `desc` loc
  key or the game errors).
- Stages support `on_first_enter` (effects, does NOT show in tooltip —
  intentional, avoids spoilers) and their own `modifier` (DOES show in
  tooltip).
- Progress bar can go both directions on one bar — 100 = complete, <0 =
  fail. Useful: "Ark escapes" vs "Ark contained" can be two ends of the
  same situation instead of two separate systems.

**Conclusion for this mod: a Situation cannot target the Ark/fleet
directly.** Two-part solution:
1. Target the situation at a **captured planet** (e.g. Zemuria-in-the-cage)
   — this is why the Planet Catcher matters mechanically, not just
   thematically. Gives situations something valid to hook into.
2. For containment/combat logic that needs to live on the ship itself, use
   **`fleet_event` / `ship_event`** (event system, not situations — these
   scopes exist for events but not for situation targets). Situation =
   slow-burn UI/stage layer; fleet events = moment-to-moment ship behavior;
   the two talk to each other via flags/variables, per the caching approach
   in §5.

---

## 7. Music (nice-to-have, not blocking)

Standard music mod = playlist entry, not a trigger:
- `yourmod.asset`: `music = { name = "..." file = "....ogg" volume = 0.xx }`
- `yourmod.txt`: `song = { name = "..." }`
- Must be `.ogg`. Both files need **UTF-8 with BOM** encoding — a common
  silent-failure cause if skipped.
- This only adds a track to the shuffled in-game playlist. **No native
  event → music trigger found in documentation searched so far.**

Possible workaround (unconfirmed): the "Galaxy View Music Injector" mod
achieves context-specific music not through the song system but by
**overwriting an ambient sound asset** (`sound/ambient/galaxy_96.wav`) that
the engine already triggers on a context change (entering galaxy map). Note
that context requires **`.wav`**, not `.ogg` — different pipeline than the
playlist system.

**Open question, unresolved:** whether `on_first_enter` (situation stage)
or any effect can fire a sound/music cue directly. If yes, that's the clean
hook for "Ark music plays when shell drops" etc. Needs checking against the
effects list, not yet done.

---

## 8. 3D assets / pipeline

- Stellaris uses proprietary binary formats, not a standard interchange
  format directly:
  - **`.mesh`** — geometry
  - **`.anim`** — animation
  - **`.dds`** — textures (DXT-compressed)
  - **`.asset`** — binds mesh + animation + locators together, lives under
    `gfx/models/`
- **Import/export tooling:**
  - **io_pdx_mesh** (github.com/ross-g/io_pdx_mesh) — Blender addon (also
    Maya). Handles both import and export. Supports **mesh-less export**
    specifically to define ship frames (slots/locators without geometry) —
    relevant for defining the Ark's capture-slot locators before any art
    exists. Blender is the sane route given existing BlockBench/LibreSprite
    use.
  - **Clausewitz Maya Exporter** — official Paradox tool, Maya-only.
- **Locators**: named mount points defined in `.asset`, referenced by
  `locatorname` in `section_templates` (confirmed working — this is how
  `wave_cannon_01` etc. are wired up in the EFCF mod already installed).
  One old forum report of difficulty adding **custom** locators to a mesh —
  dated, likely improved since ("export selected only now works for
  locators" appears in io_pdx_mesh release notes) but **verify early**,
  since locators are the actual mechanism the Planet Catcher needs.

---

## 9. Documentation sources (verified live, as of this conversation)

- **Paradox wiki**: `stellaris.paradoxwikis.com` — primary reference.
  `Ship_modding`, `Event_modding`, `Scopes`, `Situations` pages all used
  above. Note: Ship_modding page itself hasn't been touched in ~2+ years,
  so cross-check anything Nomads/4.x-specific against DEBCF below rather
  than trusting it alone.
- **DEBCF wiki** (github.com/udkudk/DEBCF/wiki) — community modding-
  framework docs, explicitly maintained for **v4.4.\*** (matches installed
  version), commits through late June 2026. Better source for anything
  post-Nomads. Has an "Overwriting specific elements" page on load-order
  behavior — read before anything else in a multi-mod setup.
- **`common/situations/99_README_SITUATIONS.txt`** — ships with the base
  game install. Authoritative for situation syntax on this exact version.
  Read directly rather than relying solely on secondary guides.
- **Steam Guide `3461023410`** — situation modding walkthrough built from
  the README above (German prose, but code blocks map directly to the
  README and are useful as worked examples).

---

## 10. Open questions to resolve before/during implementation

1. **Can a ship's `section_templates` slot be swapped by script outside a
   shipyard refit?** Decides whether Planet Catcher capture can render
   mid-flight (§3). Highest-priority unknown — blocks the core visual
   concept.
2. **Do `create_ambient_object`s track a moving parent fleet?** Fallback
   path for planet-carrying visuals if (1) is no. Untested.
3. **Can any effect available in `on_first_enter` (situation) or in event
   effects fire a sound/music cue directly**, vs. only via the static
   playlist/ambient-asset-overwrite routes in §7? Lower priority
   (music is a nice-to-have).
4. Confirm whether Nomads DLC's colony-detached-from-planet primitive is
   moddable/reusable directly, or whether it needs to be reimplemented from
   the Colossus + colony-transplant primitives in §2 as a from-scratch
   equivalent (relevant if this stays base-game + Apocalypse/Federations/
   Nemesis without adding Nomads as a hard dependency).
