# INJS2065 Technic Case

Current editable CAD: [design/current.nbcad](design/current.nbcad). Canonical native feature history: [design/current.model.json](design/current.model.json).

**Current: fit-test candidate, coupon first.** The preceding printed clips failed to retain. [The revision and mechanical limits](review/retention-fit-20261009/README.md) reduce inner locating clearance to 0.10 mm per flat, enlarge the rounded nubs to 0.26 mm, and retune the hidden seats. [Print this mating coupon](review/retention-fit-20261009/retention-coupon.3mf) before another full assembly. Native checks and slicing pass; actual inward insertion flex, preload, retention and strain remain unqualified. Earlier readiness statements are superseded.

The assembly contains the two clamshell halves, output hub, two honeycomb clips, and servo/bearing reference bodies. Each clip has two rows of four complete hex pockets, full walls, and four centered, symmetric rounded detent nubs. Local pocket-side reliefs thin the four nub-bearing corner spans to approximately 0.90 mm, with flat pocket floors and 1.45 mm backing. The housing has hidden rounded receiving pockets with minor nominal installed lip contact.

[Current review](CURRENT_REVIEW.md) describes dimensions, verification and remaining physical checks. [Working instructions](AGENTIC.md) describe the source and replay workflow.

[Previous clip-floor correction and CAD pictures](review/flat-clip-base-20261008/README.md) remove the relief depressions from the base while retaining the relieved walls and nubs. Native checks and slicing pass; the former strain/force screen does not qualify the restored backing.

The current history has 390 features, including shared root-started 55 degree bevels on all 16 hex posts. [Full fit-candidate PETG project](review/retention-fit-20261009/assembly-fit-candidate.3mf) uses X2D / 0.4 mm, hub-only six-wall solid 0.08 mm settings, retained hub supports, and no hub brim. Native named views show assembled, exploded and print-by-object arrangements. [CAD and toolpath checks](review/root-ramp-20261008/README.md) pass: the first lower-post extrusion reaches 0.198 mm outward instead of 1.490 mm, while nominal detent contacts and the five other solids remain unchanged. The compact hub retains its friction-only diameter 5.70 mm, depth 3.70 mm servo socket and 0.15 mm lead-in. Test the coupon first; strength, friction retention, preload, insertion and endurance remain unqualified.

Superseded experiments, captures and uncommitted work were archived at:

`D:/noBS-CAD-Reviews/INJS2065-Technic-Case/history-cleanup-20261004`

That archive includes a verified Git bundle of every pre-cleanup ref and a complete pre-cleanup working-tree tar. Older local branches were fully contained in the current tip before removal. No remote branches were deleted.
