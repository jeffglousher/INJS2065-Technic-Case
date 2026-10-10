# INJS2065 Technic Case

Current editable CAD: [design/current.nbcad](design/current.nbcad). Canonical native feature history: [design/current.model.json](design/current.model.json).

[Current incremental fit revision, CAD pictures and PETG projects](review/incremental-fit-20261010/README.md): underside bevels removed on all 16 hex posts, nubs increased from 0.26 to 0.28 mm, and stationary shaft aperture opened from Ø8.15 to Ø8.35 mm. The hub and bearing interfaces remain unchanged. The current [complete PETG project](review/incremental-fit-20261010/assembly-petg-incremental-fit.3mf) keeps support-free hub bridging; an updated [registered complete-shell fit test](review/incremental-fit-20261010/registered-receivers.3mf) uses the same shells and clips. No printer job has been sent by the agent.

**Current: incremental fit-test candidate; functional qualification remains blocked.** Native checks and slicing pass. The selected 0.28 mm nubs improve the paired-toolpath tolerance screen but still need a successful printed snap, seating and retention test. Accepted holding/insertion mechanics are not available. Earlier force/strain and cropped-coupon acceptance recommendations remain withdrawn; the [contact correction](review/contact-fix-20261009/README.md) and [independent adversarial review](review/adversarial-retention-20261009/README.md) remain traceable historical evidence.

The assembly contains the two clamshell halves, output hub, two honeycomb clips, and servo/bearing reference bodies. Each clip has two rows of four complete hex pockets, full walls, and four centered, symmetric rounded detent nubs. Local pocket-side reliefs thin the four nub-bearing corner spans to approximately 0.90 mm, with flat pocket floors and 1.45 mm backing. The housing has hidden rounded receiving pockets with minor nominal installed lip contact.

[Current review](CURRENT_REVIEW.md) describes dimensions, verification and remaining physical checks. [Working instructions](AGENTIC.md) describe the source and replay workflow.

[Previous clip-floor correction and CAD pictures](review/flat-clip-base-20261008/README.md) remove the relief depressions from the base while retaining the relieved walls and nubs. Native checks and slicing pass; the former strain/force screen does not qualify the restored backing.

The current history has **374 valid features** and seven bodies; the 16-feature bevel subtree is removed. Native named views retain assembled, exploded and print-by-object arrangements. The compact hub retains its friction-only Ø5.70 × 3.70 mm servo socket and 0.15 mm lead-in. Current projects use X2D / 0.4 mm / Bambu PETG Basic, hub-only six-wall solid 0.08 mm settings and no supports or brims. Physical fit and mechanical qualification remain to verify.

Superseded experiments, captures and uncommitted work were archived at:

`D:/noBS-CAD-Reviews/INJS2065-Technic-Case/history-cleanup-20261004`

That archive includes a verified Git bundle of every pre-cleanup ref and a complete pre-cleanup working-tree tar. Older local branches were fully contained in the current tip before removal. No remote branches were deleted.
