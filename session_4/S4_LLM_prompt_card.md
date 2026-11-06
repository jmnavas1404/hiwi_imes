# Session 4: LLM prompt card

Use a free chat assistant in your browser. Copy a prompt, replace the text in [square brackets], and send it.
Always paste the WHOLE cell, including the comments at the top.

---

## Prompt 1: Explain this cell

```
I am a first-year biomedical engineering student with no programming experience. Below is one cell from a Jupyter notebook that plots sensor data using pandas and matplotlib.

Explain what this cell does to a complete beginner, in plain language and in no more than 6 short sentences. Explain any technical word you use. Then tell me which lines are inside the "YOU MAY CHANGE THIS" box and what each of them controls. Do not rewrite or change the code.

[paste the whole cell here]
```

## Prompt 2: I got an error

```
I am a beginner running a Jupyter notebook in my browser (JupyterLite, Python with pandas and matplotlib). I ran the cell below and got an error.

Tell me in plain language: (1) what the error means, (2) which line caused it, and (3) exactly what I should change. If the fix is possible inside the "YOU MAY CHANGE THIS" box, only change something there. Show the corrected line, not a lecture.

Cell:
[paste the whole cell here]

Error message (copy the last lines):
[paste the error here]
```

## Prompt 3: Change one thing

```
Below is a Jupyter notebook cell that I must not break. Make exactly this one change: [describe it, for example "make the line red and thicker" or "add a grid"].

Rules:
- Use only pandas and matplotlib. Do not install anything.
- Do not rename any variable.
- Keep all comments and the "YOU MAY CHANGE THIS" box exactly as they are.
- Change as little as possible.

Give me the full cell back in one code block that I can paste over the old cell. After the code, write one sentence saying which line you changed.

[paste the whole cell here]
```
