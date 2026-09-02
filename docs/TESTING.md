# Testing the Ark mechanics

There is no way to hand-author a valid Stellaris save: a `gamestate` is a serialized
object graph with thousands of interlinked references, and any dangling one crashes or
corrupts. Editing an existing save is worse than useless here - a real campaign is a poor
test bed, and the save is locked to the exact mod set it was made with.

What works instead is a deliberately tiny galaxy plus an in-game test harness. That gets
you the same thing a debug save would, and it is repeatable.

## 1. Build the test galaxy

New game, and deliberately minimal so events are easy to attribute:

| Setting | Value | Why |
| --- | --- | --- |
| Galaxy size | 200 stars | Smallest available; keeps object counts low |
| Shape | Elliptical | Short paths, fewer chokepoints to confuse jump tests |
| AI empires | **1** | You plus one is enough to test worthiness and containment |
| Advanced AI starts | 0 | Removes noise |
| Fallen empires / Marauders | 0 | Removes noise |
| Crisis strength | any | The vanilla crisis is irrelevant here |
| Ironman | **OFF** | The console is disabled in Ironman |

Enable **only** `Ark of Destruction` if you can. If NSC3 and EFCF are loaded too, that is a
useful second pass later - but test alone first, so a failure is unambiguous.

## 2. Launch options - one of these is not optional

Set these on the Stellaris executable (Steam: Properties -> Launch Options):

```
-debug_mode -debugtooltip -logall
```

| Option | Why |
| --- | --- |
| `-logall` | **Required.** Stellaris logs only the *first* occurrence of an identical string, so a second run of the test suite appears completely silent. A swallowed `PASS` looks exactly like a test that never executed. This disables that. |
| `-debug_mode` | Extra logging, including things that are otherwise dropped |
| `-debugtooltip` | Starts with debug tooltips on, so you skip typing it each session |

Others that exist and are occasionally useful: `-script_debug`, `-logprefix`,
`-logpostfix`.

## 3. Turn the console on

Press `` ` `` or `~`. Then:

```
debugtooltip
```

Hovering anything now shows its internal ID, which you will want constantly.

## 4. Set up

Select your own empire's capital, then:

```
effect ark_debug_make_ark = yes
effect ark_debug_tag_all_ships = yes
effect ark_debug_dump = yes
```

`ark_debug_make_ark` marks one of your existing fleets as the Ark, so mechanics can be
exercised before the real hull exists. Nothing here needs the placeholder ship size to
work.

## 5. Run the suite

```
event arktest.1
```

Then open `game.log` (Documents\Paradox Interactive\Stellaris\logs\game.log) and search for
`[ARK TEST]`. Every line is `PASS` or `FAIL`.

| Test | What it proves |
| --- | --- |
| T1 | A clean system reads as uncontained, and the shared trigger agrees |
| T2 | The counter tracks additions and losses, and the clamp refuses to go negative |
| T3 | The reconciler agrees with the maintained counter |

**T3 is the one that matters.** The whole containment design is a maintained counter rather
than a measured one, and drift between the two is its characteristic failure - silent,
gradual, and invisible without exactly this check.

## 6. Reset between runs

```
effect ark_debug_reset = yes
```

## What this cannot tell you

The harness proves the *logic* holds. It cannot prove the **names** are real. If a trigger
or effect name is wrong for 4.4.6, the game usually skips it silently rather than erroring,
and a skipped assertion looks identical to a passing one that never ran.

So before trusting a green run, check `error.log` in the same folder for anything
mentioning `ark_`, and confirm the names against `script_documentation/` in the local data
folder. The game writes that directory itself; it is the only version-accurate source, and
every wiki is downstream of it.

## Existing tooling worth having

None of this replaces the harness - it does the surrounding work.

| Tool | What it is |
| --- | --- |
| [A Debug Mod for Modders](https://steamcommunity.com/sharedfiles/filedetails/?id=1920276468) | Cheat/testing layer, load order 99999 so it sits on top of most mods |
| [Developer Tool Kit](https://steamcommunity.com/sharedfiles/filedetails/?id=904179341) | Adds edicts intended for play-testing a mod quickly |
| [Sandbox testing guide](https://steamcommunity.com/sharedfiles/filedetails/?id=907837096) | A community recipe for a reusable test galaxy - tiny, 1 AI, no advanced start, no FE, crisis off. Independently the same shape as the table above. |
| [stelmod-debug](https://github.com/Swords206/stelmod-debug) | Real-time log watcher. Filters to *your* mod's messages, colour-codes errors, alerts on new ones. Windows/Linux/macOS. |
| [Stellaris-Error-Log-Inspector](https://github.com/non-npc/Stellaris-Error-Log-Inspector) | Reads `error.log` and guesses which mod is responsible. Useful with seven mods loaded. |

**There is no debug *save* on the Workshop**, and that is not an oversight - saves are
version- and mod-locked, so a shared one would break on the next patch or the next mod
change. The community answer is the same as ours: a small galaxy plus console setup.

## Before release

Delete `common/scripted_effects/99_ark_debug_effects.txt` and
`events/ark_debug_events.txt`, or guard them behind a flag. They are deliberately
destructive and there is no reason to ship them.
