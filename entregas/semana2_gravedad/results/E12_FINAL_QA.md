# E12 Final QA

## E2 Gravity QA
- Floor -1: slabs=16, area=194.410 m2, load=894.286 kN, status=PASS
- Floor 1: slabs=8, area=117.770 m2, load=541.742 kN, status=PASS
- Floor 2: slabs=7, area=89.368 m2, load=411.091 kN, status=PASS
- Floor 3: slabs=10, area=136.925 m2, load=629.855 kN, status=PASS
- Floor 4: slabs=19, area=118.722 m2, load=546.124 kN, status=PASS

## E2 OpenSees
- nodes=48, elements=84, applied=3023.097005 kN, sum_Rz=3023.097005 kN, residual=0.000000000 kN, status=PASS

## E1 Preservation (c0c0cdb validated)
- applied_gravity_kN=21189.360000
- sum_support_reaction_z_kN=21189.360000
- residual_fz_kN=0.000002000
- status=PASS
- verified_max_displacement_m=0.018001
- blockers=1 (incl. L101=GEOMETRIC_BLOCKER)
- B0022 -> SOL_1_logical_0027_seg02 = RECONCILED_SCOPING_RESPONSE

## E2 Response
- response_status_counts={"VERIFIED_CONNECTED_RESPONSE": 129, "RECONCILED_SCOPING_RESPONSE": 170, "FLOATING_LOAD_PATH_BLOCKER": 110, "UNMATCHED_STRUCTURAL_RESPONSE": 0, "PHYSICAL_MEMBER": 218, "SEGMENTATION_STUB_ARTIFACT": 103}
- verified_max_displacement_m=0.001428949547637551
- verified_supports=8/314 symbols mapped to restrained FE nodes (MATCHED_FOUNDATION_LINE)

## E12 Integrated QA
- E1_applied_gravity_kN=21189.36
- E2_applied_gravity_kN=3023.097005
- TOTAL_applied_gravity_kN=24212.457005
- E1_support_reactions_kN=21189.36
- E2_support_reactions_kN=3023.097005
- TOTAL_support_reactions_kN=24212.457005
- global_residual_kN=0.000002000
- relative_error_pct=8.260220e-09
- global_status=PASS
- E1_verified_max_displacement_m=0.018001
- E2_verified_max_displacement_m=0.001428949547637551
- combined_verified_max_displacement_m=0.018001
- E1_blockers=1
- E2_blockers=17
- interface_blockers=none invented (no fake equalDOF/merge/rigid link)
- integrated_fe_model=False
- interface_status=UNRESOLVED_INTERFACE
