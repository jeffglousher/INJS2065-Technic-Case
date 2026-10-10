# INJS2065 Technic Case

Current editable CAD: [design/current.nbcad](design/current.nbcad). Canonical native feature history: [design/current.model.json](design/current.model.json).

[Current print go/no-go report](review/print-decision-20261009/README.md). The [updated complete PETG project and hub orientation comparison](review/hub-orientation-20261010/README.md) turn the servo rim down and disable hub supports, saving approximately eight minutes and 0.38 g without changing CAD. Jeff makes the final print decision; no printer job has been sent.

**Current: registered fit experiment prepared; functional qualification remains blocked.** [Contact-model correction and complete-shell PETG test](review/contact-fix-20261009/README.md) replace the cropped receiver coupon and the unsupported-floor constraints identified by the [independent adversarial review](review/adversarial-retention-20261009/README.md). The [unchanged candidate geometry](review/retention-fit-20261009/README.md) has 0.10 mm inner clearance per flat and 0.26 mm nubs. Native checks and slicing pass. Accepted holding/insertion mechanics and a successful controlled physical test are still required before selecting retention geometry or claiming readiness for functional use. Earlier force/strain and cropped-coupon acceptance recommendations remain withdrawn.

The assembly contains the two clamshell halves, output hub, two honeycomb clips, and servo/bearing reference bodies. Each clip has two rows of four complete hex pockets, full walls, and four centered, symmetric rounded detent nubs. Local pocket-side reliefs thin the four nub-bearing corner spans to approximately 0.90 mm, with flat pocket floors and 1.45 mm backing. The housing has hidden rounded receiving pockets with minor nominal installed lip contact.

[Current review](CURRENT_REVIEW.md) describes dimensions, verification and remaining physical checks. [Working instructions](AGENTIC.md) describe the source and replay workflow.

[Previous clip-floor correction and CAD pictures](review/flat-clip-base-20261008/README.md) remove the relief depressions from the base while retaining the relieved walls and nubs. Native checks and slicing pass; the former strain/force screen does not qualify the restored backing.

The current history has 390 features, including shared root-started 55 degree bevels on all 16 hex posts. [Full fit-candidate PETG project](review/retention-fit-20261009/assembly-fit-candidate.3mf) uses X2D / 0.4 mm, hub-only six-wall solid 0.08 mm settings, retained hub supports, and no hub brim. Native named views show assembled, exploded and print-by-object arrangements. [CAD and toolpath checks](review/root-ramp-20261008/README.md) pass: the first lower-post extrusion reaches 0.198 mm outward instead of 1.490 mm, while nominal detent contacts and the five other solids remain unchanged. The compact hub retains its friction-only diameter 5.70 mm, depth 3.70 mm servo socket and 0.15 mm lead-in. Functional print readiness remains blocked by the current adversarial findings.

Superseded experiments, captures and uncommitted work were archived at:

`D:/noBS-CAD-Reviews/INJS2065-Technic-Case/history-cleanup-20261004`

That archive includes a verified Git bundle of every pre-cleanup ref and a complete pre-cleanup working-tree tar. Older local branches were fully contained in the current tip before removal. No remote branches were deleted.
