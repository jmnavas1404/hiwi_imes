# Sessions Notes
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

