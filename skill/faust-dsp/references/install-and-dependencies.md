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

## Optional

- DawDreamer for `analyze --runtime daw`
- Node.js and npm for browser UI package installs
- Node.js plus native `node-web-audio-api` setup for the Node realtime backend
- Browser audio permission for the browser runtime
- MIDI device permissions for MIDI workflows

## Troubleshooting

Run:

```bash
python3 scripts/faust_runtime.py doctor
```

If `faust` is missing, install Faust with the platform's package manager or from
the Faust project. If `g++` is missing on macOS, install Xcode command line
tools. If the browser runtime starts but audio is silent, check browser unlock,
OS audio output, and DSP gain/envelope controls.
