# Tool Surface

The upstream runtime is `sletz/faust-mcp`.

## Offline tool

`compile_and_analyze(faust_code, input_source?, input_freq?, input_file?)`

Returns JSON with status, peak amplitude, RMS, silence status, ASCII waveform,
number of outputs, and per-channel metrics. The DawDreamer variant also returns
feature and render metadata.

## Realtime tools

Common browser and Node runtime tools:

- `check_syntax(faust_code, name?)`
- `compile_and_start(faust_code, name?, latency_hint?, input_source?, input_freq?, input_file?, hide_meters?)`
- `compile(faust_code, name?, latency_hint?, input_source?, input_freq?, input_file?, hide_meters?)`
- `start()`
- `get_status()`
- `get_params()`
- `get_dsp_json()`
- `get_param(path)`
- `get_param_values()`
- `set_param(path, value)`
- `set_param_values(values)`
- `get_audio_metrics(include_scope?, include_spectrum?, per_channel?, fft_size?, smoothing?, min_db?, max_db?, edge_threshold?, log_bins?)`
- `save_wasm_module()`
- `load_wasm_module(...)`
- `get_midi_inputs()`
- `get_midi_status()`
- `select_midi_input(index?, name?)`
- `stop()`
- `destroy()`

Browser-only also has `unlock_audio(latency_hint?)`.

Use `scripts/faust_runtime.py call --tool <name>` to call an SSE runtime that was
started by `scripts/faust_runtime.py start`.
