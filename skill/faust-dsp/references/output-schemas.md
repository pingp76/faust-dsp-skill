# Output Schemas

## Offline analysis

Typical fields:

- `status`: `success` when compile and render completed.
- `max_amplitude`: maximum absolute amplitude of the mono mix.
- `rms`: root-mean-square level of the mono mix.
- `is_silent`: true when output is below the upstream silence threshold.
- `waveform_ascii`: compact waveform preview.
- `num_outputs`: number of output channels.
- `channels`: per-channel peak, RMS, silence flag, and waveform preview.

Use these fields to decide whether to revise the DSP. Silence is often caused by
closed gates, zero gain, missing test input, or a compile path that produced no
output channels.

## Realtime metrics

Realtime `get_audio_metrics` returns output/input meter data, optional scope and
spectrum arrays, and probe values. Treat `hasNaN`, clipping, and unexpectedly
silent RMS/peak values as actionable DSP issues.

Parameter paths must be discovered from `get_params` or `get_dsp_json`; do not
guess paths from slider labels alone.
