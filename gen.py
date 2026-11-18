#!/usr/bin/env python3
"""Writes banner.svg: "Petyok" in contribution-graph cells, with real Game of Life
patterns (lightweight spaceships, pulsars) running around it. Run: python gen.py"""
import random

W, H, CELL, SIZE = 120, 30, 10, 8  # grid in cells, pitch and square size in px
T = 0.2  # seconds per generation
GREENS = ["#26a641", "#30a14e", "#40c463", "#39d353"]  # readable on light and dark

FONT = {
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "e": ["00000", "00000", "01110", "10001", "11111", "10000", "01110"],
    "t": ["01000", "01000", "11100", "01000", "01000", "01001", "00110"],
    "y": ["00000", "00000", "10001", "10001", "01111", "00001", "01110"],
    "o": ["00000", "00000", "01110", "10001", "10001", "10001", "01110"],
    "k": ["10000", "10000", "10010", "10100", "11000", "10100", "10010"],
}
LWSS = [".O..O", "O....", "O...O", "OOOO."]
PULSAR_Q = [(2, 1), (3, 1), (4, 1), (1, 2), (1, 3), (1, 4), (6, 2), (6, 3), (6, 4), (2, 6), (3, 6), (4, 6)]


def cells(rows):
    return {(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c in "1O"}


def step(live):
    n = {}
    for x, y in live:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    n[x + dx, y + dy] = n.get((x + dx, y + dy), 0) + 1
    return {c for c, k in n.items() if k == 3 or (k == 2 and c in live)}


def phases(live, period):
    out = [live]
    for _ in range(period):
        out.append(step(out[-1]))
    return out[:-1], out[-1]


def rects(live, fill=None):
    f = f' fill="{fill}"' if fill else ""
    return "".join(
        f'<rect x="{x * CELL + 1}" y="{y * CELL + 1}" width="{SIZE}" height="{SIZE}" rx="2"{f}/>'
        for x, y in sorted(live)
    )


def oscillate(frames):
    """Frames shown one generation each, looping."""
    p = len(frames)
    return "".join(
        f'<g class="ph{p}" style="animation-delay:{(i - p) * T:g}s">{rects(f)}</g>'
        for i, f in enumerate(frames)
    )


def main():
    rng = random.Random(7)
    out = []

    # the name, each font pixel doubled
    word = "Petyok"
    x0, y0 = (W - (len(word) * 6 - 1) * 2) // 2, (H - 14) // 2
    text = set()
    for i, ch in enumerate(word):
        for x, y in cells(FONT[ch]):
            for a in (0, 1):
                for b in (0, 1):
                    text.add((x0 + (i * 6 + x) * 2 + a, y0 + y * 2 + b))
    out.append("".join(rects({c}, rng.choice(GREENS)) for c in sorted(text)))

    # pulsars left and right of the name (period 3)
    q = set(PULSAR_Q)
    pulsar = {(sx * x, sy * y) for x, y in q for sx in (1, -1) for sy in (1, -1)}
    frames, back = phases(pulsar, 3)
    assert back == pulsar
    for cx in (12, W - 13):
        out.append(f'<g transform="translate({cx * CELL} {(H // 2 - 1) * CELL})" fill="#30a14e">{oscillate(frames)}</g>')

    # lightweight spaceships above and below: period 4, two cells per period
    ship = cells(LWSS)
    frames, back = phases(ship, 4)
    dx = min(x for x, _ in back) - min(x for x, _ in ship)
    assert abs(dx) == 2 and back == {(x + dx, y) for x, y in ship}
    steps = (W + 10) // 2
    loop = steps * 4 * T
    for row, right in ((1, True), (H - 6, False)):
        flip = (dx > 0) != right  # mirror the ship when the lane runs the other way
        body = oscillate([{(4 - x if flip else x, y) for x, y in f} for f in frames])
        start = -6 if right else W + 1
        for k in (0, steps // 3, 2 * steps // 3):
            out.append(
                f'<g transform="translate({start * CELL} {row * CELL})" fill="#39d353">'
                f'<g class="{"mr" if right else "ml"}" style="animation-duration:{loop:g}s;'
                f'animation-delay:{-k * 4 * T:g}s">{body}</g></g>'
            )

    dist = steps * 2 * CELL
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W * CELL} {H * CELL}" role="img" aria-label="Petyok">
<style>
.ph3{{opacity:0;animation:ph3 {3 * T:g}s steps(1) infinite}}
.ph4{{opacity:0;animation:ph4 {4 * T:g}s steps(1) infinite}}
.mr{{animation:mr steps({steps}) infinite}}
.ml{{animation:ml steps({steps}) infinite}}
@keyframes ph3{{0%{{opacity:1}}33.3333%{{opacity:0}}}}
@keyframes ph4{{0%{{opacity:1}}25%{{opacity:0}}}}
@keyframes mr{{to{{transform:translate({dist}px)}}}}
@keyframes ml{{to{{transform:translate(-{dist}px)}}}}
</style>
<defs><pattern id="g" width="{CELL}" height="{CELL}" patternUnits="userSpaceOnUse"><rect x="1" y="1" width="{SIZE}" height="{SIZE}" rx="2" fill="#8b949e" fill-opacity=".13"/></pattern></defs>
<rect width="100%" height="100%" fill="url(#g)"/>
{chr(10).join(out)}
</svg>
"""
    open("banner.svg", "w").write(svg)
    print(f"banner.svg: {len(svg) / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
