---
name: faust-dsp
description: Work with Faust DSP programs, including syntax checks, offline audio analysis, local realtime/browser runtime startup, parameter control, audio metrics, and debugging generated sound. Use when the user asks to create, analyze, compile, play, test, debug, or tune Faust .dsp code, Faust audio effects, Faust synthesizers, Faust WASM runtimes, or Faust MCP workflows.
---

# Faust DSP

## Overview

Use this skill to help a user build and test Faust DSP code. Prefer the bundled
`scripts/faust_runtime.py` launcher over manually running upstream server files;
it installs the local runtime on demand, starts only what is needed, records
runtime state, and closes owned background processes safely.

This skill wraps the runtime ideas from `sletz/faust-mcp` without vendoring that
repository by default. The launcher clones it into the user's cache when needed.

## Decision Path

1. For syntax checks or offline signal analysis, run a one-shot command:
   `python3 scripts/faust_runtime.py analyze --dsp path/to/file.dsp`.
   This uses the upstream stdio client/server and exits when complete.
2. For realtime browser audio or UI work, start the browser runtime:
   `python3 scripts/faust_runtime.py start --kind browser`.
   Then open the reported local URL and ask the user to unlock audio if needed.
3. For realtime Node audio, use `start --kind node` only when the user needs
   local audio output, MIDI, or the Node backend specifically.
4. When a background runtime was started, call
   `python3 scripts/faust_runtime.py stop` before finishing unless the user
   explicitly asks to keep it running.
5. If dependencies fail, run `python3 scripts/faust_runtime.py doctor` and read
   `references/install-and-dependencies.md`.

## Common Commands

All commands are run from this skill directory unless an absolute script path is
used.

```bash
python3 scripts/faust_runtime.py doctor
python3 scripts/faust_runtime.py ensure
python3 scripts/faust_runtime.py analyze --dsp assets/examples/filter.dsp
python3 scripts/faust_runtime.py start --kind browser
python3 scripts/faust_runtime.py status
python3 scripts/faust_runtime.py call --tool get_status
python3 scripts/faust_runtime.py stop
```

For a temporary browser runtime around one command, use `with-runtime` so cleanup
happens even if the command fails:

```bash
python3 scripts/faust_runtime.py with-runtime --kind browser -- \
  python3 scripts/faust_runtime.py call --tool get_status
```

## Result Interpretation

- `status: success` means the Faust runtime compiled and rendered or started the
  DSP successfully.
- `is_silent: true` usually means the program produced silence, the tested input
  was missing, or gain/envelope controls are closed.
- `max_amplitude > 1.0` or high clipping metrics indicate clipping risk.
- Realtime parameter paths come from Faust JSON. Always call `get_params` before
  setting a parameter if the path is unknown.
- Browser audio may require a user gesture to unlock the AudioContext. Do not
  treat that as a DSP failure.

## References

- Read `references/runtime-selection.md` when choosing between offline,
  DawDreamer, browser, and Node runtimes.
- Read `references/tool-surface.md` for the upstream tool names and argument
  shapes.
- Read `references/install-and-dependencies.md` when setup or dependency checks
  fail.
- Read `references/output-schemas.md` when interpreting JSON metrics.
- Read `references/provenance.md` before changing attribution, licensing notes,
  or README wording about `sletz/faust-mcp`.
