---
name: Research before commit
description: >-
  Use before freezing mating geometry, hardware pockets, mechanism class, or fit
  numbers — forces local KB / datasheet research before CAD commit.
---
# Research before commit

Late research is how wrong envelope dims and wrong mechanism classes get baked into history. Gate commits.

## Hard gate
Do not freeze pocket dims, fastener patterns, bearing seats, or snap class until this checklist is green (or explicitly waived with reason).

## Order of retrieval
1. **Local MCP knowledge** — `resources/read` on `nbcad://knowledge/index.md` then topic pages; prefer future `cad_help` search when available.
2. **Product docs / recipes** — flagship coupons (`turbine-fit-coupons`, fit recipes), agentic primers (`PARAMETRIC_PRIMITIVES`).
3. **Primary datasheets / catalogs** for purchased parts (servo, bearing, fastener) — record nominal + tolerance source.
4. **Web search** only as escape hatch; cite URL + date; never paste closed standards tables into the model notes as if they were yours.

## Capture before modeling
Write a short **design brief** (chat or doc):
- Function + constraints (envelope, print process, materials)
- Purchased vs designed parts
- Mechanism class decision
- VERIFY table for critical dims (CAD default vs measured/datasheet)
- Fit roles (clearance / transition / interference) with radial vs diametral called out
- Open questions / waivers

## Commit rule
- Changing a VERIFY row by > process tolerance ⇒ regenerate affected features; do not “nudge” unrelated faces.
- If research flips mechanism class (e.g. tabs vs clips), scrap the wrong embodiment — do not patch.

## Anti-patterns
- Modeling from memory of a similar part
- Trusting a single blog dimension for hardware
- Applying one global slicer hole compensation instead of role-based CAD fits
