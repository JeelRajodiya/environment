#!/usr/bin/env python3
"""OLAP database architecture and query flow, step by step.

python3 olap_architecture.py      Enter = next step, q = quit
python3 olap_architecture.py 1    auto-play (2 = slower, 0.5 = faster, 0 = instant smoke test)
"""
import sys, time, textwrap

AUTO = len(sys.argv) > 1
SPEED = float(sys.argv[1]) if AUTO else 1.0
R, B = "\033[0m", "\033[1m"
def fg(r, g, b): return f"\033[38;2;{r};{g};{b}m"
CYAN, PURPLE, ORANGE, GREEN = fg(139, 233, 253), fg(189, 147, 249), fg(255, 184, 108), fg(80, 250, 123)
YELLOW, PINK, RED, GREY = fg(241, 250, 140), fg(255, 121, 198), fg(255, 85, 85), fg(98, 98, 120)

# colour per component key; a step lights up a set of keys, the rest turn grey
COLOR = {"client": CYAN, "l_client": CYAN,
         "coord": PURPLE, "parser": PURPLE, "analyzer": PURPLE, "optimizer": PURPLE, "scheduler": PURPLE,
         "catalog": ORANGE, "l_cat": ORANGE, "l_work": PINK, "exch": PINK,
         "w": GREEN, "scan": GREEN, "filter": GREEN, "agg": GREEN, "bar": GREEN, "cache": GREEN,
         "l_store": YELLOW, "storage": YELLOW, "keep": YELLOW, "prune": RED, None: ""}
W, H = 78, 23


def put(c, x, y, s, key):
    for i, ch in enumerate(s):
        c[y][x + i] = (ch, key)


def box(c, x, y, w, h, title, key):
    put(c, x, y, "┌─ " + title + " " + "─" * (w - 5 - len(title)) + "┐", key)
    for r in range(1, h - 1):
        put(c, x, y + r, "│", key)
        put(c, x + w - 1, y + r, "│", key)
    put(c, x, y + h - 1, "└" + "─" * (w - 2) + "┘", key)


def chain(c, x, y, keys, sep_key):
    """'a ▶ b ▶ c' where each word has its own key."""
    for i, k in enumerate(keys):
        if i:
            put(c, x, y, " ▶ ", sep_key)
            x += 3
        put(c, x, y, k, k)
        x += len(k)


def diagram(s):
    c = [[(" ", None)] * W for _ in range(H)]
    box(c, 0, 0, 76, 3, "CLIENT", "client")
    put(c, 2, 1, "BI dashboard · SQL editor · notebook", "client")
    put(c, 27, 3, "│", "l_client")
    put(c, 29, 3, "SQL ↓   result ↑", "l_client")

    box(c, 0, 4, 54, 3, "COORDINATOR", "coord")
    chain(c, 2, 5, ["parser", "analyzer", "optimizer", "scheduler"], "coord")
    put(c, 54, 5, "◀──▶", "l_cat")
    box(c, 58, 4, 18, 4, "CATALOG", "catalog")
    put(c, 60, 5, "schemas, files", "catalog")
    put(c, 60, 6, "min/max stats", "catalog")

    put(c, 27, 7, "│", "l_work")
    put(c, 30, 7, "plan fragments", "l_work")
    put(c, 12, 8, "┌" + "─" * 51 + "┐", "l_work")
    put(c, 27, 8, "┴", "l_work")
    put(c, 38, 8, "┬", "l_work")
    for x in (12, 38, 64):
        put(c, x, 9, "▼", "l_work")

    for i, wx in enumerate((0, 26, 52)):
        box(c, wx, 10, 24, 6, f"WORKER {i + 1}", "w")
        chain(c, wx + 2, 11, ["scan", "filter", "agg"], "w")
        b = s["bars"][i]
        put(c, wx + 2, 12, "▰" * b + "▱" * (10 - b) + f" {b * 10:>3}%", "bar")
        put(c, wx + 2, 13, "◆ local SSD cache", "cache")
        put(c, wx + 2, 14, s["wtext"][i][:20], "w")

    put(c, 0, 16, "◀" + " shuffle / exchange by hash(region) ".center(74, "─") + "▶", "exch")
    for x in s["dots"]:
        put(c, x, 16, "●", "exch")
    for x in (12, 38, 64):
        put(c, x, 17, "▲", "l_store")
    put(c, 14, 17, "only 3 of 40 columns", "l_store")

    box(c, 0, 18, 76, 5, "OBJECT STORAGE · S3 / GCS / ADLS", "storage")
    put(c, 2, 19, "partitions", "storage")
    put(c, 13, 19, "[2026-11-01] [11-02] … [11-30]", "keep")
    put(c, 45, 19, "[2025-12 … 2026-10]", "prune")
    put(c, 2, 20, "columns", "storage")
    put(c, 13, 20, "[date] [region] [amount]", "keep")
    put(c, 38, 20, "[cust_id] [sku] [price] … +34", "prune")
    put(c, 2, 21, "Parquet/ORC files · compressed per column · min/max stats per file", "storage")
    return c


def render(s):
    act = s["active"]  # None = overview, everything in colour
    lines = [B + "\033[48;2;189;147;249m\033[38;2;40;42;54m OLAP DATABASE " + R + B + "  architecture & query flow" + R,
             GREY + s["step"] + R, ""]
    for row in diagram(s):
        out, prev = "", object()
        for ch, key in row:
            if key != prev:
                out += R + (COLOR[key] if act is None or key is None else B + COLOR[key] if key in act else GREY)
                prev = key
            out += ch
        lines.append(out + R)
    lines.append("")
    if s["sql"]:
        lines += [CYAN + "  SELECT region, SUM(amount) FROM sales" + R,
                  CYAN + "  WHERE date >= '2026-11-01' GROUP BY region" + R]
    if s["result"]:
        lines += [GREEN + B + "  region   SUM(amount)" + R] + [GREEN + f"  {r:<8} {v:>11}" + R for r, v in
                  [("US", "2,981,004"), ("EU", "1,204,330"), ("APAC", "877,120"), ("LATAM", "310,442")]]
    lines.append("")
    lines += [YELLOW + B + ("» " if i == 0 else "  ") + t + R for i, t in enumerate(textwrap.wrap(s["caption"], 74))]
    sys.stdout.write("\033[H" + "\033[K\n".join(lines) + "\033[K\n\033[J")
    sys.stdout.flush()


def frame(s, **kw):
    s.update(kw)
    render(s)


def tick(s, secs, **kw):
    frame(s, **kw)
    time.sleep(secs * (SPEED if AUTO else 1))


def pause():
    if AUTO:
        time.sleep(5 * SPEED)
        return
    sys.stdout.write(GREY + "  Enter = next · q = quit " + R)
    sys.stdout.flush()
    if input().strip().lower() == "q":
        raise KeyboardInterrupt


def run():
    s = dict(step="Overview", active=None, bars=[0, 0, 0], wtext=["", "", ""], dots=[], sql=False, result=False,
             caption="OLAP = analytics on huge data: few queries, but each one scans millions or billions of rows. "
                     "Storage and compute are separate: data sits in cheap object storage, workers scale up and down.")
    frame(s)
    pause()
    frame(s, step="1/8 · Client sends SQL", active={"client", "l_client"}, sql=True,
          caption="A dashboard sends one SQL query to the coordinator, the brain of the cluster.")
    pause()
    frame(s, step="2/8 · Parse & analyze", active={"coord", "parser", "analyzer", "catalog", "l_cat"},
          caption="Parser turns the text into a tree. Analyzer asks the catalog: does table `sales` exist? "
                  "Which columns, which types, which files?")
    pause()
    frame(s, step="3/8 · Optimize", active={"coord", "optimizer", "catalog", "l_cat", "storage", "keep", "prune"},
          caption="Optimizer uses catalog stats to prune: read only November partitions and only 3 of 40 columns. "
                  "The red parts are never read.")
    pause()
    frame(s, step="4/8 · Schedule", active={"coord", "scheduler", "l_work", "w"},
          wtext=["files 1-40", "files 41-80", "files 81-120"],
          caption="Scheduler cuts the plan into fragments and gives each worker its own slice of files. "
                  "All workers run in parallel (MPP).")
    pause()
    s.update(step="5/8 · Scan", active={"w", "scan", "bar", "cache", "l_store", "storage", "keep"},
             caption="Each worker reads only the needed columns, straight from object storage. "
                     "Hot files come from the local SSD cache, so repeat queries are faster.")
    t, rates = 0, (0.8, 0.55, 0.65)
    while min(s["bars"]) < 10:
        t += 1
        bars = [min(10, int(t * r)) for r in rates]
        tick(s, 0.12, bars=bars, wtext=[f"{b * 41}M rows read" for b in bars])
    pause()
    frame(s, step="6/8 · Filter & partial aggregate", active={"w", "filter", "agg"},
          wtext=["410M rows → 4 sums"] * 3,
          caption="Vectorized execution: each operator works on a batch of ~1024 values at once. "
                  "Each worker keeps November rows and sums amount per region locally.")
    pause()
    s.update(step="7/8 · Exchange", active={"w", "exch"}, wtext=["owns US", "owns EU", "owns APAC, LATAM"],
             caption="Partial sums are shuffled by hash(region), so all sums for one region meet on one worker, "
                     "which adds them up: the final SUM.")
    for t in range(40):
        tick(s, 0.06, dots=[1 + (x + 2 * t) % 74 for x in (12, 38, 64)])
    frame(s, dots=[])
    pause()
    frame(s, step="8/8 · Result", active={"coord", "client", "l_client", "l_work"}, sql=False, result=True,
          caption="Only 4 tiny rows go back to the client. Why OLAP is fast: columnar files, pruning, "
                  "parallel workers, vectorized execution.")


if __name__ == "__main__":
    sys.stdout.write("\033[?25l\033[2J")
    try:
        while True:
            run()
            sys.stdout.write("\n" + GREY + "  Enter = replay · q = quit" + R + " ")
            sys.stdout.flush()
            if input().strip().lower() == "q":
                break
            sys.stdout.write("\033[2J")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        sys.stdout.write("\033[?25h" + R + "\n")
