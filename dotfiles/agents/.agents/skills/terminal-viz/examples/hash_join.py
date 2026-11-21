#!/usr/bin/env python3
"""Animated hash-join explainer. Run: python3 hash_join.py [speed]  (2 = slower, 0.5 = faster)"""
import sys, time

SPEED = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
R, B, DIM = "\033[0m", "\033[1m", "\033[2m"
def fg(r, g, b): return f"\033[38;2;{r};{g};{b}m"
HL = "\033[48;2;68;71;90m"
BUCKET = [fg(255, 121, 198), fg(139, 233, 253), fg(241, 250, 140), fg(189, 147, 249)]
GREEN, RED, YELLOW, GREY = fg(80, 250, 123), fg(255, 85, 85), fg(255, 184, 108), fg(110, 110, 130)

CUSTOMERS = [(1, "Asha"), (2, "Ben"), (3, "Chen"), (5, "Dia"), (6, "Eli")]
ORDERS = [(101, 1, "$40"), (102, 3, "$15"), (103, 4, "$99"), (104, 1, "$22"), (105, 6, "$70")]
N = 4  # buckets


def seg(parts, width):
    """parts = [(text, style)], padded to width by visible length."""
    plain = "".join(t for t, _ in parts)
    return "".join(s + t + R for t, s in parts) + " " * max(0, width - len(plain))


def draw(s):
    out = [
        seg([(" HASH JOIN ", B + "\033[48;2;189;147;249m\033[38;2;40;42;54m"),
             ("  orders ⋈ customers ON cust_id", B)], 0),
        seg([(s["step"], GREY)], 0), "",
        seg([("customers (build)", B)], 22) + seg([(f"hash table  key % {N}", B)], 34) + seg([("orders (probe)", B)], 0),
    ]
    for k in range(max(len(CUSTOMERS), N, len(ORDERS))):
        left = mid = right = seg([], 0)
        if k < len(CUSTOMERS):
            cid, name = CUSTOMERS[k]
            active = k == s["c"]
            st = (HL + B if active else DIM if k in s["built"] else "") + BUCKET[cid % N]
            left = seg([(f" {cid:<2} {name:<5}", st), (" ──▶" if active else "", YELLOW)], 22)
        else:
            left = " " * 22
        if k < N:
            st = HL + B if k == s["bucket"] else ""
            parts = [(f"[{k}] ", st + BUCKET[k])]
            for i in s["built"]:
                cid, name = CUSTOMERS[i]
                if cid % N == k:
                    parts.append((f" {cid}:{name} ", st + BUCKET[k]))
            mid = seg(parts, 34)
        else:
            mid = " " * 34
        if k < len(ORDERS):
            oid, cid, amt = ORDERS[k]
            active = k == s["o"]
            st = HL + B if active else DIM if k in s["probed"] else ""
            right = seg([("◀── " if active else "    ", YELLOW), (f"#{oid} cust={cid} {amt}", st + BUCKET[cid % N])], 0)
        out.append(left + mid + right)
    out += ["", seg([("result", B)], 0)]
    for ok, text in s["results"]:
        out.append(seg([("  ✓ " if ok else "  ✗ ", GREEN if ok else RED), (text, "" if ok else DIM)], 0))
    out += ["", seg([("» " + s["caption"], YELLOW + B)], 0)]
    sys.stdout.write("\033[H" + "\033[K\n".join(out) + "\033[K\n\033[J")
    sys.stdout.flush()


def show(s, secs, **kw):
    s.update(kw)
    draw(s)
    time.sleep(secs * SPEED)


def run():
    s = dict(step="", caption="", c=None, o=None, bucket=None, built=[], probed=[], results=[])
    show(s, 3, step="Goal", caption="Attach the customer name to every order, without comparing every pair.")

    for k, (cid, name) in enumerate(CUSTOMERS):
        show(s, 1.4, step="Step 1/2  BUILD: load the smaller table into a hash table", c=k, bucket=cid % N,
             caption=f"hash({cid}) = {cid} % {N} = {cid % N}  →  put {name} in bucket {cid % N}")
        s["built"].append(k)
        show(s, 0.4)
    show(s, 2.5, c=None, bucket=None, caption="Build done. Finding a customer now means looking in ONE bucket, not scanning all.")

    for j, (oid, cid, amt) in enumerate(ORDERS):
        show(s, 1.4, step="Step 2/2  PROBE: stream the other table, look up each key", o=j, bucket=cid % N,
             caption=f"order #{oid}: hash({cid}) = {cid % N}  →  check only bucket {cid % N}")
        match = next((n for c, n in CUSTOMERS if c == cid), None)
        if match:
            s["results"].append((True, f"#{oid}  {amt}  →  {match}"))
            cap = f"found customer {cid} ({match}) in bucket {cid % N}  →  emit joined row"
        else:
            s["results"].append((False, f"#{oid}  cust={cid}: no match, dropped (inner join)"))
            cap = f"bucket {cid % N} has no customer {cid}  →  inner join drops this order"
        s["probed"].append(j)
        show(s, 1.6, caption=cap)

    show(s, 0, o=None, bucket=None, step="Done",
         caption=f"Each row read once: O(n + m). A nested loop would do {len(ORDERS)} × {len(CUSTOMERS)} = {len(ORDERS) * len(CUSTOMERS)} comparisons.")


if __name__ == "__main__":
    sys.stdout.write("\033[?25l\033[2J")
    try:
        while True:
            run()
            sys.stdout.write("\n" + GREY + "Enter = replay   q + Enter = quit" + R + " ")
            sys.stdout.flush()
            if input().strip().lower() == "q":
                break
            sys.stdout.write("\033[2J")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        sys.stdout.write("\033[?25h" + R + "\n")
