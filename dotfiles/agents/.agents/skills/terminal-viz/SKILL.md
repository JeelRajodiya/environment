---
name: terminal-viz
description: Explain a topic visually (architecture, data flow, algorithm, comparison, simple chart) as a polished diagram image shown in a Herdr split pane next to the chat. Build it as HTML, render it to PNG with headless Chrome, and display it with the Kitty graphics protocol. Use whenever the user asks to visualize, diagram, draw, or "show me" how something works or looks, unless they ask for a browser page, a file, or a doc instead.
---

# Visual explainers in a Herdr pane

The chat shows only text, and your Bash output is never shown to the user. Draw the visual as HTML, turn it into PNG slides, check them yourself, then open them in a split pane.

1. **Write** `/tmp/claude-viz/<topic>.html`, starting from `examples/olap.html` in this skill's folder.
   - Dark theme and cards with one colour per component. Use real arrows (inline SVG), numbered badges for the flow, and short plain captions.
   - Slides are 1040 CSS px wide and at most ~1000 px tall (portrait, to fit a right split). Put one idea on each slide, such as a diagram slide and a steps slide. Split anything bigger into more slides, because small text is unreadable.
   - Multiple slides go in one file: each slide is a section with an `id`. CSS shows only the `:target` section, and with no `#id` the first one shows. See the example.
2. **Render** each slide:
   ```sh
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
     --force-device-scale-factor=2 --window-size=1040,1000 \
     --screenshot=/tmp/claude-viz/<topic>-1.png "file:///tmp/claude-viz/<topic>.html#<id>" 2>/dev/null
   ```
3. **Check** every PNG with the Read tool. Look for overlaps, clipped text, misplaced badges, and empty space. Fix the HTML and render again.
4. **Show** the slides in a split pane (absolute paths; Enter = next slide, q = quit):
   ```sh
   herdr-app do pane.split '{"direction":"right","argv":["python3","/Users/zeelrajodiya/.claude/skills/terminal-viz/show.py","/tmp/claude-viz/<topic>-1.png","/tmp/claude-viz/<topic>-2.png"]}'
   ```
   Wait about 3 s, run `herdr-app shot /tmp/claude-viz/shot.png`, and Read the screenshot to confirm the image is visible. To replace an old viewer, find its pane ID in `herdr-app ls` and close it with `herdr-app do pane.close '{"pane":"<id>"}'`.

`show.py` calls `kitten icat` with Unicode placeholders, stream transfer and a given window size. Herdr hides the pane's pixel size, so plain `icat` fails there.

Panes can't animate. If the user wants animation, or `herdr-app` is missing, add CSS animations to the HTML and `open` it in the browser.
