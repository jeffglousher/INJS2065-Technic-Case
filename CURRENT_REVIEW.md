# Current honeycomb detent assembly - 7 October 2026

Editable native project: [design/current.nbcad](design/current.nbcad). Canonical history: [design/current.model.json](design/current.model.json). Their parsed native payloads match. All 403 features replay with zero errors and seven bodies.

The authorized revision adds a wider tangent corner relief with 0.25 mm side-wall blends, a broader R0.80 nub crest with tangent R0.40 outer arcs, and a rounded hidden receiver cap. All eight blind hex pockets per clip and continuous walls remain. Nub protrusion remains 0.20 mm, centered on the confirmed spans. Minimum in-plane corner wall remains 0.8976 mm; broad-face backing remains 1.00 mm. Exterior housing hex-mouth signatures are unchanged; only the hidden seats change.

The nominal local inward holding-clearance target is now 0.02257 mm. The crest has 0.07697 mm radial clearance; contact remains on the diagonal flanks. [Full geometry, material, strain and slicing review](review/revision-20261007/REVIEW.md) records the limits of these geometric and mechanical estimates.

[Corner closeups](review/revision-20261007/detent-corners.png), [clip/housing ISO](review/revision-20261007/clip-housing-iso.png), [exploded assembly](review/revision-20261007/exploded.png), [native OCCT sections and cutaway](review/revision-20261007/sections.png), [strain comparison](review/revision-20261007/strain-comparison.png).

The updated part was remeshed and screened with Bambu PETG Basic V3 stiffness. Fine axial reactions are 4.15-5.04 N per nub at the new nominal movement; narrow-patch local strain peaks reduce to 4.29-4.38%. Other footprints do not uniformly improve. Local strain remains unconverged, and inclined seat loads reveal additional support sensitivity. Peak dynamic insertion, actual printed preload, creep and fatigue remain unqualified.

All three parts generated native Bambu PETG Basic / X2D 0.4 mm toolpaths at 0.12 mm main layers. Fine mesh audits and exact assembly checks pass; only the expected detent contact groups remain. No printer job was started. This is a fit-test candidate, not a mechanically qualified production release.

[Current validation reference](review/tangent-corner-flex.json) preserves the three unchanged servo/bearing/hub meshes and records the authorized clip and hidden-seat changes. Run `node tools/verify-current.mjs`. Earlier [corner-flex evidence](review/local-corner-flex.json) and [geometry-preserving cleanup](review/history-cleanup.json) remain unchanged historical references.
