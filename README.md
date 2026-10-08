# INJS2065 Technic Case

Current editable CAD: [design/current.nbcad](design/current.nbcad). Canonical native feature history: [design/current.model.json](design/current.model.json).

The assembly contains the two clamshell halves, output hub, two honeycomb clips, and servo/bearing reference bodies. Each clip has two rows of four complete hex pockets, full walls, and four centered, symmetric rounded detent nubs. Local pocket-side reliefs thin the four nub-bearing corner spans to approximately 0.90 mm, with 1.00 mm backing. The housing has hidden rounded receiving pockets with minor nominal installed lip contact.

[Current review](CURRENT_REVIEW.md) describes dimensions, verification and remaining physical checks. [Working instructions](AGENTIC.md) describe the source and replay workflow.

The current history has 374 features after the corner-flex revision and removal of accidental hub tabs and redundant horn operations. The compact hub has a smooth diameter 5.70 mm, depth 3.70 mm servo socket with a 0.15 mm lead-in, retained by friction only. [Latest spaced five-part PETG project](review/print-layout-20261008/assembly-petg-sequential-no-brim.3mf) uses X2D / 0.4 mm, hub-only six-wall solid 0.08 mm settings, retained hub supports, and no hub brim. Native named views show assembled, exploded and print-by-object arrangements. [Latest review](review/print-layout-20261008/README.md) includes a separate finer clip candidate and the unresolved reported hex-strand failure. Edge selection is pending before a printable underside revision; friction retention, insertion, detent preload, creep and endurance remain physical checks.

Superseded experiments, captures and uncommitted work were archived at:

`D:/noBS-CAD-Reviews/INJS2065-Technic-Case/history-cleanup-20261004`

That archive includes a verified Git bundle of every pre-cleanup ref and a complete pre-cleanup working-tree tar. Older local branches were fully contained in the current tip before removal. No remote branches were deleted.
