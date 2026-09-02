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

Choosing crisis opened four more (`G13`-`G16`), including a contradiction between the
notes' four-slot Planet Catcher cap and a losing condition defined as collecting worlds
indefinitely. `G13` is upstream of every balance number.

## Build order

Steps 1–6 require no unknown to be resolved: mod skeleton, Ark hull and comet shell, empty
stub seam, containment counting, planet capture (base-game backing), situation layer.
Steps 7–8 are gated on U1/U2 and U5 respectively. See the architecture map for detail.
