# Independent adversarial review of clip revision 613402c

Reviewed 9 October 2026 against parent 6c36d88 by three separate, read-only agents: `retention_mechanics_review`, `retention_native_review`, and `retention_coupon_review`. The primary agent reproduced the support-footprint calculation and checked the evidence before writing this report. This was an engineering review using separate agents; no branded Bugbot or Security Review service ran.

**Disposition: mechanical qualification is blocked. Withdraw the previous coupon-as-acceptance-test recommendation until its receivers have repeatable registration and support.** The candidate geometry remains unchanged. There was no independent adversarial review before 613402c was committed; the previous CAD/slicer checks were the implementing agent's checks.

## P1: the strain model fixes unsupported pocket-floor material

[strain.py:39](../retention-fit-20261009/strain.py#L39) selects every clip boundary triangle at Y = 10.55 mm as a support. Both support cases fix its Y displacement ([lines 92–97](../retention-fit-20261009/strain.py#L92)), including floor material facing air. The comparison against all housing planar faces at that elevation gives approximately:

- Fixed clip floor: **107.8850 mm²**.
- Actual housing support footprint within that floor: **66.0124 mm²**.
- Unsupported floor nevertheless constrained: **41.8726 mm², or 38.81%**.

These areas use projected native display-mesh triangles, rather than exact OCCT area. The fine FEM mesh has 2,922 constrained floor nodes; 2,354 are outside the housing footprints at a 0.000001 mm containment tolerance. Mesh density makes the node percentage different from the area percentage. [Reproduction script](support-footprint.py), [hashed receipt](support-footprint.json).

As a cross-check against missed housing lands, complete native material sections of both shells at Y = 10.55 mm give a clip-floor intersection of 66.012401 mm², agreeing with the projected post tips within contour sampling. The unsupported-area finding does not depend on considering only selected posts.

The two support cases therefore do not bracket the installed part's actual support. Their reported 7.71–9.02 N per patch and 2.39–6.52% local peak strain at a prescribed 0.020 mm movement cannot be used to predict physical preload or insertion force. They do not prove that the geometry fails either. The next analysis must permit the unsupported backing to move and represent actual compressive contact, including possible separation, with the housing posts and seats.

## P1: the requested insertion flex remains unverified

The load model applies prescribed axial pressure in -Y ([strain.py:73](../retention-fit-20261009/strain.py#L73)); it does not solve the contact-normal forces and changing contact locations during insertion. Its numerical equilibrium checks do not validate that chosen loading mechanism.

The current part is a continuous backed frame. A thin wall measured in the XZ plane does not by itself establish the required inward bending perpendicular to the broad face. The [native approach audit](../retention-fit-20261009/insertion.json) records approximately 0.053735 mm³ overlap per shell at approach offsets 0.75, 1.0 and 1.4 mm, versus 0.000122675 mm³ seated. The previously reported 0.362407 mm single-meridian construction is not the clearance travel for the entire moving nub through that obstruction, and is not a solved dynamic displacement or strain.

Demonstrate the insertion path using actual supports and moving contact, or observe and measure the deformation in a registered physical test, before choosing another nub increase. Preserve the user's full-wall/no-groove requirement unless a proposed change is separately approved.

## P1: the coupon removes the shell registration features

[audit.mjs:20](../retention-fit-20261009/audit.mjs#L20) crops each receiver to X = -8…21 mm, Y = 6…12 mm, Z = 8…27.6 mm. It removes the usable +Y locating features: the lower locator is centered at (24.4, 9.4, 18.6) mm; the upper locator is centered at (-8.4, 9.4, 17.9) mm, with a 0.38 mm tip radius whose maximum X is -8.02 mm. A cut remnant is not the original mating registration. Opposite-side locators are outside the Y crop.

The coupon instructions merely ask the operator to keep the two halves aligned and supported; no fixture or repeatable datum setup is supplied. Hand positioning or squeezing can create or hide an effect on the scale of the 0.020 mm holding target. This coupon can be an exploratory print or locating-fit check, but it cannot presently select a reliable snap/preload design. Use a registered fixture or the full receiving halves with controlled support before judging retention. [Coupon audit receipt](coupon-review-receipt.json).

## P2: repeatability was described as independent qualification

The new `retention-fit.json` was a candidate-generated regression baseline. [verify-current.mjs:17](../../tools/verify-current.mjs#L17) checks candidate bytes and [line 27](../../tools/verify-current.mjs#L27) checks meshes against it. This is useful repeatability evidence, not independent mechanical approval. The previous README's “independent reference” wording was inaccurate; this report and the current status supersede that wording. No historical reference has been rewritten.

The earlier report also said the fillets were rebound. Comparing the two committed native models shows their definitions, edge IDs and keys did not change; their resulting positions moved with the uniformly smaller inner pockets. The build script has a repair path, but the committed result does not demonstrate that it was exercised. No incorrect fillet selection was found.

## P2: the three coupon variants change more than protrusion

The [build formula](../retention-fit-20261009/build.mjs#L9) limits the outer blend radius to at least 0.20 mm. The 0.28 mm variant consequently has a 1.466424 mm meridian span, versus 1.44 mm for the nominal and looser clips, with different lead geometry as well as height. These are related profile experiments, not an isolated height calibration. Record the complete winning profile if testing proceeds. The 3MF names do not physically mark the clips; label them immediately after printing using their plate positions.

## What independently passed

- Fresh native replay: 390 successful features, seven bodies, the four expected interference pairs, and the three untouched meshes preserved.
- Native archive payload matches canonical JSON byte for byte; all eight inner pockets shrink uniformly from 1.95 to 1.85 mm half-width without moving their centers.
- The isolated upper-left native nub/receiver intersection clears after a local rigid 0.020 mm inward shift: overlap falls from 0.0000613375 mm³ to zero. This confirms the seated geometry construction, not an achievable elastic deformation or contact force. [Native test](local-nub-translation.mjs), [results](local-nub-translation.json).
- Coupon/full-project 3MF, G-code and source STL hashes match their receipts. Fresh G-code parsing matches the saved paths; all cropped receiver layer elevations match the full assembly. All twelve nominal clip/coupon sampled overlap areas equal their full-project counterparts. Profile and override settings match the documented X2D / 0.4 mm / PETG Basic configuration.

The paired commanded-width screen still loses all 24 full-project sampled contacts after hypothetical 0.04 mm erosion per mating surface. This remains sensitivity evidence, not a measured tolerance guarantee or proof that printed nubs disappeared.

## Recommended next work

1. Correct the structural support and contact assumptions and recompute holding behavior; keep existing results as a superseded screening experiment.
2. Establish the insertion deformation direction and path before deriving dynamic strain or increasing the nub again.
3. Provide repeatable receiver registration/support for the physical test; measure seating, snap, pull-off behavior, wobble, permanent set and retention after dwell.
4. Select geometry from those results, then check the full assembly. Neither the current coupon nor the successful slice establishes print readiness for functional use.

The stiffness basis is consistent with the manufacturer's [PETG Basic V3 technical data sheet](https://store.bblcdn.com/s1/default/cb94589bf7994fdcbfa833badefae9cd/Bambu_PETG_Basic_Technical_Data_Sheet.pdf): X-Y Young's modulus 2780 MPa. That standard specimen data does not calibrate this part's orthotropy, nonlinear behavior, creep or fatigue. No material failure or safe life is inferred from the unconverged linear peak strains.

Canonical geometry reviewed SHA-256: `19a73dd1a82072cfbd80a95da27a19720c7a09fef52b39dab940d3c3ec4ec340`. This review changes documentation and saves evidence only; it starts no print job.
