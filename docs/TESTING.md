# Testing the Ark mechanics

There is no way to hand-author a valid Stellaris save: a `gamestate` is a serialized
object graph with thousands of interlinked references, and any dangling one crashes or
corrupts. Editing an existing save is worse than useless here - a real campaign is a poor
test bed, and the save is locked to the exact mod set it was made with.

What works instead is a deliberately tiny galaxy plus an in-game test harness. That gets
you the same thing a debug save would, and it is repeatable.

## 0. Get the mod loading first

See `Installing it locally` in the README - `tools/install_local_mod.py --write`. The short
version: the `ugc_*.mod` files already in your mod folder are Workshop pointers, not data,
and a local mod needs its own.

**On Windows, quote any path you pass.** `Paradox Interactive` contains a space, so an
unquoted `--stellaris-dir` gets split by the shell and argparse rejects the remainder:

```powershell
py tools\install_local_mod.py --stellaris-dir "C:\Users\you\OneDrive\Dokumenty\Paradox Interactive\Stellaris"
```

Auto-detection handles localised Documents folders (`Dokumenty`, `Dokumente`, `Documentos`)
and OneDrive redirection, so you should not normally need the override at all.

**If the mod does not appear in the launcher after writing the pointer:**

1. Close the launcher entirely (check the tray) and reopen. It reads its mod list once at
   startup.
2. Confirm the `path=` in the pointer is correct and uses forward slashes, even on Windows.
3. Confirm `descriptor.mod` exists *inside* the mod folder as well - the pointer and the
   descriptor are two separate files and the game wants both.
4. Check `error.log` for a parse complaint about the pointer itself.

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

### Deselect first. This is the whole trick.

The console fires an event on whatever you have **selected**. Every event here is a
`country_event`, so with a planet selected you get:

```
got planet expected country
```

and with `effect` you get `Wrong scope for effect 'every_owned_fleet'`. Same cause, two
messages.

**Press Escape, or click empty space, so nothing is selected. Then run the commands.**

If you would rather be explicit than remember to deselect, the console takes a target:

```
event arktest.1 <your country id>
```

Hover your own empire with `debugtooltip` on to read that id. It is usually `0` in a
single-player game, so `event arktest.1 0` normally works.

Use `event`, never `effect` - `effect` has no target argument and is entirely at the mercy
of your selection.

The console's `effect` verb runs in whatever you have *selected*. With a planet selected
the scope is a planet, and `every_owned_fleet` is a country-scope effect - which produces
`Wrong scope for effect 'every_owned_fleet'` in `error.log` and does nothing. A
`country_event` fired from the console always lands on the player country regardless of
selection, so every debug action has an event wrapper:

```
event arktest.10      set up: mark a fleet as the Ark
event arktest.11      set up: tag every owned ship as inhibitor-fitted
event arktest.12      dump current state
event arktest.13      reset everything
```

`arktest.10` marks one of your existing fleets, so nothing here needs the placeholder ship
size to exist.

## 5. Run the suite

```
event arktest.1
```

Then read `game.log` (or use the watcher) and search for `[ARK TEST]`. Every line is `PASS`
or `FAIL`.

| Test | What it proves |
| --- | --- |
| T1 | A clean system reads as uncontained, and the shared trigger agrees |
| T2 | The counter tracks additions and losses, and the clamp refuses to go negative |
| T3 | The reconciler agrees with the maintained counter |

**T3 is the one that matters.** The whole containment design is a maintained counter rather
than a measured one, and drift between the two is its characteristic failure - silent,
gradual, and invisible without exactly this check.

## Reading the log

Two things learned the hard way on the first run:

**Names do not print for countries or fleets.** Their names are localisation-composed (a key
plus variables), and `[This.GetName]` resolves to an empty string in a `log` for those
scopes. That is why the first run logged `ark fleet found:` with nothing after it. Solar
systems have literal names and do print. The harness now logs fixed identifying strings
instead of names.

**Other mods' errors appear in the same file.** Lines like

```
Error in change_pc effect, Could not find planet or randomlist with key:
pc_dark_fractured_unstable  file: events/EFCF_Fake_Ship_Auto_designs_events.txt
```

are EFCF referencing a planet class that is not loaded - pre-existing, unrelated to this
mod, and present whether or not it is enabled. `tools/watchlog.py` filters to `ark_` lines
precisely so these do not drown the signal.

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

## Watching the log

`game.log` carries thousands of lines from the base game and every other mod. With seven
mods loaded, finding ours by eye does not scale.

```
python3 tools/watchlog.py
```

It tails `game.log` and `error.log`, shows only lines matching `ark_`, colours `FAIL` and
errors red and `PASS` green, survives the truncation Stellaris does on launch, and prints a
tally when you Ctrl-C. Pass `--dir` if it cannot find the logs folder, `--all` to drop the
filter.

Stdlib only. No install, no dependencies, no network calls, about a hundred lines. Read it
before you run it - that is rather the point.

## A note on third-party tooling

There are Workshop mods and GitHub tools that cover similar ground. **They are not the same
kind of risk, and the difference matters:**

| Kind | What it can do |
| --- | --- |
| **Workshop mods** (Debug Mod for Modders, Developer Tool Kit, Cheat Panel) | Script and data files the *game* interprets. They cannot execute code on your machine. Low risk. |
| **Standalone tools** (`.bat`, `.exe`, or a script you run yourself) | Run with your user privileges. They can read, write and send anything you can. A README is not evidence of safety, and neither is a star count. |

An earlier version of this file recommended a GitHub log-watcher with a `.bat` installer on
the strength of its README. That was the wrong basis for a recommendation - nobody had read
its source, including me. `tools/watchlog.py` above replaces it and is short enough to
audit in one sitting, which is the only reason to trust it either.

If you do want the Workshop debug mods, they are the safer category:
[A Debug Mod for Modders](https://steamcommunity.com/sharedfiles/filedetails/?id=1920276468),
[Developer Tool Kit](https://steamcommunity.com/sharedfiles/filedetails/?id=904179341), and
a [sandbox recipe](https://steamcommunity.com/sharedfiles/filedetails/?id=907837096) whose
galaxy settings independently match the table above.

**There is no debug *save* on the Workshop**, and that is not an oversight - saves are
version- and mod-locked, so a shared one breaks on the next patch or the next mod change.

## Before release

Delete `common/scripted_effects/99_ark_debug_effects.txt` and
`events/ark_debug_events.txt`, or guard them behind a flag. They are deliberately
destructive and there is no reason to ship them.
