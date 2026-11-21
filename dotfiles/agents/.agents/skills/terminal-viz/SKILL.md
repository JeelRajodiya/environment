---
name: terminal-viz
description: Explain a topic visually inside the terminal with a colourful, animated ANSI diagram (architecture, data flow, algorithm walk-through, simple charts) drawn by a small Python script the user runs in a split pane. Use whenever the user asks to visualize, diagram, draw, animate, or "show me" how something works or looks, unless they ask for an HTML page, image, or doc instead.
---

# Terminal visualizations

The chat can only show plain text, and your Bash output is never shown to the user. So write a script that draws the visual with ANSI codes, test it yourself, then have the user run it in a pane next to the chat.

1. **Write** `/tmp/claude-viz/<topic>.py`: one file, Python 3 stdlib only. Start from the closest example in this skill's `examples/` dir and copy its helpers (do not import them):
   - `olap_architecture.py`: architecture diagram. Boxes on a character canvas, and each step lights up some components while the rest turn grey. Enter = next step.
   - `hash_join.py`: algorithm walk-through. Tables and a hash table that fill up as an auto-play animation.
2. **Rules**
   - Fit in 78 columns × 38 rows, the size of a half-width pane.
   - Use 24-bit colour (`\033[38;2;R;G;Bm`) with one colour per component. Active parts are bold and coloured, inactive parts are grey.
   - Redraw each frame with `\033[H` + lines joined by `\033[K\n` + `\033[J` so there is no flicker. Hide the cursor and restore it in `finally`.
   - Each step gets a one- or two-sentence caption in plain words.
   - Optional speed argument: none = interactive or default speed, `N` = auto-play at N× the timings, `0` = draw every frame instantly (used for the smoke test).
3. **Smoke test.** Exit code 0, aligned boxes, no line over 78 columns:
   ```sh
   python3 -I /tmp/claude-viz/<topic>.py 0 </dev/null > /tmp/claude-viz/out.txt; echo $?
   python3 -I -c "import re; f=open('/tmp/claude-viz/out.txt').read().split('\x1b[H')[-1]; print(re.sub(r'\x1b\[[0-9;?]*[A-Za-z]','',f))"
   ```
4. **Open it in a split.** In the Herdr desktop app (`herdr-app` is on PATH), open it yourself, using an absolute path:
   ```sh
   herdr-app do pane.split '{"direction":"right","argv":["python3","/tmp/claude-viz/<topic>.py"]}'
   ```
   Without `herdr-app`, tell the user to split the pane to the right and run `python3 /tmp/claude-viz/<topic>.py`.

If the user wants a browser version instead, write one self-contained HTML file and `open` it.
