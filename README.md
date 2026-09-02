# Ark of Destruction

A Stellaris mod concept: a Gatlantis-style travelling comet empire. A mobile capital
hull with no fixed homeworld, wrapped in a regenerating comet shell, carrying captured
worlds as detached colonies, killable only through a staged sequence rather than HP
attrition.

Built by the **Archelias**, a precursor civilisation. **Zemuria** is one of the worlds
the Planet Catcher captures, not its builders.

**Status: planning only. No mod code has been written yet.**

**v0.1 scope: the Ark is an AI crisis.** Build steps 1-6 sit in the shared core.

**There is exactly one Ark, buried in the galaxy from the first day.** It is placed at
galaxy generation as a flagged system with *no fleet spawned* - a flag and a location,
costing nothing - and only instantiates when something wakes it. It is not spawned by a
crisis system on a schedule; the crisis is what happens if nobody reaches it first.

**v0.2 proposal: the Ark is acquirable by a machine empire** via a precursor event chain,
racing the wake date. Finish first and it is yours; fail and it wakes on its own.
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
