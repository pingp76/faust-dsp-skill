# Faust DSP Skill

An agent skill for creating, analyzing, debugging, and running
[Faust](https://faust.grame.fr/) DSP programs with local runtimes.

This project is derived from the runtime design and tool surface of
[sletz/faust-mcp](https://github.com/sletz/faust-mcp). Instead of requiring users
to install an MCP server manually, the skill provides a launcher that installs
and starts the local runtime on demand.

## What this is

- A portable skill folder at `skill/faust-dsp/`.
- A runtime manager at `skill/faust-dsp/scripts/faust_runtime.py`.
- Reference docs that teach agents when to use offline, browser, DawDreamer, or
  Node runtimes.
- Example Faust DSP programs for smoke tests and prompts.

The skill does not vendor `sletz/faust-mcp` source code by default. On first use,
the launcher clones it into `~/.cache/faust-dsp-skill/faust-mcp`.

## User experience

After installing the skill, a user can ask an agent:

```text
Use $faust-dsp to analyze this Faust DSP and fix any silence or clipping.
```

The agent should automatically:

1. Check local dependencies.
2. Clone `sletz/faust-mcp` if needed.
3. Install Python dependencies into a cache-local virtual environment.
4. Install browser UI npm dependencies when browser audio/UI is requested.
5. Run one-shot offline analysis, or start a local browser/Node runtime only
   when realtime audio is needed.
6. Stop any skill-owned background runtime before finishing.

## Install

Copy or symlink the skill folder into an agent's skill directory.

For Codex:

```bash
mkdir -p ~/.codex/skills
cp -R skill/faust-dsp ~/.codex/skills/
```

For other skill-compatible agents, copy `skill/faust-dsp` to that agent's skill
search path.

## Quick start

From the skill folder:

```bash
python3 scripts/faust_runtime.py doctor
python3 scripts/faust_runtime.py ensure
python3 scripts/faust_runtime.py ensure --with-browser-ui
python3 scripts/faust_runtime.py analyze --dsp assets/examples/oscillator.dsp
```

Start a browser runtime:

```bash
python3 scripts/faust_runtime.py start --kind browser
python3 scripts/faust_runtime.py status
python3 scripts/faust_runtime.py stop
```

The browser runtime may require a user gesture to unlock audio.

## Dependencies

Default offline analysis needs:

- `git`
- Python 3.10+
- Faust CLI (`faust`)
- `g++`

Optional runtimes may need:

- DawDreamer
- Node.js
- browser audio permission
- MIDI device permission

## Attribution

This skill was created as a skill-based wrapper around the ideas and local
runtime workflow in [sletz/faust-mcp](https://github.com/sletz/faust-mcp).
`sletz/faust-mcp` provides the upstream MCP server implementations and clients
that this skill installs and calls at runtime.

At the time this repository was created, the upstream repository did not include
an explicit license file. For that reason, this repository keeps the wrapper code
separate and downloads upstream code only into the user's local cache.

## License

The wrapper code and documentation in this repository are released under the MIT
License. This license does not apply to code downloaded from upstream
`sletz/faust-mcp`.
