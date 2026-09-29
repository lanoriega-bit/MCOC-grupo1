# P1L6 mobile integration

## Scope

This integration consumes the frozen structural geometry and precomputed
CURRENT results. The Android device does not run OpenSees and this milestone
does not modify structural IDs, loads, supports, capacities or results.

## Coordinate contract

The tested mathematical mapping is:

```text
model/OpenSees [x, y, z] -> Unity [x, z, -y]
p_anchor_local = R_calibration * (scale * (p_unity - p_model_origin)) + offset
p_world = ARAnchor.localToWorld * p_anchor_local
```

Units are metres. The ARAnchor world pose comes exclusively from Luis's image
tracking implementation. It is applied once, by parenting the structural
object under the anchor; it is not repeated inside the local transform.

The primitive's physical length is local `+Y`. Its rotation is therefore
computed with `FromToRotation(Vector3.up, orientation_unity)`. The direction
stored as `orientation_unity` must not pass through the model-to-Unity axis map
a second time.

## Provisional marker calibration

`ImagenPrueba` does not yet represent a permanently selected location in the
real building. For the first phone test only, the final scene uses this explicit
and reversible convention:

- image centre = base centre of `E2-P1-C-002`;
- model origin in Unity metres = `[7.502, 3.960, -0.001]`;
- image/local `+X` = building/model `+X` after the canonical axis map;
- image/local `+Y` = structural vertical;
- initial calibration rotation = identity;
- visualization scale = `0.25` (1:4);
- calibration offset = zero.

The image must therefore be held or mounted vertically and upright for the
column to appear vertical in the first demonstration. Moving the marker to a
real building location later requires changing only the calibration origin,
rotation and optional offset. It does not change Jose's axis transformation or
the structural dataset.

## Tracking policy

```text
Tracking -> render element and CURRENT result.
Limited  -> hide element; panel reports TRACKING LIMITED.
None     -> hide element; panel reports TRACKING UNAVAILABLE.
```

Luis's tracker creates at most one anchor. Repeated updates of the same image
reuse it. The test cube is disabled in the final scene; only the structural
renderer creates visible geometry.

## Initial elements

- `E2-P1-C-002`: initial phone element; its base is the provisional marker
  origin. The panel exposes elementTag, solidTag, OpenSees tag 10039, CURRENT,
  P, M, V, displacement and D/C.
- `E2-P1-V-032`: second orientation check for a horizontal member.

## Scene separation

- `Main.unity`: unchanged desktop viewer.
- `P1L6_AR_Prototype.unity`: retained desktop/fake-anchor QA scene.
- `Scenes/Luis_AR_Test.unity`: retained original tracking test.
- `Scenes/P1L6_AR_Final.unity`: Android integration scene and the only enabled
  scene in mobile Build Settings.

## Physical test still required

Repository and Editor QA cannot prove tracking performance on a real phone.
The final status remains `PHYSICAL_DEVICE_TEST_PENDING` until the APK is
installed on an ARCore-compatible Android device and the complete flow is
observed with camera permission granted.
