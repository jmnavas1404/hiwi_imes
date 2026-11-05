# Sessions Notes

# Bachelor Project — Session Plan (working notes)

Updated after BME PhD meeting on 2026-09-23 · Status: all 10 sessions agreed at concept level; open points listed per session and in “Open questions”.

## Frame

* 10 sessions × 3 h, \~20 first-semester students in 5 fixed groups of 4.

* Students have little to no engineering knowledge and cannot code. Tasks must be as simple as possible; the goal is curiosity and independent learning.

* Sessions 1–4: one self-contained topic each, defined by (1) main topic, (2) material brought by lecturers, (3) independent work + deliverable.

* Sessions 5-7: putting the knowledge from the first lectures together, combining experiments and mostly doing independent work with deliverables

* Sessions 8–9: one more complex task, leading to the final presentation in Session 10.

## Settled decisions

* **Stimulators:​** commercial TENS/EMS units bought online (e.g. Beurer EM 49 / Sanitas SEM 43 class), ideally one per group + 1 spare. Must have a user-programmable mode (frequency, pulse width, on/off time adjustable) — verify in the manual before ordering; buy one unit first and test the S2 worksheet on the lecturers.
  Suggested by Jakob: <https://www.lidl.de/p/dr-senst-ems-tens-geraet-2in1-as1080a/p100387878>

* **Supervision:​** maximum one supervisor in the room and/or the HiWi (Umashankar). Safety in FES sessions therefore relies on the worksheet (settings check, printed rules), not on continuous observation.

* **Ethics, insurance, consent:​** dealt with at institute level; not a planning concern.

* **LLMs:​** students use freely available LLMs (no paid accounts provided). Students create accounts before S1; each group keeps a second option in case of rate limits.

* **Motion sensor:​** Capture2Gos IMUs&#x20;

* **Notebook environment:​** **JupyterLite**. Hosted as a static site (institute web server or GitHub Pages) with the course notebooks and reference CSVs pre-bundled, so students open one URL and the notebook is already there. Caveats: first load takes 1–2 min and needs internet; files live in that browser’s storage (IndexedDB) — results must be downloaded to the group folder explicitly, and clearing the browser cache loses local edits.
  Fallback: Google Colab (needs a Google account). No university JupyterHub exists.

* **Laptops:​** at least one per group is a course requirement (checked in S1).

* **Notebooks:​** S4 is the only “coding” session. S7 uses a second pre-written notebook and concentrates on understanding results, not on how code works.

## Open questions (affect several sessions)

* Who hosts the JupyterLite site, and is it reachable from the university network without login?

## Sessions

### Session 1 - The Big Picture: Foot Drop, First Ideas, First Investigation

#### **Responsible person**: Lucia

### Main topics

* Organisational and introductory information of the project and imes,

* Foot drop as a clinical problem; what a technical solution would have to do;&#x20;

* Forming the fixed teams.&#x20;

The lecturer presentation is split in two parts so that students first design and investigate on their own, and only then see the existing solutions and the course concept.

→ remind students that next session they need to attach the patches to the leg → access to skin

Maybe Tim-David has similar slides

Ask if they access to eduroam, email adresses, stud.ip

### Timeline (3 h)

| Time | Block                                                                                                                                                                            | Length |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 0:00 | **Slides part 1:​** welcome, what foot drop is, videos of steppage gait, impact on daily  life, group formation. Nothing yet about FES or IMUs.                                  | 30 min |
| 0:30 | **Design challenge (no phones/laptops):​** patient card + paper sketch answering three questions — What does your device do? How does it know when to act? What could go wrong?  | 25 min |
| 0:55 | **Self-Guided investigation:​** each group researches one *sub-question*\* with the web and an LLM, and builds one slide.                                                        | 50 min |
| 1:45 | Break                                                                                                                                                                            | 10 min |
| 1:55 | **Groups teach their slide:​** 3 min each + questions.                                                                                                                           | 25 min |
| 2:20 | **Slides part 2:​** existing solutions (AFO, commercial FES devices), course concept (FES = motor, IMU = eyes, Python = brain), roadmap, roles, logistics, notebook-login check. | 30 min |
| 2:50 | **Reflection:​** groups write one sentence on their sketch — “what would we change now?”                                                                                         | 10 min |

Independent work ≈ 1 h 40 (design challenge + investigation + mini-talks + reflection).

Order matters: the design challenge must come before the investigation, otherwise researching existing devices spoils it.

### \*Sub-questions (one per group)

1. What causes foot drop?

2. How does an ankle brace (AFO) work, and what are its downsides?

3. Which commercial FES foot-drop devices exist, and what do they cost?

4. How can a device detect that someone is taking a step? *(hard to research → provide 2–3 starting links)​*

5. What do patients say about daily life with foot drop? *(hard to research → provide 2–3 starting links)​*

### Material to be brought by lecturers

* Slide deck part 1 (problem, **videos**, group formation) and slide deck part 2 (existing solutions, course concept, roadmap, logistics).

* 5 patient cards (can all be the same patient, e.g. “58-year-old after stroke, trips on carpets, wants to walk to the bakery”).

* Sketch worksheet for groups → with the three initial questions + space for the final “what would we change now?” sentence after second session of presentation.

* One-slide template for the “presentation” of their idea.

* Group folder structure; login instructions for the notebook environment.

### Independent work

1. Design challenge on paper (25 min).

2. Web + LLM investigation of the group’s sub-question, producing one slide (50 min).

3. Teaching the slide to the class (3 min per group).

4. Revisiting the sketch after slides part 2 (10 min).

### Deliverable (per group)

* The sketch worksheet, including the “what we’d change” sentence.

* The one slide, following two rules:

  * max. 30 words, one image, sources named, presented without notes;

  * a corner box: “one thing the LLM told us that we couldn’t verify, or that was wrong”.

### Open points for S1

* Official LLM for students (see open questions).

* Confirm every student can log into the notebook environment during slides part 2.

​

# Session 2

FES: Making a Muscle Move, Safely

**Responsible person**: Khaled

### Main topic

How electricity moves a muscle, how a stimulator delivers it, what amplitude and frequency change, and how to place electrodes to get a foot lift. Students feel all of it on themselves.

### Timeline (3 h)

| Time | Block                                                                                                                                                                                                                                                                                                                                                              | Length |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------ |
| 0:00 | **Presentation:​** nerve → muscle → movement, and how an external pulse does the nerve’s job; how the stimulator delivers  current; amplitude (recruits more fibres → stronger) and frequency (single twitches vs smooth contraction, faster fatigue at high frequency); live electrode-placement demo on a lecturer; safety rules; consent/contraindication form. | 30 min |
| 0:45 | **Setup + settings check:​** each group programmes the device (frequency, pulse width, on/off time as given on the worksheet)                                                                                                                                                                                                                                      | 15 min |
| 1:00 | **Forearm warm-up:​** find the wrist extensors; record two thresholds (first tingle, first visible movement) for one volunteer. Low-risk, builds confidence; lets the supervisors see which groups need attention.                                                                                                                                                 | 25 min |
| 1:25 | **Frequency experiment:​**fixed comfortable intensity, very low frequency (\~2–5 Hz)   vs normal (\~30–40 Hz); describe what is  seen (separate twitches vs smooth held movement). Only possible with a manual mode                                                                                                                                                | 15 min |
| 1:40 | Break                                                                                                                                                                                                                                                                                                                                                              | 10 min |
| 1:50 | **Electrode map on tibialis anterior:​** 3–4  positions marked with skin marker; for    each, record foot movement (lift/turning outward / nothing) and comfort 0–10; find the best position.                                                                                                                                                                      | 50 min |
| 2:40 | **Closing:​** groups compare best positions and thresholds; short Q\&A.                                                                                                                                                                                                                                                                                            | 20 min |

### Safety with one supervisor + HiWi

* Settings check with initials before any group switches on (5 × \~2 min, split between the two).

* Three rules printed on the worksheet and in the slides: (1) only the stimulated person touches the intensity buttons; (2) one step at a time, never while the device is off-cycle; (3) “stop” means stop, no discussion.

* Anyone who prefers not to be stimulated takes the operator/recorder role.

### Material to be brought by lecturers

* Slide deck (30 min).

* One stimulator + electrodes per group (+ spare); batteries charged.

* Electrode placement photo guide (forearm wrist extensors, tibialis anterior with 3–4 marked candidate positions).

* One-page device quick-start card (original manual is unusable for this).

* Worksheet with: settings box, threshold table, frequency-observation box, electrode map table, one-sentence conclusion.

* Consent/contraindication forms (institute template).

* Skin marker, measuring tape, alcohol wipes, paper towels.

### Independent work

1. Programme the device and get the settings check.

2. Forearm warm-up: two thresholds for one volunteer.

3. Frequency experiment: low vs normal frequency at fixed intensity.

4. Electrode map on the tibialis anterior: 3–4 positions, movement + comfort per position.

### Deliverable (per group)

* Completed worksheet: device settings (initialled), thresholds, frequency observations, electrode map with the best position marked.

* One sentence: why electrode placement matters.

### Open points for S2

* Confirm the chosen device has a manual mode; otherwise drop the frequency experiment and keep only intensity.

* Electrode reuse/hygiene policy (personal set per student vs shared per group) drives the electrode order.

​

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

​

# Session 4 — The Notebook as an Instrument

**Responsible**: Jakob

### Main topic

Run a pre-written notebook on your own sensor data, change a handful of marked parameters, and use an LLM to explain what a cell does and to make one small change. Students never write code from a blank cell. Little to no active supervision: the guide and the notebook carry the session.

* No Python basics (variables, lists, loops), no pandas/matplotlib teaching. The notebook does the work; students turn knobs.

* Free chat LLM in the browser instead of Copilot; three prompts that work are given on a card.

* JupyterLite instead of Colab (no accounts).

### The notebook (5 cells, each with a large comment header and one “YOU MAY CHANGE THIS” box)

| Cell              | What it does                                                 | What students may change                         |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------ |
| 1 Load            | Reads the CSV, prints the first rows and   the column names. | File name                                        |
| 2 Plot everything | All six signals vs time.                                     | Nothing (uses cell 1)                            |
| 3 Pick one signal | Plots one column with a proper y-axis label.                 | Column name, y-axis label (from their S3 labels) |
| 4 Zoom            | Cuts the plot to a time window and adds a title.             | Start time, end time, title.                     |
| 5 Save            | Saves the figure as PNG.                                     | File name.                                       |

Runs on first click with the bundled reference CSV. Comments are written for absolute beginners (what the cell does, what the parameter means, what a typical error looks like).

### Timeline (3 h)

| Time | Block                                                                                                                                                                                                                                | Length |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------ |
| 0:00 | **Presentation:​** what a notebook is (cells, run button, output); the five cells shown live on the reference CSV; how to talk to an LLM about code (the three prompts); the rule “you only edit inside the boxes”.                  | 25 min |
| 0:25 | **Run it as delivered:​** open the URL, run all five cells on the reference CSV — every group has a working plot within 10 min.                                                                                                      | 15 min |
| 0:40 | **Own data:​** upload the group’s S3 CSV, change the file name, rerun. If columns are named differently it breaks — fix the column name in cell 3. First real debugging, one-word fix.                                               | 30 min |
| 1:10 | **Find the five movements:​** zoom (cell 4) to each S3 movement in turn using the tap markers; save the best one (cell 5).                                                                                                           | 30 min |
| 1:40 | Break                                                                                                                                                                                                                                | 10 min |
| 1:50 | **LLM explain-a-cell:​** paste one cell into the LLM, ask what it does, write a two-sentence explanation in own words. Then ask the LLM for one small change (line colour, grid, thicker line), paste it in, check whether it works. | 35 min |
| 2:25 | **Break it on purpose (fast groups):​** delete a bracket, read the error, ask the LLM what it means, fix it. Slower groups finish the PNG.                                                                                           | 20 min |
| 2:45 | **Closing:​** each group shows its PNG; one error each group met and how it was solved.                                                                                                                                              | 15 min |

### Material to be brought by lecturers

* JupyterLite site with `S4_notebook.ipynb` and the reference CSV pre-bundled; deep link that opens the notebook directly. Tested on Windows, macOS and at least one low-RAM laptop; Chrome/Edge/Firefox; Safari checked.

* **Student guide (may be several pages, screenshot-based):​** opening the URL; what to do while it loads; running a cell; uploading a CSV; where the PNG ends up and how to download it into the group folder; a **troubleshooting page** with the six most common problems (page stuck loading → reload; “file not found” → check the file name and upload; “KeyError” → column name; plot empty → time window outside the recording; kernel busy → wait/restart; browser storage cleared → re-upload). This page is what replaces the supervisor.

* **LLM prompt card** with three prompts: “Explain this cell to a complete beginner”, “I got this error: … What does it mean and what do I change?”, “Change X in this code and give me the full cell back”.

* Worksheet: explanation of one cell (two sentences), the LLM change and whether it worked, one error and its fix.

* Backup: reference CSV covers any group whose S3 export failed.

### Independent work

1. Run the notebook on the reference CSV.

2. Swap in own data, fix the column name.

3. Zoom to the five S3 movements, save one as PNG.

4. LLM: explain one cell; make one small change.

5. Optional: break it and fix it.

### Deliverable (per group)

* PNG of one movement: labelled axes with units, title, in the group folder.

* Worksheet: two-sentence explanation of one cell; the LLM change and its result; one error message and how it was resolved.

### Open points for S4

* Build the JupyterLite site and the notebook; test the first-load time on the university network.

* Decide where group folders live (shared drive) so the PNG download step is unambiguous.

​

# Sessions 5–7 — how they fit together

Each is self-contained with its own deliverable and a lecturer-provided backup dataset, but they build one story: **S5** measure the foot lift (FES + sensor, response curve), **S6** is it repeatable? (same measurement repeated; first honest look at variability), **S7** what does the data say? (second pre-written notebook turns the S5/S6 files into one figure; students interpret). S8–S9 reuse the same setup for the complex task.

​

# Session 5 - Measuring the Foot Lift (FES + sensor)

Responsible person: HiWi

### Main topic

Combining the two tools for the first time: the stimulator lifts the foot, the sensor measures how much. Result: a **response curve** — foot angle vs intensity step — for one subject. The measurement is **static** (seated, foot hanging free); no walking with the stimulator on.

→ Be sure they save the data to use it in later sessions for comparison (naming conventions)

### The measurement

Subject seated, lower leg free, foot hanging relaxed. IMU attached to foot, live data streaming. Note the resting angle. Increase intensity one step at a time; at each step, during the stimulator’s “on” phase, read the angle off the screen and write it in the table. **Start with one reading per step**; if time allows, go back and take three readings per step (the repetition then feeds S6). Stop at “comfortable”.

### Timeline (3 h)

| Time | Block                                                                                                                                                                                                                                                                                           | Length |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 0:00 | **Presentation:​** why we measure instead of watch; what a response curve is (sketch: angle vs intensity); the protocol on one   slide; safety rules from S2 repeated; start from your S2 best position.                                                                                        | 30 min |
| 0:30 | **Setup + settings check:​** electrodes at the S2 best position, imu strapped to the foot, Inclination reading stable at rest; device settings checked and initialled by a supervisor.                                                                                                          | 25 min |
| 0:55 | **Response curve, one reading per step:​** from zero to comfortable, angle noted at each step.                                                                                                                                                                                                  | 35 min |
| 1:30 | Break                                                                                                                                                                                                                                                                                           | 10 min |
| 1:40 | **Response curve, three readings per step (if time allows):​** repeat the ramp twice more; otherwise use this slot to finish and tidy the table.                                                                                                                                                | 35 min |
| 2:15 | **Plot on paper + observations:​** angle vs intensity on the prepared grid; three observations (where does the foot start to move; straight line or flattening; straight lift or sideways turn). Fast groups: repeat with electrodes 2 cm off the best position, second curve on the same grid. | 25 min |
| 2:40 | **Export + closing:​** one recorded phyphox file of a full ramp exported to the group folder (checked); groups compare curves; Q\&A.                                                                                                                                                            | 20 min |

### Material to be brought by lecturers

* Slide deck (30 min).

* Stimulators + electrodes (one set per group + spare), batteries charged.

* IMUs (Inclination experiment) + foot straps; a chair per subject where the foot hangs free.

* Worksheet: settings box (+ initials), resting angle, table intensity step × reading 1/2/3, prepared plot grid, three-observation box, mounting-photo box.

* The groups’ own S2 electrode maps, returned.

* Backup: a lecturer-recorded full-ramp file for S7 (dependency rule).

### Independent work

1. Setup: S2 best position, imu on foot, stable resting angle, settings check.

2. Response curve, one reading per step.

3. Response curve, three readings per step (if time allows).

4. Plot on paper; three observations.

5. Optional: second curve with electrodes moved 2 cm.

6. Export one full-ramp recording to the group folder.

### Deliverable (per group)

* Worksheet: filled table, hand-drawn response curve, three observations, mounting photo.

* One exported phyphox recording of a full ramp in the group folder.

### Open points for S5

* Confirm on the real device how long the “on” phase is, so that one reading per step is comfortably possible (it drives the worksheet timing).

* Confirm that the Inclination reading is stable enough on the foot (test once with the strap).

​

# Session 6 - Is It Repeatable?

**Responsible**: HiWi

### Main topic

Repeatability: *if we do exactly the same thing again, do we get the same number?​* The S5 measurement repeated under three conditions; a first honest look at how much the numbers move. No statistics vocabulary beyond “spread”.

### The measurement

Not the whole ramp. Each group picks **two intensity steps** from its S5 curve — a low one just above the movement threshold and a comfortable high one — and measures the angle at those two steps only (\~2 min per repetition), using the same static setup as S5 (seated, imu on foot).

### Timeline (3 h)

| Time | Block                                                                                                                                                                                                   | Length |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 0:00 | **Presentation:​** one real example of “the same measurement, ten times” from any field; the three rounds explained; the two-step protocol; safety rules repeated.                                      | 25 min |
| 0:25 | **Setup + settings check:​** S5 electrode position marked on the skin, imu on foot, resting angle noted; supervisor initials. Choose the two intensity steps from the S5 curve.                         | 20 min |
| 0:45 | **Round 1 — same everything:​** same subject, electrodes untouched, **five** repetitions of the two-step measurement in a row (trial-to-trial noise). Record at least this round in phyphox and export. | 35 min |
| 1:20 | Break                                                                                                                                                                                                   | 10 min |
| 1:30 | **Round 2 — electrodes off and on again:​** remove electrodes, re-place at the marked position, measure; **three** times (placement effect — usually the biggest surprise).                             | 30 min |
| 2:00 | **Round 3 — different subject:​** second group member, same protocol, same intensity steps (subject effect). Groups with only one volunteer swap subjects with a neighbouring group for this round.     | 30 min |
| 2:30 | **Dot plot + three sentences:​** all high-step readings as dots in three columns on the worksheet grid (“same”, “re-placed”, “other person”); three sentences on the spread.                            | 20 min |
| 2:50 | **Closing:​** groups show their dot plots side by side; which round moved the most?                                                                                                                     | 10 min |

### Material to be brought by lecturers

* Slide deck (25 min).

* Same hardware as S5 (stimulators, electrodes, imus with gui, straps, chairs), skin marker.

* The groups’ S5 worksheets, returned (to choose the two steps).

* Worksheet: settings box (+ initials), chosen steps, three-round table (round × repetition × low/high angle), dot-plot grid with three labelled columns, three-sentence box.

* Backup dataset for S7 (a lecturer-recorded three-round set).

### Independent work

1. Setup, mark the position, choose the two steps.

2. Round 1: five repetitions, same everything (recorded and exported).

3. Round 2: three repetitions with electrodes re-placed.

4. Round 3: second subject.

5. Dot plot and three sentences.

### Deliverable (per group)

* Worksheet: three-round table, three-column dot plot, three sentences (how much did the number move when nothing changed / when the electrodes were re-placed / with the other person).

* Exported phyphox recordings of at least round 1 in the group folder.

### Open points for S6

* One volunteer per group is enough for rounds 1–2; round 3 needs a second volunteer or a swap with a neighbouring group — say so in S1 when roles are explained.

​

# Session 7 —

What Does the Data Say?

**Responsible:​** HiWi

### Main topic

From a table of readings to a picture of the whole experiment. A second pre-written notebook turns the S5 and S6 recordings into figures; students interpret, they do not code. The point: the recording holds more than the numbers read off the screen (rise when the stimulator switches on, plateau, dip in the off phase, sag over repetitions as the muscle tires).

→ We can use code from session 4 + minor changes → they will use llms for changes

### The notebook “S7\_analysis” (4 cells + 1 optional)

| Cell                                | What it does                                                                                                                                                                           | Knobs                                                   |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| 1 Whole S5 ramp                     | Angle vs time for the full recording — the “staircase” (plateau per step, dip per off phase).                                                                                          | File name.                                              |
| 2 Mark the steps                    | Draws vertical lines at entered times; prints the mean angle between each pair. Replaces reading-off-the-screen with a defined measurement.                                            | List of step start/end times, read off the cell-1 plot. |
| 3 Response curve from the recording | Cell-2 means vs step number, for comparison with the hand-drawn S5 curve.                                                                                                              | none                                                    |
| 4 S6 round 1, five repetitions      | The five high-step plateaus overlaid/side by side, mean and highest-to-lowest range printed.                                                                                           | File name, five time windows.                           |
| 5 (optional, fast groups)           | Integrate the pitch rate and plot it over the inclination angle — watch it drift away. No explanation of why; just the picture. *Decision pending: keep in or leave out for clarity.​* | none                                                    |

### Timeline (3 h)

| Time | Block                                                                                                                                                                                                                     | Length |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 0:00 | **Presentation:​** a hand-drawn curve next to a machine-made one from the same data — “what does the second one know that the first one doesn’t?”; the four cells demonstrated on the reference file; knob rule repeated. | 20 min |
| 0:20 | **Run it:​** on the reference file, then on the group’s own S5 ramp.                                                                                                                                                      | 15 min |
| 0:35 | **Read the step times off the plot** and enter them in cell 2 — the slow, valuable part: looking closely at own data to find the plateaus.                                                                                | 30 min |
| 1:05 | **Hand vs machine:​** compare cell-2 means with the hand-written S5 table; note the biggest difference and a guess why.                                                                                                   | 15 min |
| 1:20 | Break                                                                                                                                                                                                                     | 10 min |
| 1:30 | **S6 repetitions:​** run cell 4 on the round-1 file; answer three questions (do the plateaus stay level during “on”; is repetition 5 lower than repetition 1; does the recording show anything the dot plot did not).     | 35 min |
| 2:05 | **Save + optional cell 5;​** slower groups finish; PNGs to the group folder.                                                                                                                                              | 25 min |
| 2:30 | **Closing:​** each group shows one figure and its hand-vs-machine difference.                                                                                                                                             | 30 min |

### Material to be brought by lecturers

* `S7_analysis.ipynb` bundled into the JupyterLite site with reference S5 and S6 files.

* S4 student guide extended by one page for the new notebook (screenshots of the knobs; how to read times off the plot).

* The groups’ S5 and S6 worksheets, returned.

* LLM prompt card (“explain this cell”).

* Backup: reference S5 ramp and S6 round-1 recording (dependency rule).

### Independent work

1. Run the notebook on the reference file, then on own S5 ramp.

2. Read step times off the plot; enter them; get the machine means.

3. Compare with the hand-written table; biggest difference + guessed reason.

4. Run cell 4 on S6 round 1; answer the three questions.

5. Save two PNGs (optional: cell 5).

### Deliverable (per group)

* Two PNGs in the group folder: response curve from the recording; five repetitions overlaid. (These are the raw material for S8–S9.)

* Worksheet: the step-time table entered; biggest hand-vs-machine difference with guessed reason; three answers on the S6 repetitions.

### Open points for S7

* Decide whether optional cell 5 (integration/drift picture) stays in.

​

# Sessions 8–10 — The complex task: “Your experiment, your verdict, your device”

**Responsible**: HiWi for 8-9, WiMi for 10

### The task

Each group runs its own comparison experiment on the S5 setup and takes it to a final talk. Three things are the students’ own: they **choose what to change and why it matters for a patient**, they **predict the outcome before measuring** (as a sketch of the expected figure), and they **say what the result means for a real foot-drop device** and defend it.

### Guardrails that keep it feasible

* Fixed frame: the S5 protocol **plus one changed thing**, measurable with stimulator + imus in \~80 min. At least three repetitions of the key step per condition (S6 lesson).

* An **idea-starter list** of things one could change (electrode distance, position, frequency, pulse width, sensor placement, knee angle, number of repetitions, a pause between them, a second person, skin preparation, …) — no ready-made questions. **Fallback menu** for groups that cannot decide within 30 min (no penalty): (1) 2 cm electrode shift, (2) 20 Hz vs 40 Hz at equal intensity, (3) plateau drop over 15 repetitions and recovery after a 2-min pause, (4) two people at the same steps, (5) imu on instep vs toe.

* The **plan card is initialled by a supervisor** — a feasibility and safety check with a possible “send back” plus a one-sentence steer. Only settings inside the device’s user-programmable range; the S2 rules stay. Supervisors get a short list of “good steers” (questions with no effect or with a trivially large one).

* Analysis stays in the S7 notebook. Two curves on one plot: ask the LLM to adapt cell 3 (S4 skill), with a lecturer-provided “compare two recordings” cell as fallback.

* No inter-group organisation: the dry run and the critical review happen inside the group, with the LLM as devil’s advocate.

* No technical report. The record is: plan card, worksheets, seven slides.

​

## Session 8 —

Question, Prediction, Measurement

### Timeline (3 h)

| Time | Block                                                                                                                                                                                                                                                                                         | Length |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 0:00 | **Presentation:​** the brief (“a company wants a stimulator that works for many patients — what would it need to know?”); the change-one-thing rule; three good and three bad example questions; why you predict before you measure; the idea-starter list; the S10 talk format on one slide. | 20 min |
| 0:20 | **Question + plan card:​** what we change / what we keep the same / what we measure / **why a patient would care** / **prediction as a sketch of the expected figure**. Fallback menu after 30 min.                                                                                           | 40 min |
| 1:00 | **Feasibility check:​** supervisor initials or sends back with one sentence.                                                                                                                                                                                                                  | 10 min |
| 1:10 | **Measure, condition A:​** S5 protocol, ≥ 3 repetitions of the key step.                                                                                                                                                                                                                      | 40 min |
| 1:50 | Break                                                                                                                                                                                                                                                                                         | 10 min |
| 2:00 | **Measure, condition B.​**                                                                                                                                                                                                                                                                    | 40 min |
| 2:40 | **Export + check-in:​** recordings to the group folder (checked); one sentence: “first impression — does it look like our sketch?”                                                                                                                                                            | 20 min |

### Material to be brought by lecturers

* Slide deck (20 min); the idea-starter list; the fallback menu; the “good steers” list for supervisors.

* Plan card (one page: change / keep / measure / patient relevance / prediction sketch grid / supervisor initials).

* Same hardware as S5/S6; the groups’ S5–S7 worksheets and PNGs returned.

* Backup: two lecturer-recorded conditions (e.g. 2 cm shift) for any group whose recordings fail.

### Deliverable (per group)

* Initialled plan card with prediction sketch; recordings of both conditions in the group folder; first-impression sentence.

​

## Session 9

Verdict, Device v2, Rehearsal

### Timeline (3 h)

| Time | Block                                                                                                                                                                                                                                                                        | Length |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 0:00 | **Presentation:​** the seven-slide template; what “what could have fooled us” means (two S6 examples: placement, fatigue); the device-v2 task; how to use the LLM as devil’s advocate.                                                                                       | 15 min |
| 0:15 | **Figure:​** S7 notebook on both conditions; one figure with both curves (LLM adaptation of cell 3 or the fallback cell).                                                                                                                                                    | 40 min |
| 0:55 | **Verdict:​** prediction sketch next to the real figure. Three boxes: what matched / what didn’t / **two things that could have fooled us** (two, not one).                                                                                                                  | 30 min |
| 1:25 | Break                                                                                                                                                                                                                                                                        | 10 min |
| 1:35 | **Device v2:​** the S1 sketch returned. Given what you now know, what must a real device do about the thing you studied? One drawing, three annotations.                                                                                                                     | 25 min |
| 2:00 | **Slides:​** fill the seven-slide template (question & why · prediction · what we did · figure · verdict · what could have fooled us · device v2).                                                                                                                           | 30 min |
| 2:30 | **Rehearsal + devil’s advocate:​** one timed run-through inside the group; then paste question, figure description and verdict into the LLM and ask for the two strongest objections and the one question a critical listener would ask; write the answers on the worksheet. | 25 min |
| 2:55 | **Closing:​** slides and worksheet into the group folder.                                                                                                                                                                                                                    | 5 min  |

### Material to be brought by lecturers

* Slide deck (15 min); the seven-slide template; the devil’s-advocate prompt on the LLM card.

* JupyterLite site with the S7 notebook + fallback “compare two recordings” cell.

* Worksheet: verdict boxes, two fooled-us boxes, device-v2 drawing space, objections + answers box.

* The groups’ S1 sketches, returned.

### Deliverable (per group)

* Seven slides in the group folder; worksheet with verdict, two fooled-us items, objections and answers; device-v2 drawing.

​

## Session 10 —

Final Talks and Wrap-up

### Timeline (3 h)

| Time | Block                                                                                                                                            | Length       |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ |
| 0:00 | Welcome, order of talks, rules (8 min talk + 4 min questions; first question from the lecturers; presenter = someone who has not presented yet). | 10 min       |
| 0:10 | **Talks 1–3.​**                                                                                                                                  | 36 min       |
| 0:46 | Break                                                                                                                                            | 10 min       |
| 0:56 | **Talks 4–5.​**                                                                                                                                  | 24 min       |
| 1:20 | **“What surprised you”​** — one sentence per group.                                                                                              | 10 min       |
| 1:30 | **Then and now:​** S1 sketches pinned next to the device-v2 drawings on a wall; short walk-around.                                               | 20 min       |
| 1:50 | Feedback on the course, course close-out. Reserve for overruns.                                                                                  | up to 70 min |

### Material to be brought by lecturers

* Projector/laptop with all seven-slide decks pre-loaded from the group folders; timer; the S1 sketches and device-v2 drawings; wall space or boards.

### Deliverable (per group)

* Final talk delivered. (Assessable record across the course: one templated group deliverable per session S1–S9 + the talk. Grading vs pass/fail is the lecturers’ call; the structure supports both.)

​
