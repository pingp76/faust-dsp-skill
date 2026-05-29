import("stdfaust.lib");

probe_rms(id, x) = x <: attach(x, an.rms_envelope_rect(0.1)
  : hbargraph("Probe RMS%2id[probe:%id]", 0, 1));

freq = hslider("freq[Hz]", 440, 20, 2000, 1);
gain = hslider("gain", 0.3, 0, 1, 0.01);

process = os.sawtooth(freq) * gain : probe_rms(0) <: _,_;
