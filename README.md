# Ark of Destruction

A Stellaris mod concept: a Gatlantis-style travelling comet empire. A mobile capital
hull with no fixed homeworld, wrapped in a regenerating comet shell, carrying captured
worlds as detached colonies, killable only through a staged sequence rather than HP
attrition.

Built by the **Archelias**, a precursor civilisation. **Zemuria** is one of the worlds
the Planet Catcher captures, not its builders.

The Archelias were humanoid, and concluded that humanoid form intrinsically tends to
violence and chaos. The Ark is therefore not a conquest engine but a **correction** -
built to end the flawed legacy they left behind. Two consequences follow, and they are
the spine of the acquisition design:

- **A machine empire is not that legacy**, so it is never evaluated by worthiness. It can
  approach and hold the Ark - and can never be `ASSIMILATE`d, only `SHATTER`ed. The only
  empires that can hold it are the only ones with nothing held in escrow if they fail.
- **Only a human can activate it.** The correction requires the consent of the flawed.
  A machine empire can own the Ark and still not switch it on. The activation key checks
  for a living organic pop, not a strict portrait group - the humanoid-form reasoning is
  the Archelias' stated rationale, and it was wrong. Machines make war too; the exemption
  is a flaw in the device's premise, not a fact about machines.
- **The activator survives, and their world goes into a cradle.** Activation converts one
  of the empire's worlds into the first carried colony, so the Ark never starts empty and
  the acquiring empire is bound to it from the first moment.

**There are two Archelian arks.** `Shambleau` is the seeder - an artificial planet that
spread Archelian genes and is why human species exist. The **Ark of Destruction**, the
White Comet, is the one with the Planet Catcher and the one this mod is about. They are
not the same vessel.

What the Ark actually is: an Archelian ark that **reshapes itself to fit its user's needs
when awakened**. The cage is not a perversion of its design - it is the ark becoming what
its wielder asked for. That also quietly supports `U1`'s live section swap: a vessel that
changes its own shape is the fiction, not a rendering trick.

So acquisition needs two keys rarely in one hand: a machine empire to hold it, and a
living humanoid to start it. A Determined Exterminator disqualifies itself by purging
every hand that could have turned the key.

**Status: planning only. No mod code has been written yet.**

**v0.1 scope: the Ark is an AI crisis.** Build steps 1-6 sit in the shared core.

**There is exactly one Ark, buried in the galaxy from the first day.** It is placed at
galaxy generation as a flagged system with *no fleet spawned* - a flag and a location,
costing nothing - and only instantiates when something wakes it. It is not spawned by a
crisis system on a schedule; the crisis is what happens if nobody reaches it first.

**v0.2 proposal: the Ark is acquirable by a machine empire** via a precursor event chain,
racing the wake date. Finish first and it is yours; fail and it wakes on its own. The
chain unlocks at mid-game (`mid_game_years_passed >= 0`, so it respects the player's own
galaxy setup). **AI empires can win the race too** - and the machine-empire restriction
keeps the eligible field to however many machine empires the galaxy generated, typically
none to three.
Crucially this is *acquisition, not displacement* - the player keeps their empire and
gains a fortress - so `G2`'s economy problem does not arise, and Nemesis' Become the
Crisis supplies the galaxy's response. The branch reduces to one new system (the chain)
rather than the five the displaced-empire version needed. See `§17`.

**DLC note:** archaeological sites can be created and excavated without Ancient Relics,
but **minor artifacts and relics require it** and it is not owned. Chapter rewards must be
ordinary ones - a tech option, a modifier, an event.

Target version: Stellaris 4.4.6 (Pegasus).
Owned DLC: Apocalypse, Federations, Nemesis. **Nomads is not owned** — the mechanics that
would use it sit behind a stub seam so the backing implementation can be swapped later.

## Lore stance

**Yamato-inspired, not a retelling.** The design has already diverged structurally - a
buried object raced for by three parties, worthiness verdicts with eviction, a
regeneration threshold, degrading containment. None of that is in the source. What remains
one-to-one is the **naming**, which is the cheapest layer to change and carries nearly all
the IP risk.

Four coined proper nouns (`Archelias`, `Gatlantis`, `Zemuria`, `Zworder`) and one
technology term (`wave motion`) want replacing. "Ark of Destruction" and "travelling comet
empire" are generic enough to keep. Cheapest done before build step 1, since localisation
keys are written there (`G38`).

## Contents

| Path | What it is |
| --- | --- |
| `docs/design-notes.md` | Source design notes. The origin document; everything else derives from it. |
| `docs/architecture-map.html` | Architecture map — subsystems mapped onto their Clausewitz directories, the two engine constraints that force the design, the staged kill sequence, the stub seam, and the open unknowns. Published as an artifact; this is the source. |

## The two constraints

Nearly every structural decision follows from these:

1. **Planets cannot be relocated.** There is no mechanism to move a `galactic_object`. The
   Ark carries a *colony detached from a planet*, not a planet.
2. **Situations cannot target a fleet.** A Situation is country-scoped with a planet or
   empire target. This is why the Planet Catcher is load-bearing rather than thematic — a
   carried colony is the only thing on the Ark a Situation can legally hook into.
3. **There is no browsable tech tree.** Research is a card draw: three weighted alternatives
   per area, and a card shown last hand has its weight halved next draw. Prerequisite chains
   are scriptable; a screen where the player *sees* the chain is not. So anything mandatory
   must not be left to the draw.

## Research structure

Gating a branch on the comet event works cleanly — `potential = { has_country_flag =
ark_revealed }` keeps the whole branch out of every draw pool until the Ark exists, so it
never dilutes the early game. The structure splits by whether content is required:

| Layer | Mechanism | Used for |
| --- | --- | --- |
| Mandatory spine | `common/special_projects/`, started with `enable_special_project` | The reveal chain (`G4`). Deterministic — assign a scientist, it completes. Cannot be missed. |
| Optional depth | `common/technology/` with `potential` + `weight_modifier`; `add_research_option` to force a card into hand | Branch techs that reward engagement but are not required |
| Scaling | Repeatable techs | Where "more firepower" lives — an empire raising its own share of the damage threshold |

Three branches, mirroring the three simultaneous requirements of the engagement:
engineering (anti-shell weapons), physics (inhibitor components), society (boarding
doctrine). The third unlocks from an archaeology site on a world the Ark shattered
(`create_archaeological_site`) — so the Ark's own destruction teaches its counter.

## Register status

Forty gaps and five unknowns were raised during design. `§22` of the architecture map
consolidates all of them. Current state:

- **Closed by evidence** (4): `G17` `relative_power` exists and is the vanilla mechanism;
  `G34` AI empires do take Become the Crisis and avoid competing when one already exists;
  `G6` and `G19` closed by later sections.
- **Closed by decision** (13): recorded in `§22`, each overridable.
- **Still yours** (4): `G30` capital, `G38` naming, `G11` scope, `G4` reveal-chain content.
- **Needs the game** (5): `U1`-`U4`, `G10` your iteration loop. `G9` is answered below.

## Verified against a real save

A 2539 save was parsed directly (`§24`). It confirms `Pegasus v4.4.6` and exactly
`Apocalypse` + `Federations` + `Nemesis`, and gives scale: 6,452 planets, 299 colonies,
~1.37M pop units, 3,287 fleets.

**`G9` answered.** `NSC3` and `EFCF` between them own `ship_sizes`, `section_templates`
and `component_templates` - the save contains `EFCF_Dreadnought_Bow/_Mid/_Stern` section
templates and 102 distinct EFCF objects, plus NSC3 classes and aura slots. Those are
exactly the three directories phase 2 needs, and **none of the directories phase 1 needs**
(`situations`, `script_values`, `scripted_triggers`, `on_actions`, `events`). Scoping
visuals out of v0.1 moved the compatibility risk out of it too.

**§5 is largely a recombination, not an invention.** Ship-mounted auras are vanilla
(`SHIP_AURA_TARGETING_GRID`, `SHIP_AURA_STRIKE_CRAFT`), the inhibition effect already
exists as `STARBASE_AURA_FTL_INHIBITOR`, `tech_ftl_inhibitor` is a vanilla technology, and
NSC3 adds dedicated aura slots (`NSC_SUPPORTSHIP_AURA_EMPTY`, `NSC_TITAN_AURA_EMPTY`).

**Capital calibration** (`G30`, second reading): median `planet_size` 19 (range 6-25), 4
districts, stability 97. A capital holds ~1.8x the pop of a median colony. Use the ratio,
not the absolute - pop scale drifts between patches.

**Nothing blocks v0.1.** `U1` was the last blocker and it only ever blocked *rendering*
the carried worlds - scoping visuals out of v0.1 moves it to phase 2.

## Phases

| Phase | Contents | Blockers |
| --- | --- | --- |
| **1 - v0.1** | Lore, situations, mechanics. Build steps 1-6: worthiness, containment logic, the shell threshold, capture. | none |
| **2** | Graphics experiments, the containment aura's appearance, carried-world rendering. | `U1`, `U2` |
| **3** | Modelling (author's own), then the reveal chain `G4`. | - |

Containment *logic* is phase 1; only the aura's *appearance* is phase 2.

Shipping v0.1 without `G4` is fine for private testing. It is **not playable by anyone
else** - without the reveal chain the kill sequence is unreachable by design.

**Localisation keys are named for roles, never for names** (`BUILDER_RACE_NAME`,
`WIELDER_RACE_NAME`, `FIRST_TAKEN_WORLD`), so the `G38` naming pass lands as loc *values*
whenever it happens and never becomes a sequencing dependency.

**`script_documentation/` in the local data folder is the ground truth** for every trigger
and effect name in these documents - the game writes it, and it is version-accurate in a
way no wiki is.

## Open unknowns

Tracked in the architecture map as `U1`–`U5`. Two are blocking:

- **U1** — can a ship's `section_templates` slot be swapped by script outside a shipyard
  refit? Decides whether planet capture renders mid-flight. Needs an in-game prototype.
- **U5** — the shell-stripping cannon in the kill sequence is Nomads content, but Nomads
  is not owned. Stage 1 needs a substitute or the kill sequence has no first step.

## Information gaps

Separate from `U1`-`U5`. The unknowns are questions the notes ask and cannot yet answer;
the gaps (`G1`-`G12`, in the architecture map) are areas the notes never reach. Four are
architectural and cannot be deferred:

- ~~**G1**~~ - **decided: AI crisis for v0.1.** See `§11` of the architecture map.
- **G2** - economy with no homeworld. Largely deferred by the G1 decision, since crises
  conventionally spawn fleets by event rather than building them.
- **G3** - what happens when the Ark dies, to the empire and to its carried colonies.
- **G4** - how a defender ever learns the kill sequence exists. **Now mandatory**: against
  an AI crisis the player has no other route to the rules.
- **G8** - AI behaviour. **Promoted to critical** by the G1 decision; still zero coverage.

Choosing crisis opened four more (`G13`-`G16`). Three more (`G17`-`G19`) came from the
worthiness mechanic below.

## Planet Catcher worthiness

Captured worlds are not taken indiscriminately. Each candidate is scored on two tiers -
empire-level (*who* the Ark preys on) and planet-level (*which of their worlds*) - and
the score yields one of three verdicts:

Structure, and why the kill sequence climbs: a gas shell (which is *both* the shield and
the supergravity area weapon - one organ, two roles) surrounds a castle tower above a
disk-shaped urban area above the Planet Catcher cage. The caged worlds sit at the bottom
and the throne at the top, so boarding a captured world means climbing the whole vessel.
`Golem` sits *beneath the throne* and kills the wielders instantly - it is the builders'
failsafe, not loot, and it was always there.

| Verdict | Effect |
| --- | --- |
| `ASSIMILATE` | Carried as a colony. Consumes one of the four slots. |
| `DISPLACE` | Beats the weakest held world, which is jettisoned to make room. |
| `SHATTER` | Destroyed in place. **Consumes no slot.** |

**This resolves `G13`.** A shattered world costs nothing, so the Ark can advance through
the galaxy indefinitely while never holding more than four worlds. The four-slot cap and
the "collects worlds indefinitely" losing condition stop contradicting each other.

**Scoring basis: strength sets the floor, damage escalates it.** Strength alone is
deterministic and punishes the leader every campaign; damage alone rewards turtling.
Worthiness is **maintained via `on_actions`, never recomputed by scanning** - the same
discipline as the containment count.

## Getting empires to fight together

Free-riding is the correct play in a crisis unless the mechanics make it wrong: everyone
gains if the Ark dies, but each empire gains more by letting someone else pay. Lore
asserting that doom is universal does not fix this. Five levers cut the loop (`§13`):

| | Lever | Relies on |
| --- | --- | --- |
| `L1` | Worthiness inversion - abstaining means `SHATTER` (permanent) rather than `ASSIMILATE` (pops survive, world recoverable by boarding) | nothing; it punishes the abstainer directly |
| `L2` | Public ledger - worthiness standings and Ark trajectory visible galaxy-wide | player attention |
| `L3` | Containment floor `N` set above any single empire's fleet | nothing; it is a constraint |
| `L4` | Cannon jointly funded through the Galactic Community | scripting, to be dependable |
| `L5` | Golem awarded to the largest contributor | scripting, to be dependable |

**L1 costs no new systems** - the score, the verdicts and the boarding surface all exist.
It does need teaching, since a player who assumes capture is the worse outcome reads the
whole mechanic backwards.

**Cooperation is rewarded, not gated** (`G20`).

**There is no cannon.** Stage 1 is sustained fleet fire (`§15`). The shell regenerates in
proportion to how damaged it is, so incoming fire and regeneration reach an equilibrium:

- Combined damage **below** the threshold - the shell flattens out and *never* falls, no
  matter how long the fight runs.
- **Above** it - the shell falls, and every extra gun shortens the descent.

Damage is natively additive across empires, so the coalition incentive lives in the combat
maths with nothing to build and nobody to coordinate with. The window is not a timer: the
shell stays down **only while fire is sustained above the threshold**, which collapses
containment, stripping and boarding into one simultaneous engagement - and gives the Ark's
spinal AoE weapon its purpose, since one wide attack degrades all three at once.

**What stops a superpower soloing it:** regeneration scales with the number of worlds the
Ark has collected. Early, one strong empire genuinely can - and should be allowed to.
Late, no single fleet is enough. The gate is *time*, not permission, and the Ark's own
growth becomes the difficulty curve.

`L3`'s containment floor softens to match (degrade, do not gate), and the contribution
counter still ranks empires for `L5`'s Golem award.

**Caveat:** in single-player the coalition is mostly AI, and Stellaris AI does not reliably
coordinate against crises. The cooperative outcome must be reachable without the AI
choosing it (`G21`).

## Build order

Steps 1–6 require no unknown to be resolved: mod skeleton, Ark hull and comet shell, empty
stub seam, containment counting, planet capture (base-game backing), situation layer.
Steps 7–8 are gated on U1/U2 and U5 respectively. See the architecture map for detail.
