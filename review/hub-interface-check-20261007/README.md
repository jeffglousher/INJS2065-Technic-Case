# Servo-facing hub interface comparison

The user clarified that the cross/tab geometry in the servo-facing side was the concern, not the opposite Technic axle socket. Native OCCT sections compare body 54 with body 216 from the current garden-auger-direct-drive.nbcad, both at equal mouth scale. The source hashes are retained in comparison-source.json. The garden auger repository was read only; its unrelated dirty work was left intact.

Current hub: nominal round recess diameter 5.60 mm with four inward tabs, each 1.20 mm wide and extending inward to a 2.10 mm radius, giving 4.20 mm opposing-tab opening. The tab tips are world Z26.10; the floor is Z30.20 (4.10 mm). The surrounding flange face is Z26.30 (3.90 mm to the floor). There is no center retaining-screw passage through the solid separating web.

Current auger reference: a smooth trial diameter 5.70 mm pilot, 3.70 mm depth, 0.15 mm entry chamfer, 3.40 mm center-screw passage and 6.40 mm screw-head access. It mounts directly onto the servo shaft, replacing a separate metal horn. Its M3 screw envelope and depth came from a different servo, INJS035-360, and are not automatically valid for INJS2065. The pilot diameter remains a physical fit-coupon candidate in that project.

INJORA lists the INJS2065 spline as diameter 5.9 mm / 25T: https://www.injora.com/products/injora-injs2065-7kg-high-voltage-waterproof-2065-digital-servo-with-mount-for-1-18-trx4m?variant=45753856819487 . Shared nominal spline diameter/tooth count does not establish identical exposed shaft length, center screw size or thread depth. Referencing the manufacturer's specification; no source text copied.

Decision pending: whether to match the auger's direct-to-shaft interface or retain a separate metal horn. The four tabs do not match the current auger. A direct-to-shaft revision also requires a workable screw-retention/access design: the existing opposite axle opening has only a 4.85 mm span and cannot pass the auger reference's round 5.5 mm screw head. No hub geometry was changed during this comparison. Do not treat the existing five-part plate's successful slice as hardware mating validation; resolve this hub interface before printing it as the final assembly.

[Equal-scale native mouth comparison](servo-mouth-comparison.png). Native source data and the local capture/render scripts are included; the reference auger model is retained externally at D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-interface-review-20261007/auger.model.json.
