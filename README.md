# INJS2065 servo holder for LEGO Technic

A printable clamshell that holds an INJS2065 servo in a Technic build. Two retaining clips close the housing, and a bearing-supported output hub connects the servo shaft to a Technic cross socket.

![Servo holder viewed from every side](docs/images/turntable.gif)

## The parts

- Upper and lower shells with Technic mounting holes.
- Two hex-pattern retaining clips with rounded snap nubs.
- An output hub with a servo friction-fit socket and a Technic cross socket.
- A purchased INJS2065 servo and MR128 bearing, shown as reference hardware.

Print the **five plastic parts in PETG**. The servo and bearing are not included on the print plate.

## Inside the holder

![Exploded servo holder with all seven parts labeled](docs/images/exploded.png)

<details>
<summary>See the assembled rear, underside and opposite exploded view</summary>

![Assembled rear and cable side](docs/images/assembly-rear.png)

![Underside and servo opening](docs/images/underside.png)

![Exploded assembly from the opposite side](docs/images/exploded-rear.png)

</details>

![The cavities and mounting features inside both shells](docs/images/shell-interiors.png)

<details>
<summary>Look closer at the clips and output hub</summary>

![Clip pocket side and flat rear face](docs/images/clip-detail.png)

![The hub's servo socket and Technic cross socket](docs/images/hub-detail.png)

</details>

## How we made it

We designed and refined the holder in **[Limo CAD](https://github.com/limo-cad/Limo-CAD)**, exported the parts, then prepared the PETG print project in Bambu Studio. The editable model and saved print settings are included so you can adapt the holder to your own build.

The first print fits reasonably according to the owner. Its large end grooves were traced to local slicer modifiers that split the end-wall paths. The current print project removes those modifiers and applies the slower speeds across each whole shell, preserving the fitted geometry.

## Print plate

![Five PETG parts on the reviewed Bambu print plate](docs/images/print-plate.png)

The current project uses **Bambu X2D, a 0.4 mm nozzle and Bambu PETG Basic**, printing by object without supports, brims or skirts. Native slicing estimates **3 h 25 min and 22.49 g**.

It is ready for a **confirmation print**. Check the new end finish, clip seating and retention, and hub engagement and bearing rotation before putting it into service. Long-term retention and loaded operation remain unqualified.

## Make your own

- [Editable Limo CAD model](design/current.nbcad)
- [Current Bambu Studio print project — all five parts](review/grooves-20261105/assembly-uniform-shells.3mf)
- [Matching editable model JSON](design/current.model.json)

[Assembly notes](docs/assembly.md) · [Design and print workflow](docs/workflow.md) · [Detailed dimensions and fit](DESIGN.md) · [Latest all-parts review](review/readiness-20261106/README.md)

The older projects under `print/` retain the superseded regional modifiers. Use the **current Bambu Studio print project** linked above for the next print.
