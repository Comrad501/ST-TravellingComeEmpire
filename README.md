# Ark of Destruction

A Stellaris mod concept: a Gatlantis-style travelling comet empire. A mobile capital
hull with no fixed homeworld, wrapped in a regenerating comet shell, carrying captured
worlds as detached colonies, killable only through a staged sequence rather than HP
attrition.

**Status: planning only. No mod code has been written yet.**

**v0.1 scope: the Ark is an AI crisis.** A playable "displaced empire" version is the
more interesting build and stays on the roadmap, but it is deferred until the mechanics
have been playtested. Build steps 1-6 sit in the shared core and are not wasted either way.

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

**Caveat:** in single-player the coalition is mostly AI, and Stellaris AI does not reliably
coordinate against crises. The cooperative outcome must be reachable without the AI
choosing it (`G21`).

## Build order

Steps 1–6 require no unknown to be resolved: mod skeleton, Ark hull and comet shell, empty
stub seam, containment counting, planet capture (base-game backing), situation layer.
Steps 7–8 are gated on U1/U2 and U5 respectively. See the architecture map for detail.
