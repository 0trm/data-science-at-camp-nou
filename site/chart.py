# Fig. 6 redrawn for the page: the README's Excel chart, as lines that follow the page's theme.
# The values are traced from images/a-simplified-graph-explaining-the-problem-smartbooking-solves.webp,
# one per day and rounded to 100 seats; the original is a simplified graph, so they are its shape, not data.

# %%
DAYS = list(range(-61, 1))  # days before the match; 0 is match day
SERIES = {
    "sold": [
        1500, 5400, 6300, 6700, 6900, 7100, 7300, 7600, 7700, 7900, 8200, 8400, 8500, 8700, 8800, 8800,
        *[8900] * 27, *[9000] * 8,
        9300, 13200, 14200, 14700, 15300, 17100, 19700, 22500, 24900, 28100, 30500,
    ],
    "released": [
        8700, 8700, 8800, 8800, 8800, 8800, 8900, 8900, 8900, 9000, 9000, 9100, 9100, 9200, 9300, 9400,
        9400, 9400, 9500, 9600, 9600, 9700, 9700, 9800, 9900, 9900, 10000, 10000, 10100, 10200, 10300, 10300,
        10500, 10500, 10600, 10700, 10800, 10900, 10900, 11000, 11000, 11000, 11100, 11300, 11400, 11500, 11700, 11800,
        11900, 12100, 12400, 12700, 13000, 13500, 13900, 14500, 16100, 18200, 23700, 26700, 30900, 38100,
    ],
    "model": [*[25000] * 57, 25200, 28100, 30900, 36000, 41100],
}
assert all(len(values) == len(DAYS) for values in SERIES.values())
TOP = 45000  # seats at the top of the plot
# Each line's name sits on the flat stretch, where the lines are far apart: (series, day, seats, above or below the line)
LABELS = [
    ("model", -60, 25000, "above", "Predictive model"),
    ("released", -40, 11600, "above", "Seats released"),
    ("sold", -40, 8300, "below", "Seats sold"),
]


def x(day):
    return (day + 61) / 61 * 100


def y(seats):
    return (1 - seats / TOP) * 100


# %%
def fig6():
    # The SVG stretches to the plot's box, so its units are percent of it; the text is HTML, so it keeps its size on phones
    grid = "".join(
        f'<line class="{"base" if s == 0 else "grid"}" x1="0" x2="100" y1="{y(s):.2f}" y2="{y(s):.2f}"/>'
        for s in range(0, TOP, 10000)
    )
    lines = "".join(
        f'<polyline class="{name}" points="{" ".join(f"{x(d):.2f},{y(v):.2f}" for d, v in zip(DAYS, values))}"/>'
        for name, values in SERIES.items()
    )
    yticks = "".join(
        f'<span class="y" style="top:{y(s):.2f}%">{s // 1000}k</span>' if s else f'<span class="y" style="top:100%">0</span>'
        for s in range(0, TOP, 10000)
    )
    xticks = "".join(f'<span class="x" style="left:{x(-d):.2f}%">{d}</span>' for d in range(60, -1, -10))
    labels = "".join(
        f'<span class="lab {name} {side}" style="left:{x(d):.2f}%;top:{y(s):.2f}%">{text}</span>'
        for name, d, s, side, text in LABELS
    )
    summary = (
        "Line chart of seats over the 61 days before a match. Seats released and seats sold stay between "
        "about 9,000 and 11,000 until ten days before, then climb to about 38,000 and 30,000 on match day. "
        "The predictive model expects 25,000 seats from the start, rising to about 41,000."
    )
    return (
        '<div class="chart">'
        '<p class="title">Seats sold vs. seats released, cumulative</p>'
        f'<div class="plot"><svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="{summary}">'
        f"{grid}{lines}</svg>{yticks}{xticks}{labels}</div>"
        '<p class="xtitle">Days before the match</p>'
        "</div>"
    )
