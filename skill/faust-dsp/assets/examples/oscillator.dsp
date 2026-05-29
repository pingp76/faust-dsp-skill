import("stdfaust.lib");

freq = hslider("freq[Hz]", 440, 20, 2000, 1);
gain = hslider("gain", 0.2, 0, 1, 0.01);

process = os.osc(freq) * gain <: _,_;
