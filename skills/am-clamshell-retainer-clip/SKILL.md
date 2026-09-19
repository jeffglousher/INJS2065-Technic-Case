---
name: AM clamshell retainer clip
description: >-
  Use when designing or revising an FDM/AM retainer that holds two clamshell
  halves together — slide-fit first, then optional detents; never invent snap
  geometry without this order.
---
# AM clamshell retainer (slide first, detent second)

## Print
- Print the retainer **on its side** so layer lines run with the clamp load (stronger against the halves separating).
- Prefer a simple **rectangle with a center cutout** (channel / frame), not a decorative C or ornamental hooks.

## Function split (do not merge)
1. **Clamp / strength** — faces that keep the two halves from separating. Sized for a clean removable slide-in.
2. **Retention** — small **detents on the inserted faces** only, added *after* the sliding fit is confirmed. Detents keep the clip from falling out; they are not the load path.

The surface that carries strength is not the surface that provides snap retention.

## Order of work
1. Model a perfect removable sliding shape against the real pockets (dims, clearances, tolerances, mating surfaces).
2. Validate: slide in / slide out by hand intent, no interference on the clamp faces, printable without supports in the side orientation.
3. Only then add tiny detent details on the insert faces.
4. Do not invent complex barbs, I-beams, or load-bearing snaps while iterating the slide fit.

## Engineering checklist
- Nominal + clearance / press roles called out (radial vs diametral where relevant)
- Mating surface finish / print orientation noted
- Lifetime: abrasion and plastic set on detents, not on the clamp faces
- Kid-removable when required: soft detent force; clamp still structural

## CAD / knowledge
- Prefer local CAD knowledge / DFM notes when present (`nbcad://knowledge/...`).
- Gaps or wrong docs → flag for contribution to the product knowledge base; do not paper over with invented geometry.
