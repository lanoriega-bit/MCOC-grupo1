# E2 Force Extraction Audit

- OpenSees response queried with `localForce`.
- Ordering used: `[N, Vy, Vz, T, My, Mz]` at i then `[N, Vy, Vz, T, My, Mz]` at j.
- Units exported: N/V in kN, T/M in kN*m, u in m, rotations in rad.
- Elements audited: 84.
- Largest exported torsion/moment magnitude: 4.712555 kN*m at `E2_STK_0008_11.88_15.84`.
- Element equilibrium: PASS for solved verified submodel via global support reaction check.
- Outliers: none promoted from scoping/blocker/stub universe.
- Status: PASS for the verified solved E2 submodel; unresolved slab/interface regions are documented blockers and excluded.
