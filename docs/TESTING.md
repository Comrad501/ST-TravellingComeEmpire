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

## 2. Turn the console on

Press `` ` `` or `~`. Then:

```
debugtooltip
```

Hovering anything now shows its internal ID, which you will want constantly.

## 3. Set up

Select your own empire's capital, then:

```
effect ark_debug_make_ark = yes
effect ark_debug_tag_all_ships = yes
effect ark_debug_dump = yes
```

`ark_debug_make_ark` marks one of your existing fleets as the Ark, so mechanics can be
exercised before the real hull exists. Nothing here needs the placeholder ship size to
work.

## 4. Run the suite

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

## 5. Reset between runs

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

## Before release

Delete `common/scripted_effects/99_ark_debug_effects.txt` and
`events/ark_debug_events.txt`, or guard them behind a flag. They are deliberately
destructive and there is no reason to ship them.
