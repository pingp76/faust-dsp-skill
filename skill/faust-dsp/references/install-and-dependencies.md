# Install And Dependencies

The skill launcher installs `sletz/faust-mcp` into the user cache, not into the
skill folder.

Default cache:

```text
~/.cache/faust-dsp-skill/
```

Override it with:

```bash
FAUST_DSP_SKILL_CACHE=/custom/cache python3 scripts/faust_runtime.py ensure
```

## Required for default offline analysis

- `git`
- Python 3.10+
- Faust CLI in `PATH` (`faust`)
- `g++`
- Python packages from upstream `requirements.txt`

## Platform Status

Treat this skill as macOS-first. The Codex install flow, Homebrew guidance, and
browser playback smoke test have been exercised on macOS.

Linux is not intentionally excluded, but it is less tested. It should be
possible when `git`, Python 3, `faust`, `g++`, Node.js, and npm are available in
`PATH`; use the distribution's package manager rather than Homebrew unless the
user explicitly has Homebrew on Linux.

Native Windows is not currently a recommended target. The launcher assumes a
Unix-like environment in several places, including `venv/bin/python`, `g++`,
process-group cleanup, executable permission bits, and shell wrappers. Prefer
WSL for Windows users.

## Optional

- DawDreamer for `analyze --runtime daw`
- Node.js and npm for browser UI package installs
- Node.js plus native `node-web-audio-api` setup for the Node realtime backend
- Browser audio permission for the browser runtime
- MIDI device permissions for MIDI workflows

## Launcher-managed local fixes

The launcher creates `~/.cache/faust-dsp-skill/tmp` and passes it as `TMPDIR`
to upstream servers. Do not ask the user to create this directory manually.

On macOS/Homebrew systems, Faust headers may live under
`/opt/homebrew/include/faust/...` or `/usr/local/include/faust/...` while the
upstream offline C++ compile command calls plain `g++`. When those headers are
detected, the launcher creates a cache-local `bin/g++` wrapper that adds the
needed include path. This wrapper lives only in the skill cache and is prepended
to the runtime `PATH`; it does not replace or modify the system compiler.

## Troubleshooting

Run:

```bash
python3 scripts/faust_runtime.py doctor
```

If `faust` is missing, install Faust with the platform's package manager or from
the Faust project. If `g++` is missing on macOS, install Xcode command line
tools. If the browser runtime starts but audio is silent, check browser unlock,
OS audio output, and DSP gain/envelope controls.

## System Package Installation Policy

Do not silently install system package-manager dependencies during a first-run
check. If `faust` is missing, explain that it is a system-level Faust CLI
dependency required for compilation and offline rendering.

If the user explicitly asks you to install it, you may request approval to run
the platform package-manager command. On macOS with Homebrew available, the
typical command is:

```bash
brew install faust
```

Tell the user this may take several minutes, especially if Homebrew updates
itself first. After installation, verify with `faust --version` and rerun
`python3 scripts/faust_runtime.py doctor`.
