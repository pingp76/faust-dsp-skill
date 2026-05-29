# Runtime Selection

Use the least stateful runtime that satisfies the task.

## Offline C++ runtime

Use `analyze --runtime cpp` for quick compile-and-render checks. It wraps
`faust_server.py` from `sletz/faust-mcp` and calls `compile_and_analyze` over
stdio. It requires the Faust CLI and `g++`.

Choose this when the user asks whether a DSP compiles, clips, is silent, or
produces plausible output.

## DawDreamer runtime

Use `analyze --runtime daw` when the user needs offline rendering with richer
features or input sources (`sine`, `noise`, `file`). It requires DawDreamer,
which is not installed by the default setup because it can be heavier and more
platform-sensitive.

## Browser runtime

Use `start --kind browser` for WebAudio, Faust WASM, UI inspection, browser MIDI,
scope, spectrum, and probe work. This runtime starts a local static server and
an MCP SSE endpoint. Browser audio may require the user to click an unlock
control.

## Node runtime

Use `start --kind node` only when the user specifically needs the Node backend,
native audio output, Node MIDI, or parity with `faust_node_server.py`. It
requires Node.js, `node-web-audio-api`, and native builds.

## Cleanup

For background runtimes, always use `scripts/faust_runtime.py stop`. The launcher
stores the owned process group in the cache state file and stops only that group.
