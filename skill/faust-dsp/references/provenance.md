# Provenance

This skill is a wrapper and workflow layer for local Faust DSP work. It was
inspired by and designed to interoperate with:

https://github.com/sletz/faust-mcp

The default launcher clones that repository at runtime into the user's cache.
This repository does not vendor upstream source code by default, because the
upstream repository did not include an explicit license when this skill was
created.

Keep README wording clear:

- Say this project is "derived from the runtime design of" or "wraps"
  `sletz/faust-mcp`.
- Do not imply that this repository owns or relicenses the upstream project.
- If vendoring upstream code later, first confirm upstream license terms.
