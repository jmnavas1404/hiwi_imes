# Sessions Notes
# Session 3 — Motion Sensors: The Unlabelled Signals

**Responsible**: Timo

**Status:​** Capture2Go IMUs + custom GUI

**Suggestion**: write it in Java script or jupiter notebook

### Main topic

What a motion sensor sees. Two sensor types inside (accelerometer, gyroscope), three directions each — and the students find out by experiment which curve is which. Nothing on drift, Euler angles or orientation algorithms (not needed before S7, if at all).

### The core idea: the “unlabelled GUI”

Students receive a custom experiment (“Foot Sensor”, distributed as a QR code) that shows six live traces called **Signal 1 … Signal 6** with no sensor names, no units, no sampling rate. Their job is to fill in every label by physical experiment. The experiment has editable label fields; once labelled, the group exports its recording and a screenshot of the now-labelled screen.&#x20;

→ Save data of 10s of recordings to a CSV file for session 4

| Blank                                                         | How the students find it                                                                                                                                                                                |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Which 3 signals are the accelerometer, which 3 the gyroscope? | imu at rest: three signals sit near zero (gyro), one of the other three sits at a constant non-zero value (gravity).                                                                                    |
| Unit of the accelerometer                                     | Read the resting value: ≈ 9.8 → m/s², ≈ 1 → g.                                                                                                                                                          |
| Which signal is which axis                                    | Lay the imu flat, on its long edge, on its short edge — the         gravity value jumps from one signal to another.                                 Same for the gyro: rotate about one edge at a time. |
| Unit of the gyroscope                                         | Quarter turn in \~1 s: peak ≈ 90 → °/s; ≈ 1.6 → rad/s.                                                                                                                                                  |
|                                                               | Record exactly 10 s, count rows in the CSV / read timestamp     spacing                                                                                                                                 |
| Which signal is “toes up” when mounted on the foot            | Strap the imu to the foot and do the movement.                                                                                                                                                          |

​

### Timeline (3 h)

| Time | Block                                                                                                                                                                                                                                                     | Length |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 0:00 | **Presentation:​** a motion sensor turns movement into curves; two sensor types inside (feels gravity/pushes vs feels turning); three directions each; live demo “I tilt the imu and this line moves”; today’s task.   QR code for the custom experiment. | 25 min |
| 0:25 | **Label game, IMU in hand:​** fill in the six blanks using the tricks above; write the evidence for each label on the worksheet (what was done, what was seen).                                                                                           | 60 min |
| 1:25 | Break                                                                                                                                                                                                                                                     | 10 min |
| 1:35 | **IMU on the foot:​** strap the imu to the foot - record five movements in sequence with a tap before each (toes up, toes      down, foot in, foot out);                          mark them by hand on a screenshot;      name the “toes-up” signal.      | 35 min |
| 2:10 | **Export:​** save the recording as CSV into the group folder — this is the file S4 uses. Check the file opens and has the expected columns.                                                                                                               | 10 min |
| 2:20 | **Mystery recording:​** each group gets a lecturer-recorded CSV/screenshot of an unknown movement (a step, a kick, a foot tap, standing still, …) and must say what was done, using their labels.                                                         | 15 min |
| 2:35 | **Closing:​** groups compare their sampling rates and their “toes-up” axis; short Q\&A.                                                                                                                                                                   | 25 min |

### Material to be brought by lecturers

* Slide deck (25 min).

* Custom experiment “Foot Sensor”

* Worksheet: label table (Signal 1–6 → sensor / axis / unit, plus the evidence), sampling-rate box, foot-mounting box, mystery-recording answer box.

* Foot mounting: elastic straps or a sock/velcro band per group;&#x20;

* Five different mystery recordings (CSV + screenshot), one per group. -> could be skipped

* Backup: a lecturer-recorded reference CSV in case a group’s export fails (dependency rule).

### Independent work

1. Label game with the imu in hand (60 min).

2. imu on the foot: five-movement recording, hand-marked screenshot (35 min).

3. CSV export to the group folder (10 min).

4. Mystery recording (15 min).

### Deliverable (per group)

* Worksheet with all six labels **and the evidence** for each.

* Screenshot of the labelled experiment.

* Hand-marked screenshot of the five-movement recording + mounting photo.

* Mystery-recording answer.

* Exported CSV in the group folder (checked).

### Open points for S3

* Build and test the custom phyphox experiment (can be drafted with Claude in an afternoon).

* Confirm iOS/Android axis conventions in the experiment so that “toes up” is findable on both.

* Decide go/no-go for the Movella DOT GUI (see settled boundary conditions).