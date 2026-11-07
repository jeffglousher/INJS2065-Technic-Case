# INJS2065 servo holder for LEGO Technic

A printable clamshell that holds an INJS2065 servo in a Technic build. Two retaining clips close the housing, and a bearing-supported output hub connects the servo shaft to a Technic cross socket.

**Start with the retention coupons.** The new tool-released latch needs printed
fit and load testing. Follow the [test instructions and print files](docs/retention-trial.md)
before printing a complete housing. The gallery below shows the control design.

![Servo holder viewed from every side](docs/images/turntable.gif)

<details>
<summary>See a still assembled view</summary>

![Assembled servo holder](docs/images/assembly.png)

</details>

## The parts

- Upper and lower shells with Technic mounting holes.
- Two hex-pattern retaining clips with rounded snap nubs.
- An output hub with a servo friction-fit socket and a Technic cross socket.

Print the **five plastic parts in PETG**. The servo and bearing are not included on the print plate.

## Bill of materials

Purchased parts:

- **1 × INJS2065 servo**
- **1 × MR128 bearing** — 8 mm bore × 12 mm outer diameter × 3.5 mm width

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

The last print fit reasonably, but its clips slid in loosely. The new latch
adds a defined spring tongue and retaining shoulder. Both versions use continuous
end-wall toolpaths; physical acceptance of the new latch is pending.

## Control print plate

![Five PETG parts on the reviewed Bambu print plate](docs/images/print-plate.png)

The current project uses **Bambu X2D, a 0.4 mm nozzle and Bambu PETG Basic**, printing by object without supports, brims or skirts. Native slicing estimates **3 h 25 min and 22.49 g**.

Print the [retention coupons](docs/retention-trial.md) first. If a coupon passes,
test the corresponding complete housing for clip retention, end finish, hub
engagement, bearing rotation and loaded operation before putting it into service.

## Make your own

- [Retention trial: print files, part identification and test procedure](docs/retention-trial.md)
- [Editable Limo CAD latch model](design/retention/latch.limo)
- [Editable Limo CAD control model](design/current.limo)
- [Bambu Studio control project — all five parts](print/servo-holder.3mf)
- [Control model JSON](design/current.model.json)

[Assembly notes](docs/assembly.md) · [Design and print workflow](docs/workflow.md) · [Dimensions and fit](DESIGN.md) · [Validation](docs/validation.json)
