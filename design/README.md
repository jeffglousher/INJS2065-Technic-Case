# INJS2065 v16.23 — all Technic steps, enclosed pin paths, compact envelope

The case remains 24 x 24 x 34 mm. The lower side holes remain removed. The four top sockets and both side through paths now share a 6.2 mm-diameter entrance recess 0.8 mm deep, a 6.2 mm-long gripping land at the preceding 5.05 mm PETG trial bore diameter, and 6.2 mm-diameter pin-tip relief from 7.0 to 8.2 mm insertion. Top sockets are blind; side paths remain through from either face. Printed pin fit and retention require physical testing.

The side-hole opening into the orange hub was real. The previous full-length 12.3 mm bearing clearance broke into the side bores and their internal relief. It is replaced with shaped clearances: 11.7 mm around the broad horn base, a taper to an 8.8 mm throat, then a taper and 10.9 mm collar clearance below the bearing seat. This restores nominal 1.075 mm shell walls at the closest side-bore section. All retention-relief rings should be complete rather than breaking into the central cavity.

The hub retains its 11.2 mm broad base, tapers earlier to an 8.3 mm local neck, then uses a 10.4 mm collar beneath the unchanged bearing journal. This trades some hub wall thickness for enclosed side pin paths without enlarging the case. The minimum horn-socket wall in the local neck is 1.125 mm, compared with 2.575 mm at the base. The cross socket remains 8 mm deep, flush at Z42; hub overall length remains 15.7 mm. Strength and fatigue at this thinner neck are not established by CAD checks.

## Bearing assembly

The bearing remains Z34.35–37.85. It now enters from the front through a 12.3 mm pocket and seats on a shoulder at Z34.35 with inner diameter 10.9 mm. Install the hub through the shell from below, then insert the bearing from the front over the journal before completing servo/clam assembly. The former upper shoulder is removed to permit insertion. There is no separate front retaining cap; outward axial retention relies on the journal fit and assembled hub. This remains a physical fit/load validation item, not a proven axial load rating.

## Acceptance evidence

`validation_results.json` records built geometry, full circular step edges, top floors, through-pin clearance, the separating-wall section sweep, and front bearing insertion. Regression checks show v16.20 lacked a wall at the bore centerline and v16.22 blocked bearing insertion. The v16.22 live views were inspected before the bearing-access change. Final v16.23 live visual review is BLOCKED by an unrelated Windows Security prompt for tests.test; no unobstructed final screenshot has been accepted. Exposed internals and cavity views are not true solid sections; section evidence here is numerical mesh intersection.

No larger envelope, relocated Technic grid, or new snap mechanism is introduced. Nominal geometry checks do not establish PETG print quality, pin retention, hub strength, or bearing axial retention. No new print release is issued in this revision.
