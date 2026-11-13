# Session 4: LLM prompt card (v2)

Use a free chat assistant in your browser. Copy a prompt, replace the text in [square brackets], and send it.

**Which prompts do I use?**
- **Simple notebook:** Prompts 1, 2 and 3.
- **Advanced notebook:** Prompts 4, 5 and 6.

---

## Before you paste anything (read once)

1. **Paste the WHOLE cell**, including the comments at the top. The comments tell the assistant what is allowed to change.
2. **Paste the error from the last lines of the red message**, not just the cell.
3. **Never paste your CSV or personal data** (names, health information, file contents). The assistant only needs the code and the error. If it asks for data, describe it instead: "a table with a time column in seconds and six numeric columns".
4. **The assistant can be wrong.** Always run what it gives you. If it fails, paste the new error back (Prompt 2 or 6).
5. **Your notebook runs in the browser (JupyterLite).** Ignore any advice that says to install something (`pip install`), use Google Colab, or open files from a computer path. Only pandas, numpy and matplotlib are available.
6. **Understand before you paste.** The worksheet asks you to explain in your own words what a cell does or what you changed.

---

## Prompt 1: Explain this cell (both notebooks)

```
I am a first-year biomedical engineering student with no programming experience. Below is one cell from a Jupyter notebook that plots sensor data using pandas and matplotlib.

Explain what this cell does to a complete beginner, in plain language and in no more than 6 short sentences. Explain any technical word you use. Then tell me which lines I am allowed to change (the ones inside the "YOU MAY CHANGE THIS" or "PARÁMETROS" box, or marked "TU CÓDIGO") and what each of them controls. Do not rewrite or change the code.

[paste the whole cell here]
```

---

## Prompt 2: I got an error (simple notebook)

```
I am a beginner running a Jupyter notebook in my browser (JupyterLite, Python with pandas and matplotlib). I ran the cell below and got an error.

Tell me in plain language: (1) what the error means, (2) which line caused it, and (3) exactly what I should change. If the fix is possible inside the "YOU MAY CHANGE THIS" box, only change something there. If the cause might be an earlier cell that I did not run or a wrong file/column name, say so. Show the corrected line, not a lecture.

Cell:
[paste the whole cell here]

Error message (copy the last lines):
[paste the error here]
```

---

## Prompt 3: Change one thing (simple notebook)

```
Below is a Jupyter notebook cell that I must not break. Make exactly this one change: [describe it, for example "make the line red and thicker" or "add a grid"].

Rules:
- Use only pandas, numpy and matplotlib. Do not install anything.
- Do not rename any variable.
- Do not change the values inside the "YOU MAY CHANGE THIS" box.
- Keep all comments and the "YOU MAY CHANGE THIS" box exactly as they are.
- Change as little as possible.

Give me the full cell back in one code block that I can paste over the old cell. After the code, write one sentence saying which line you changed.

[paste the whole cell here]
```

---

# Advanced notebook only

In the advanced notebook you write parts of the code yourself. These prompts ask the assistant to **teach and give hints, not to do the task for you**.

## Prompt 4: Give me a hint (I am stuck on a ✏️ task)

```
I am a first-year biomedical engineering student learning Python (pandas, numpy, matplotlib) in a Jupyter notebook. Below is a cell with a task marked "TU CÓDIGO". I have to write that part myself.

Do NOT give me the solution. Instead:
1. Tell me in one or two sentences what the task is asking for, in plain language.
2. Name the function(s) or concept(s) I should look up, and what each one does.
3. Give me a tiny example with different, unrelated data (not my variables).
4. Then stop and let me try. If I answer "more help", give a bigger hint, but still not the final line.

Task number I am working on: [for example 1.c or 4.a]

[paste the whole cell here]
```

## Prompt 5: Explain a function or a line

```
I am a beginner learning Python for biomedical data. Explain the following line (or function) from my notebook:

[paste the line or function, for example: data[COLUMN_NAME].rolling(window=25, center=True).mean()]

Please:
- Say what it does in plain language, one short paragraph.
- Explain each argument and what happens if I change it (for example, what changes if the number gets bigger).
- Say what type of thing it returns (a number, a list, a table, a plot).
- Give one small example using made-up numbers, with the result.
- Tell me the name of the official documentation page I can look up (pandas, numpy or matplotlib).
```

## Prompt 6: My code gives an error or a wrong result

```
I am a beginner learning Python (pandas, numpy, matplotlib) in a Jupyter notebook running in my browser (JupyterLite). I wrote part of the code in the cell below (the lines marked "TU CÓDIGO"). It does not work.

What I expected: [describe in one sentence, for example "a plot of 10 seconds of signal_1"]
What happened: [describe, for example "empty plot", "wrong numbers", or paste the error's last lines]

Please:
1. Tell me in plain language what is wrong and on which line.
2. Explain WHY it is wrong, so I do not repeat the mistake.
3. Give me a hint for the fix, not the corrected code. Only show the corrected line if I answer "show me".
4. Do not change anything outside the lines marked "TU CÓDIGO".

Cell:
[paste the whole cell here]
```

---

## After the assistant answers: 3-point check

1. **Run it.** Does it work? If not, paste the new error (Prompt 2 or 6).
2. **Can you explain it?** Say in your own words what each new line does. If you cannot, ask Prompt 5 about that line.
3. **Is the result plausible?** Do the axes have the right label and unit? Does the time window show what you expect? A plot that runs without errors can still be wrong.

## Things that usually go wrong

- Asking "fix my code" without the error or the full cell: the assistant will guess.
- Accepting a long answer that renames variables or deletes comments: ask again with the rules of Prompt 3.
- Following advice to install packages or change the kernel: not possible in this setup.
- Copying code you do not understand into the worksheet: the worksheet asks you to explain it.
