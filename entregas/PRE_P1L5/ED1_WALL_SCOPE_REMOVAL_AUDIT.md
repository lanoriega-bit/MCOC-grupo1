# ED1 wall scope removal audit

Baseline: `d323e248434162bfc8cd5a888ad6578cd3600ac9`. User scope decision, NOT a finding that the real building has no walls.

44 walls and 7 exclusively wall support visuals excluded. 13 exclusively wall FE support nodes removed by rebuilding. These are distinct counts.

All columns, column supports and shared/unknown support visuals preserved. Removing real walls changes the structural idealization: no current analysis or adequacy certification.

| Support visual | Class | Wall correspondence | Retained members | Action |
|---|---|---|---|---|
| E1-S1-A-051 | COLUMN_SUPPORT |  | E1-S1-C-004 | PRESERVE |
| E1-S1-A-053 | COLUMN_SUPPORT |  | E1-S1-C-006 | PRESERVE |
| E1-S1-A-052 | COLUMN_SUPPORT |  | E1-S1-C-005 | PRESERVE |
| E1-S1-A-008 | COLUMN_SUPPORT |  | E1-S1-C-002 | PRESERVE |
| E1-S1-A-006 | COLUMN_SUPPORT |  | E1-S1-C-001 | PRESERVE |
| E1-S1-A-009 | COLUMN_SUPPORT |  | E1-S1-C-003 | PRESERVE |
| E1-S1-A-066 | COLUMN_SUPPORT |  | E1-S1-C-009 | PRESERVE |
| E1-S1-A-067 | COLUMN_SUPPORT |  | E1-S1-C-010 | PRESERVE |
| E1-S1-A-073 | COLUMN_SUPPORT |  | E1-S1-C-013 | PRESERVE |
| E1-S1-A-076 | COLUMN_SUPPORT |  | E1-S1-C-016 | PRESERVE |
| E1-S1-A-074 | COLUMN_SUPPORT |  | E1-S1-C-014 | PRESERVE |
| E1-S1-A-075 | COLUMN_SUPPORT |  | E1-S1-C-015 | PRESERVE |
| E1-S1-A-071 | COLUMN_SUPPORT |  | E1-S1-C-011 | PRESERVE |
| E1-S1-A-072 | COLUMN_SUPPORT |  | E1-S1-C-012 | PRESERVE |
| E1-S1-A-064 | COLUMN_SUPPORT |  | E1-S1-C-008 | PRESERVE |
| E1-S1-A-077 | COLUMN_SUPPORT |  | E1-S1-C-017 | PRESERVE |
| E1-S1-A-079 | COLUMN_SUPPORT |  | E1-S1-C-019 | PRESERVE |
| E1-S1-A-078 | COLUMN_SUPPORT |  | E1-S1-C-018 | PRESERVE |
| E1-S1-A-061 | COLUMN_SUPPORT |  | E1-S1-C-007 | PRESERVE |
| E1-S1-A-004 | WALL_ONLY_SUPPORT | E1-S1-M-004 |  | EXCLUDE |
| E1-S1-A-002 | SHARED_SUPPORT | E1-S1-M-002 | E1-S1-C-003 | PRESERVE |
| E1-S1-A-034 | SHARED_SUPPORT | E1-S1-M-031 | E1-S1-C-001 | PRESERVE |
| E1-S1-A-019 | SHARED_SUPPORT | E1-S1-M-016 | E1-S1-C-001 | PRESERVE |
| E1-S1-A-033 | SHARED_SUPPORT | E1-S1-M-030 | E1-S1-C-006, E1-S1-C-003 | PRESERVE |
| E1-S1-A-005 | WALL_ONLY_SUPPORT | E1-S1-M-005 |  | EXCLUDE |
| E1-S1-A-032 | WALL_ONLY_SUPPORT | E1-S1-M-029 |  | EXCLUDE |
| E1-S1-A-023 | WALL_ONLY_SUPPORT | E1-S1-M-020 |  | EXCLUDE |
| E1-S1-A-029 | WALL_ONLY_SUPPORT | E1-S1-M-026 |  | EXCLUDE |
| E1-S1-A-037 | WALL_ONLY_SUPPORT | E1-S1-M-034 |  | EXCLUDE |
| E1-S1-A-042 | SHARED_SUPPORT | E1-S1-M-039 | E1-S1-C-004 | PRESERVE |
| E1-S1-A-055 | WALL_ONLY_SUPPORT | E1-S1-M-049 |  | EXCLUDE |
| E1-S1-A-056 | SHARED_SUPPORT | E1-S1-M-050 | E1-S1-C-005 | PRESERVE |
| E1-S1-A-022 | SHARED_SUPPORT | E1-S1-M-019 | E1-S1-C-006 | PRESERVE |
| E1-S1-A-080 | SHARED_SUPPORT | E1-S1-M-061 | E1-S1-C-002 | PRESERVE |

## Excluded wall IDs

E1-P1-M-001, E1-P1-M-002, E1-P1-M-012, E1-P1-M-015, E1-P1-M-016, E1-P1-M-020, E1-P1-M-021, E1-P1-M-022, E1-P1-M-023, E1-P1-M-024, E1-P1-M-025, E1-P1-M-026, E1-P1-M-031, E1-P1-M-032, E1-P1-M-033, E1-P1-M-034, E1-P1-M-035, E1-P1-M-036, E1-P1-M-037, E1-P2-M-003, E1-P2-M-005, E1-P2-M-009, E1-P2-M-010, E1-P3-M-003, E1-P3-M-005, E1-P3-M-009, E1-P3-M-010, E1-P4-M-003, E1-P4-M-009, E1-P4-M-010, E1-P4-M-012, E1-S1-M-002, E1-S1-M-004, E1-S1-M-005, E1-S1-M-016, E1-S1-M-019, E1-S1-M-020, E1-S1-M-030, E1-S1-M-031, E1-S1-M-034, E1-S1-M-039, E1-S1-M-049, E1-S1-M-050, E1-S1-M-061

## Fresh topology

{
  "baseline_commit": "d323e248434162bfc8cd5a888ad6578cd3600ac9",
  "geometry_solids": 724,
  "ED1_active_walls": 0,
  "walls_excluded_this_revision": 44,
  "support_visuals_excluded_this_revision": 7,
  "FE_wall_only_supports_removed": 13,
  "FE_members": 676,
  "FE_pending": 6,
  "FE_components": 4,
  "FE_constraints": 1205,
  "FE_supports": 33,
  "pending_ids": [
    "E1-S1-V-005",
    "E2-P4-V-004",
    "E2-P4-V-005",
    "E2-P4-V-006",
    "E2-P4-V-007",
    "E2-P4-V-009"
  ],
  "new_pending_ids": [
    "E1-S1-V-005"
  ],
  "current_results": "NONE",
  "analysis_run": false
}

## QA

- ED1_ACTIVE_WALLS_ZERO: PASS
- COLUMN_SUPPORTS_PRESERVED: PASS
- SHARED_SUPPORTS_PRESERVED: PASS
- UNKNOWN_SUPPORTS_PRESERVED: PASS
- COLUMNS_PRESERVED: PASS
- SLABS_PRESERVED: PASS
- STABLE_IDS: PASS
- CROSSWALK: PASS
- NO_EXCLUDED_FE: PASS
- FE_INPUT_HASH: PASS
- NO_ANALYSIS: PASS
- LUIS_REFERENCE: PASS
- FE_COLUMN_SHARED_SUPPORTS_PRESERVED: PASS
