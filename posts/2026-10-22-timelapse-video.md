title: Time-lapse to video tool
date: 2026-10-22
author: Jerry Miao
summary: A browser tool that turns the still images in a run's timelapse folder into an MP4 with an elapsed-time overlay, using the interval and start time from experiment.json.
tag: tools

The [Tools page](/tools/) has a new entry: [time-lapse to video](/tools/timelapse-video).

During a run, the SciSpinner Max saves one still per interval into `sessions/<name>/timelapse/` on the USB drive, numbered in capture order. The tool takes that folder, or the whole session folder, and produces an MP4.

If `experiment.json` is present, it reads the interval and start time so the overlay can show either elapsed time from the start of the run or the date and time of each frame. Without it, the interval can be entered manually, or the frame number can be shown instead.

The frame rate, output size (720p, 1080p or the original 2592 × 1944), quality and frame range are adjustable, and every Nth frame can be used for very long runs. A 24-hour run at 5-minute intervals is 289 frames, about 12 seconds of video at 24 fps. The page also shows the speed-up and how much of the run one second of video represents.

Encoding uses the browser's own H.264 encoder, so the file plays in QuickTime, PowerPoint and on the web, and nothing is uploaded. Frames are read one at a time, so a run of several thousand full-resolution stills works on an ordinary laptop.
