title: New tool: clinostat simulator
date: 2026-10-20
author: Jerry Miao
summary: A browser-based simulator of the SciSpinner Max: set the frame and core speeds, watch the instrument turn, and see the motion sensor reading, time-averaged ⟨g⟩ and sphere coverage before a run.
tag: tools

A second tool is now on the [Tools page](/tools/): a [clinostat simulator](/tools/clinostat-simulator) for the SciSpinner Max.

Set each axis to a speed and direction, as on the instrument's own controls (0.050–5.000 rpm in 0.001 rpm steps, or 0 to hold an axis still), and the instrument turns on screen at those speeds. Beside it, the simulator shows what a motion sensor module in the core would read, and the time-averaged gravity ⟨g⟩ over 2-minute, 15-minute and 1-hour windows, plus how much of the sphere the gravity direction has covered so far. A run can be played in real time or at 10×, 60× or 600×, so an hour of rotation takes six seconds.

The calculation is the same one the instrument and the [g-level analysis tool](/tools/g-level-analysis) use: the kinematic model of Clary et al. (2022), sampled at 20 Hz and averaged over one-second means. The number the simulator reports for a pair of speeds is the number the analysis tool's "kinematic model" column gives for the same speeds. What it cannot know is your sensor's zero-g offset, which a real run measures and removes.

Two things it shows quickly that are easy to get wrong when choosing speeds. Equal speeds on both axes never average down: ⟨g⟩ settles at 0.5 g however long the run. A simple ratio such as 1 : 2 does average to nearly zero, but the gravity direction traces the same closed loop over and over and covers only about a fifth of the sphere. Speeds without a simple ratio, such as the default 3.875 and 1.5 rpm, cover the whole sphere within minutes and bring the one-hour average below 2 × 10⁻³ g.

Like the analysis tool, it runs entirely in your browser and nothing is uploaded. The 3D model is the same one that now turns on the home page.
