# INJS2065 Technic Clamshell — Session handover (2026-09-19)

**Branch purpose:** park Cad Bot session state after v16.8 print attempt.  
**Owner context:** Jeff Glousher · Cad Bot · Thunder machine · noBS-CAD MCP.

## Status (read this first)

| Item | State |
|------|--------|
| Latest design tag | **v16.8** |
| Clip print | **FAILED** (Jeff 2026-09-19) — open-C + soft detent did not work in hand/print |
| Main body | **Structural issues reported** — Jeff flagged body problems as *more important* than clip; **details not yet diagnosed in CAD** (next session must inspect live model + print) |
| Audit v16.8 | Digital audit **PASS** (IFC, open C, wall-to-cavity 3.00) — **digital PASS ≠ print success** |
| 3MF export | Done; staged toward Orca on Thunder; print **not** started by bot |
| Jeff design steer | Do **not** invent snap/clip geometry without Jeff; he offered design help after repeated bad clips |

## Project goal

3D-printable **Technic clamshell case** for Injora **INJS2065** micro servo:

- ±12 mm Technic brick envelope
- Shaft-near flange trap
- Alignment nubs (short dome, not long pins)
- MR128 bearing + output hub
- Kids’ **removable** AM retainer holding A/B halves

## Locked design decisions (still valid unless Jeff overrides)

1. **Open C / U-channel retainer silhouette** (spine + top leg + bottom leg, open toward insert) — *not* a closed hollow rectangle (cannot slide on).
2. **Strength ≠ retention:** clamp faces hold halves; detents only stop the clip falling out.
3. **Order:** sliding fit first, then optional small detents.
4. **Print clips on side** (profile in YZ, build along X) so layers carry clamp load.
5. Review images = **live noBS-CAD window captures**, not PyVista/mesh PNGs or drawing sheets.
6. Latch reviews need **behind / inner / section / cutaway**; prefer solid/opaque.
7. Prefer MCP **one-step** for fiddly geometry; script replay in ~100-line chunks once proven — don’t mix on same fragile feature.

## Clip evolution (why we are here)

Many rejected iterations (v12–v16.5): thin seats, U-clip artifacts, proud clips, I-beams, fat wedges, “fancy C” snaps, closed frames, unprintable barbs (e.g. v16.1 barb overlap ~1.78 mm³, 0.4 mm hook).

Jeff locked open-C + slide-then-detent. Cad Bot still over-iterated snaps; feedback filed.

| Ver | Idea | Outcome |
|-----|------|---------|
| v16.6 | Sliding rectangle only, no detents | Intermediate |
| v16.7 | Open C + adversarial fit audit | Intermediate |
| **v16.8** | Tighter channel (no inside gaps) + Ø1.2 / 0.20 proud soft bumps | **Printed / tried → clip failure** |

### v16.8 geometry snapshot (digital)

- Wall **1.40 mm**, `CLIP_XW=4.2`
- Outer Y ≈ `[9.63, 12.0]` (detent tip ~9.43); Z ≈ `[14.05, 26.45]`
- Channel floor `|Y|=9.55`, lip Y **2.45**, wall-to-cavity **3.00**
- Slide clr: **0.08** mm total Y; **0.10** mm total Z
- Detent: bump Ø**1.20**, **0.20** proud; seat Ø**1.30**, depth **0.18**; Z centers 14.75 / 25.75; ~0.12 mm ride interference
- Parts: ClamshellA/B, OutputHub, BuckleClipYP/YM (+ Servo/MR128 proxies in CAD only)

Session (at export): `c1eaa786-7d76-4cd5-8dc5-cb3c9112b27d` · doc `320c97b5-fda0-4d0c-aa01-4969e93f91d7`

## Body / shell context (for structure review)

- `split_z ≈ 20`, shell ±12, cavity Y ±6.55
- Shaft-near flange ear trap (not continuous tab bar)
- Align: short dome nubs + socks; Technic grid on faces
- Hub / bearing / FACE_EXTRA history: shortened for printability then bearing restored; Technic cross ~5.00×2.00 snug

**Next session:** Jeff says main body has structure issues — prioritize diagnosing those (walls, ledges, nubs, flange nest, Technic breakthroughs, print orientation) over another clip invention.

## Artifacts in this branch

```
v16.2/ … v16.8/     gen_*.py, *.nbcad.jsonc, audit_*.json, gen_meta.json,
                    print/*.3mf (where present), shots/*.png (subset)
skills/             copies of Cad Bot workflows used on this part
docs/               early DESIGN + v11 plan notes
SESSION_HANDOVER.md this file
README.md           short pointer
```

Thunder working tree (may be fuller than git):  
`C:\Users\jeffg\Documents\noBS-CAD\INJS2065-Technic-Case\`  
Print pack also: `...\v16.8\print\` and `Documents\INJS2065\v16.8\print\`

## Skills / memory cues for next agent

- [AM clamshell retainer clip](skills/am-clamshell-retainer-clip/SKILL.md) — slide first, detent second
- [AM snap-fit design](skills/am-snap-fit-design/SKILL.md)
- [adversarial-mesh-audit](skills/adversarial-mesh-audit/SKILL.md)
- [validate-before-show](skills/validate-before-show/SKILL.md)
- [research-before-commit](skills/research-before-commit/SKILL.md)
- [mcp-vs-script-replay](skills/mcp-vs-script-replay/SKILL.md)

Cad Bot memory: open-C silhouette; Jeff strength/retention split; don’t invent snaps without him; live CAD screenshots only.

## Tooling notes

- MCP: `user-nobs-cad` — attach, script/view, `solid_export_3mf` (prefer), interference check
- Blank document before large scripts; long scripts may MCP-timeout while playback continues — poll session
- Live CAD displays often `:1` / `:8`; resize ~1200×720 before x11grab
- Grid snap: 10 mm / ~2.5 mm capture bug — disable while sketching, re-enable before `sketch_finish`
- noBS-CAD git (app): `jackControls/noBS-CAD` on Thunder `C:\Users\jeffg\dev\noBS-CAD` — Cad Bot may push **feature** branches; draft PR only when ready. **This design pack is a separate repo** (`jeffglousher/INJS2065-Technic-Case`).

## Suggested next-session plan

1. **Intake print failure** — photos/notes from Jeff on clip *and* body structure (where it cracked, flexed, didn’t seat, thin walls, etc.).
2. **Live CAD audit of body** (v16.8 nbcad) — wall thickness probes, flange nest, nubs/socks, Technic holes, split face, bearing/hub — adversarial mesh audit skill.
3. **Retainer:** pause inventive clips; either Jeff sketches the next retainer concept, or reduce to proven slide-only coupon while body is fixed.
4. Re-export / reprint only after body structure gates pass and Jeff signs clip approach.

## What not to do

- Don’t claim digital IFC PASS means printable success.
- Don’t invent new snap barbs/hooks/I-beams without Jeff.
- Don’t open a PR on jackControls/noBS-CAD for this design pack.
- Don’t start a printer job unless Jeff asks.

---
*Written by Cad Bot for Jeff · 2026-09-19 CT*
