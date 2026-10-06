# Editor runtime checkpoint — 2026-10-05

Unity 6000.6.0f1 opened from Hub after the licensing connection issue.
Main was exercised in the actual Editor, not only through cached compiler references.

The first run hid CURRENT results because the source-settings gate still read
the former weekly configuration path. Updated that read to
`config/analysis_settings.json`, and repository detection to
`config/project_config.json`. Hash/version validation remains mandatory.
No result, geometry, load, material, capacity or AR dataset was regenerated.

After explicit Assets Refresh, Assembly-CSharp rebuilt at 16:25:53 local time.
The fresh `Temp/p1l4-ui-smoke.result.txt` at 16:27:26 reported:

```
[UI QA] Iniciando prueba automatica en Play.
[P1L5 DEMO QA] PASS: selección; casos; deformada; My/Mz/N/Vy/Vz; sliders y R instantánea.
[UI QA] PLAY_SMOKE_COMPLETE: arranque y ciclo Play/Edit finalizados.
```

`tools/verify_migration.py`: PASS, 120/120 protected files byte-identical.
The known JsonModels nested-list serialization warning remains visible;
it was not suppressed. No scene changes were made.

This clears the desktop licensing/startup and CURRENT-demo block, not the entire
architecture migration. AR device tracking and the AR Play suites remain to be
validated separately. Unity relocation, master commands and clean-clone QA are
still pending; Main remains in its original project location.
