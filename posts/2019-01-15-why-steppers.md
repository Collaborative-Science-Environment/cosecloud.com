title: Choosing the motors: DC, servo or stepper
date: 2019-01-15
author: Jerry Miao
tag: engineering
summary: What each axis of a clinostat needs from its motor, the five ways it could be driven, and which one we chose.

Each axis of the clinostat needs a motor. Before choosing one, we wrote down what the axes actually need to do, then worked through the available ways to drive them.

## What the motor has to do

- Turn at any speed from 0.05 to 5 rpm, settable to 0.001 rpm. At the slow end, that is one turn every twenty minutes.
- Hold that speed exactly. The time-averaged gravity a sample sees depends on the ratio between the two axes, so any speed drift changes the experiment.
- Keep running for weeks inside a warm, humid incubator.
- Cope with a load that is never perfectly balanced. A sample mounted off-centre makes the axis harder to turn on the way up than on the way down.
- Stop one axis and hold it still while the other turns.

## The options

| | Brushed DC gear motor | DC gear motor with encoder | Brushless servo | Stepper, direct drive | Stepper with gearbox |
|---|---|---|---|---|---|
| Speed accuracy | Drifts with load, voltage and temperature | Good once the loop is tuned | Excellent | Exact; set by a clock | Exact; set by a clock |
| Smoothness at 0.05 rpm | Poor; stalls and surges near standstill | Poor; the loop has little to work with | Good with a fine encoder | Fair; the motor is barely turning and every step shows | Good; microstepping plus a 10:1 reduction |
| Uneven load | Speeds up and slows down each turn | Corrected by the loop | Corrected by the loop | Little torque margin; risk of skipped steps | Absorbed by gearbox torque |
| Holding still | Needs a brake | Needs active control | Active control | Holds position by itself | Holds position by itself |
| Weeks of running | Brushes wear | Brushes wear | No wear parts besides bearings | No wear parts besides bearings | No wear parts besides bearings |
| Extra wiring through the slip rings | None | Encoder lines | Encoder lines | None | None |
| Parts and tuning | Simplest | Encoder and a tuned loop per axis | Encoder, servo drive, tuning | Driver only | Driver and gearbox |
| Main weakness | Cannot hold a set speed | Weak at very low speed | Cost and complexity | Torque and smoothness at low speed | Vibration, heat, open loop |

## Brushed DC gear motor

A brushed DC gear motor is cheap, simple, and perfectly adequate for something that only needs to turn. The problem is that its speed depends on voltage, load, and motor temperature.

With an unbalanced chamber, the motor speeds up and slows down over each revolution, and its average speed can drift over a long run. For a clinostat, where rotation speed is part of the experiment, that makes an open-loop DC motor a poor fit.

## DC gear motor with an encoder

Adding an encoder and a control loop fixes most of the drift at moderate speeds.

At 0.05 rpm, though, the motor is barely moving. The encoder produces few counts, so the loop has little information to work with, and the motion becomes a series of small corrections rather than a smooth rotation.

The brushes also still wear during long runs, and the encoder signals for the inner axis have to pass through a slip ring.

## Brushless servo

A brushless motor with a fine encoder and a closed-loop drive can do everything a clinostat needs, and it is the approach used in many industrial positioning systems.

The tradeoff is complexity. Each axis needs an encoder, a servo drive, and a tuned control loop, and the inner axis needs additional encoder lines through the slip rings. That is a lot of hardware for a problem that may not require it.

## Stepper motor, direct drive

A stepper takes a different approach. Its speed is not measured and corrected; it is defined by the rate at which the driver issues steps.

The steps come from a crystal clock, and the shaft moves a fixed angle for each full step, so the speed is set by a ratio of two numbers rather than by the output of a feedback loop. It does not drift with load or temperature as long as the motor does not lose steps, and at zero speed it holds its position. That makes a set-point of 0.001 rpm meaningful without an encoder.

Mounted directly on the axis, though, a stepper is operating at the edge of what it does well. At 0.05 rpm, the motor itself is also turning at 0.05 rpm, slow enough that each step and the motor's natural detent can show up in the motion.

A NEMA 17 on its own also has modest torque. An off-centre sample uses up much of that margin, and if the motor runs out of torque, a stepper can skip steps without knowing it.

## Stepper motor with a gearbox

Putting a 10:1 planetary gearbox between a NEMA 17 stepper and the axis keeps the stepper's exact speed while addressing both problems.

The gearbox multiplies torque, giving the axis more margin against an unbalanced load. It also reduces the motion seen at the axis: the driver selects the microstepping automatically based on speed, up to 256 microsteps per full step, and at that setting the axis moves about 0.0007° per microstep. That makes very slow rotation smooth rather than a sequence of visible steps.

The gearbox also lets the motor run ten times faster than the axis, in a range where a stepper runs better.

## What we chose

Every option could turn the axes. The steppers are the only options here that hold an exact speed without a feedback loop, and the geared stepper also provides the smoothness and torque margin needed at the slowest speeds and with an unbalanced load.

Each axis of the SciSpinner Max is therefore driven by a NEMA 17 stepper motor with a 10:1 planetary gearbox.

It is not free of weaknesses, and most of the motor-control design work went into dealing with them:

- Vibration and noise. A silent-stepping driver with automatic microstepping, up to 256 microsteps per step, keeps the motion smooth and the instrument quiet.
- Microstepping is not precision. A microstep is not an exact position. Between full steps, the shaft settles where the coil currents and the load balance, so a stepper commanded to a particular microstep will not return to exactly the same angle every time. That would matter in a positioning stage. A clinostat does not need to stop at a precise angle; it needs continuous, even rotation. In that application, microstepping does what we need by smoothing the motion between full steps. The error does not accumulate either: every full step returns to a defined position, so the average speed stays exact.
- Open loop. A stepper does not know whether it has skipped a step, so the driver's stall and over-temperature detection are reported as faults rather than going unnoticed.
- Heat. A stepper draws current even when it is moving very slowly, and in an incubator that heat matters, so the drive current is set no higher than the load requires.
