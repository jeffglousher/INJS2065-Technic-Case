# Dimensions and print specification

Dimensions are millimetres. The editable design is [current.limo](design/current.limo)
with its matching [model JSON](design/current.model.json). Use
[servo-holder.3mf](print/servo-holder.3mf) for the five-part PETG print.

## Housing and clips

The two shells have Technic mounting holes and sixteen full hex posts with
1.70 mm projection. Each clip has two rows of four blind hex pockets, flat
pocket floors and four centered rounded nubs.

The nub protrusion is 0.28 mm, crest curve radius 0.80 mm, blend radius 0.20 mm
and meridian span 1.4664 mm. The minimum corner wall in the clip plane is
0.897584 mm; flat backing is 1.45 mm. Inner hex clearance is 0.10 mm per flat.
The receiving seat has a 0.50 mm radius and 0.020 mm crest-center relief.

The clip is a backed closed frame. Local flex and printed contact determine
retention; rigid geometry alone does not predict insertion force, holding force,
allowable strain, creep or fatigue. Those quantities remain unqualified.

![Shell interiors](docs/images/shell-interiors.png)

![Clip pockets and rear face](docs/images/clip-detail.png)

## Hub and rotating clearances

The servo socket is nominally diameter 5.70 × 3.70 deep, friction fit, with a
0.15 mm entry chamfer and 3.55 mm straight engagement. The Technic cross socket
has 4.85 mm overall span, 1.85 mm arms and 8.00 mm depth. The separating web is
3.80 mm.

The hub journal is diameter 7.94 mm. The housing aperture is diameter 8.35 mm,
giving 0.205 mm nominal radial clearance. The MR128 bearing has an 8 mm bore,
12 mm outer diameter and 3.5 mm width; nominal radial journal clearance is
0.030 mm. Overall housing-to-hub minimum clearance is 0.150 mm. CAD dimensions
are not guaranteed printed fits.

![The hub's two sockets](docs/images/hub-detail.png)

## Saved print settings

Bambu X2D, 0.4 mm nozzle, Bambu PETG Basic, textured plate at 70 °C. Nozzle
settings are 245 °C for the first layer and 250 °C thereafter. The process uses
four walls, 25% gyroid infill, 0.16 mm layers and a 0.20 mm first layer.

Shells use Arachne and whole-shell speeds: outer walls 30 mm/s, inner walls
45 mm/s, gap fill 30 mm/s, internal solid infill 45 mm/s and top surfaces
30 mm/s. Detail bands request 0.12 mm layers: lower shell Z=5.0–10.95; upper
shell Z=0.2–3.6, 8.5–15.5 and 18.0–24.45 in oriented build coordinates.

Clips and hub use Classic. The hub is flipped on the plate and uses 0.08 mm
layers, six walls and 100% infill. There are no modifier volumes, supports,
support paint, brims or skirts. Print by object. Native slicing estimates about
3 h 25 min and 22.49 g; no printer job was sent.

## Validation and acceptance

[Validation](docs/validation.json) records five closed, connected,
positive-volume meshes with consistent winding, matching saved model/JSON and
successful native slicing. End-wall continuity is probed on both shells. These
checks do not exhaustively detect triangle self-intersections or establish
printed strength. [Dimensions](docs/dimensions.json) records the geometric values.

The owner reports reasonable printed fit but inadequate snap retention on the
last print. Snap retention is not accepted. Identify the printed revision and
measure the mating features before choosing another detent increment. Use the
complete aligned shells for a controlled retention test, reusing sound printed
parts where possible. Check end finish, unsupported hex undersides, seam closure, full clip
seating, snap retention, permanent set, hub engagement, bearing rotation, torque
transmission and axial retention. Repeat insertion cycles and a loaded holding
dwell. Follow [the assembly notes](docs/assembly.md). PETG results do not qualify PLA.
