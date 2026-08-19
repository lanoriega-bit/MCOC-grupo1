# Project

Laboratorio estructural digital 3D de un edificio real.

# Units

SI: m, N, Pa.

# Structural Model

- Global model: linear elastic 3D.
- Slabs are not FE modeled.
- Floor gravity load = slab self weight + uniform finishes.
- Slab loads are transferred through tributary areas.
- RC capacity analysis is separate from the global model.

# Architecture

- OpenSees owns structural analysis.
- Unity owns visualization/preprocessing/interaction.
- JSON is the contract between both.
- Mobile does not run OpenSees in the base project.

# Verification Rules

- Check equilibrium.
- Check units.
- Check local axes.
- Check superposition.
- Never modify reference benchmark results without justification.

# P1L0 Scope

- Keep the 2D benchmark minimal and explainable.
- Do not add Unity, AR, nonlinear sections, or building-level complexity to P1L0.
- Any OpenSeesPy result must be compared against an independent hand calculation when feasible.
