# 01. Choose the Chart by the Question
# 02. Comparison: Sorted Bars from Zero
# 03. Pie Chart Pitfalls
# 04. 3D Pitfalls
# 05. Dual-Axis Pitfalls
# 06. Color: Sequential, Diverging, Categorical
# 07. Colorblind-Safe Palettes
# 08. Accessibility
# 09. Labels, Units and Annotations
# 10. Small Multiples
# 11. Data-Ink and Decluttering
# 12. Reusable Plot Helpers Returning (fig, ax)
# 13. A Style Guide Dict with rc_context
# 14. Testing Plots Instead of Eyeballing
# 15. Before/After: Truncated Axis
# 16. Before/After: Spaghetti and Overplotting
# 17. Pre-Publish Checklist

import os
os.environ.setdefault("MPLBACKEND", "Agg")   # headless; in Jupyter the inline backend is already set

import io
import warnings

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import proj3d

# plt.show() under Agg only warns "cannot be shown"; silence just that message
warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive")

rng = np.random.default_rng(3)

# 01. Choose the Chart by the Question
# ------------------------------------
# - Start from the QUESTION, not the chart type:
#     Comparison   "which is bigger?"          -> bar / dot plot (sorted)
#     Trend        "how did it change?"        -> line (ordered x, usually time)
#     Distribution "what is the spread/shape?" -> histogram, box, violin, ECDF
#     Relationship "do x and y move together?" -> scatter (+ trend line), heatmap of correlations
#     Composition  "what share is each part?"  -> stacked bar, 100% bar (pie only for 2-3 parts)
#     Geography / flow / network have their own specialised charts.
# - One chart = one message. Write the message as the title.
# - If you cannot say the question in one sentence, split the chart.

CHOICES = {
    "comparison": "bar",
    "trend": "line",
    "distribution": "hist",
    "relationship": "scatter",
    "composition": "stacked bar",
}
for question, chart in CHOICES.items():
    print(f"{question:12s} -> {chart}")

# 02. Comparison: Sorted Bars from Zero
# ------------------------------------
# - Bars encode value by LENGTH, so they must start at ZERO. A cut axis
#   makes small differences look huge (see section 15).
# - Sort by value (unless categories have a natural order such as months).
# - Use horizontal bars for long names; label the values directly.
# - Many categories or you only care about position? A dot plot (scatter on
#   a category axis) can start anywhere.

names = np.array(["Alpha", "Bravo", "Charlie", "Delta"])
vals = np.array([23, 41, 17, 35])
order = np.argsort(vals)
fig, ax = plt.subplots()
ax.barh(names[order], vals[order])
print("bars drawn in order of value:", [p.get_width() for p in ax.patches])
print("axis starts at zero:", ax.get_xlim()[0] <= 0)
plt.close(fig)

# 03. Pie Chart Pitfalls
# ------------------------------------
# - People compare angles and areas badly; with 5+ slices or similar sizes
#   a pie is unreadable. Colours also have to be matched to a legend.
# - Use a sorted bar chart instead; keep a pie only for 2-3 parts of a clear
#   whole (e.g. "yes / no").
# - Demo: shares of 27% vs 25% differ by only ~7 degrees of arc but are an
#   easy-to-read 2-point gap on a bar.

shares = np.array([27, 25, 24, 14, 10])
fig, ax = plt.subplots()
wedges, _ = ax.pie(shares)
angles = [w.theta2 - w.theta1 for w in wedges]
print("wedge angles (deg):", [round(a, 1) for a in angles])
print("27% vs 25% gap in degrees:", round(angles[0] - angles[1], 1))
plt.close(fig)

# 04. 3D Pitfalls
# ------------------------------------
# - A 3D bar/surface is rendered through a PROJECTION: the same data value
#   lands at different screen positions depending on the viewing angle, and
#   front bars hide back bars. You cannot read exact values.
# - Never use 3D for what 2D shows (bars, pies, lines). It is justified only
#   when the 3D SHAPE is the point (physical surfaces, terrain) - and then
#   offer a contour/heatmap too.
# - Demo: project the same data point under two viewing elevations.

fig = plt.figure()
ax3 = fig.add_subplot(projection="3d")
ys = []
for elev in (10, 60):
    ax3.view_init(elev=elev, azim=30)
    fig.canvas.draw()
    x2, y2, _ = proj3d.proj_transform(0.5, 0.5, 1.0, ax3.get_proj())
    ys.append(round(float(y2), 3))
print("same point, projected y at elev 10 vs 60:", ys, "| differ:", ys[0] != ys[1])
plt.close(fig)

# 05. Dual-Axis Pitfalls
# ------------------------------------
# - With twinx() the two y-ranges are chosen by YOU. Change one range and
#   lines cross, diverge or appear correlated at will.
# - Demo: same data, two arbitrary right-hand limits -> the vertical position
#   of series B (in axes fractions) changes a lot.
# - Alternatives: two stacked panels sharing x (small multiples), or index
#   both series to 100 at the start, or plot the ratio.
# - If you must use dual axes: colour each axis to match its line, state units.

b = np.array([10.0, 12.0, 15.0])
def frac(v, lo, hi):
    return [round(float((t - lo) / (hi - lo)), 2) for t in v]
print("B at limits (0, 20):  ", frac(b, 0, 20))
print("B at limits (8, 16):  ", frac(b, 8, 16))
fig, (top, bottom) = plt.subplots(2, 1, sharex=True)
top.plot([0, 1, 2], [1, 2, 3])
bottom.plot([0, 1, 2], b)
print("alternative: two stacked panels sharing x ->", len(fig.axes), "axes, x shared:",
      top.get_shared_x_axes().joined(top, bottom))
plt.close(fig)

# 06. Color: Sequential, Diverging, Categorical
# ------------------------------------
# - Sequential (low -> high, one hue light to dark): viridis, Blues. Use for
#   ordered magnitudes (counts, density).
# - Diverging (two hues meeting at a neutral midpoint): RdBu, coolwarm. Use
#   when the midpoint MEANS something (zero change, average). Pair with
#   TwoSlopeNorm / center=0.
# - Categorical (distinct hues, no order): tab10, Okabe-Ito. Keep to ~7
#   categories or fewer.
# - Do not use a rainbow (jet) for numbers: false boundaries, not uniform.
# - One colour = one meaning, across all charts in a report.

for name, kind in [("viridis", "sequential"), ("RdBu", "diverging"), ("tab10", "categorical")]:
    cm = matplotlib.colormaps[name]
    print(f"{kind:11s} {name:8s} N={cm.N:3d} start={mcolors.to_hex(cm(0.0))} end={mcolors.to_hex(cm(0.999))}")

def luminance(c):
    r, g, bl = mcolors.to_rgb(c)
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(bl)

lums = [luminance(matplotlib.colormaps["viridis"](t)) for t in np.linspace(0, 1, 10)]
print("viridis lightness rises monotonically:", all(a < b for a, b in zip(lums, lums[1:])))

# 07. Colorblind-Safe Palettes
# ------------------------------------
# - About 1 in 12 men has some red-green colour-vision deficiency.
# - Safe categorical palette: Okabe-Ito (below), seaborn "colorblind",
#   or the built-in "tableau-colorblind10" style.
# - Avoid red vs green as the only distinction. Viridis is also safe.
# - Do not rely on colour alone (see next section).

OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
print("Okabe-Ito colours:", len(OKABE_ITO), "| all valid:", all(mcolors.is_color_like(c) for c in OKABE_ITO))
print("built-in colorblind style present:", "tableau-colorblind10" in plt.style.available)
with plt.rc_context({"axes.prop_cycle": matplotlib.cycler(color=OKABE_ITO)}):
    fig, ax = plt.subplots()
    lines = [ax.plot([0, 1], [i, i + 1])[0] for i in range(3)]
    print("cycle applied:", [mcolors.to_hex(l.get_color()).upper() for l in lines])
    plt.close(fig)

# 08. Accessibility
# ------------------------------------
# - Encode with MORE than colour: add marker shapes, line styles, direct
#   labels, or hatching, so greyscale prints and colour-blind readers work.
# - Contrast: text and lines need enough luminance contrast against the
#   background (WCAG ratio >= 4.5 for text, >= 3 for graphics).
# - Font sizes: >= 10-12 pt in the final size; check at the size it will be
#   displayed.
# - Provide alt text / a text summary of the finding (in notebooks/web).
# - Do not use red-green traffic lights alone; add icons or words.

def contrast(c1, c2):
    a, b = sorted((luminance(c1), luminance(c2)), reverse=True)
    return (a + 0.05) / (b + 0.05)

print("black on white contrast:", round(contrast("black", "white"), 1))
print("yellow #F0E442 on white passes 3:1?", contrast("#F0E442", "white") >= 3)
print("blue #0072B2 on white passes 3:1?", contrast("#0072B2", "white") >= 3)
fig, ax = plt.subplots()
styles = [("o", "-"), ("s", "--"), ("^", ":")]
for i, (m, ls) in enumerate(styles):
    ax.plot([0, 1, 2], [i, i + 1, i + 0.5], marker=m, linestyle=ls, label=f"S{i}")
print("redundant encoding (marker, linestyle):", [(l.get_marker(), l.get_linestyle()) for l in ax.lines])
plt.close(fig)

# 09. Labels, Titles, Units and Annotations
# ------------------------------------
# - Title states the finding ("Sales doubled after March"), not the topic
#   ("Sales").
# - Axis labels name the variable AND the unit: "Revenue (USD millions)".
# - Label lines directly at their ends instead of a legend far away.
# - Annotate the one or two points the reader must notice; grey out the rest.
# - Add source and date in a footnote (fig.text) for reports.

months = np.arange(1, 13)
sales = 100 + 8 * months + rng.normal(0, 4, 12)
fig, ax = plt.subplots()
ax.plot(months, sales, color="0.6")
ax.annotate("campaign launch", xy=(6, sales[5]), xytext=(6, sales[5] + 25),
            arrowprops=dict(arrowstyle="->"))
ax.set_title("Sales grew steadily through the year")
ax.set_xlabel("Month (2024)")
ax.set_ylabel("Revenue (USD thousands)")
fig.text(0.01, 0.01, "Source: demo data", fontsize=8)
print("title:", ax.get_title())
print("labels carry units:", "(" in ax.get_ylabel(), "| annotation:", ax.texts[0].get_text())
print("figure footnote:", fig.texts[0].get_text())
plt.close(fig)

# 10. Small Multiples
# ------------------------------------
# - Many series on ONE chart = spaghetti. Split into a grid of small panels
#   with the SAME axes so panels are comparable (sharex/sharey=True).
# - Highlight the series of interest; put the others in light grey behind it.
# - Order panels meaningfully (alphabetical, by size).

series = {f"G{i}": np.cumsum(rng.normal(0, 1, 30)) for i in range(6)}
fig, axs = plt.subplots(2, 3, sharex=True, sharey=True, layout="constrained")
for ax, (name, y) in zip(axs.flat, series.items()):
    for other in series.values():
        ax.plot(other, color="0.85", lw=0.8)        # context
    ax.plot(y, color="C0", lw=1.5)                   # focus
    ax.set_title(name, fontsize=9)
print("panels:", axs.size, "| lines per panel:", len(axs[0, 0].lines), "| shared y:",
      axs[0, 0].get_shared_y_axes().joined(axs[0, 0], axs[1, 2]))
plt.close(fig)

# 11. Data-Ink and Decluttering
# ------------------------------------
# - Remove what does not carry information: heavy borders, top/right spines,
#   dense grids, 3D effects, redundant legends, rainbow fills.
# - Keep a light grid only if readers need to read values; or label bars
#   directly and delete the axis.
# - Lighten, do not delete, things you need (grey, thin lines).
# - Rule: when a mark can be removed with no loss of information, remove it.

fig, ax = plt.subplots()
bars = ax.bar(["A", "B", "C"], [3, 5, 4], color="0.5")
ax.bar_label(bars)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.yaxis.set_visible(False)
ax.spines["left"].set_visible(False)
print("visible spines:", [k for k, s in ax.spines.items() if s.get_visible()])
print("y axis hidden but values labelled:", not ax.yaxis.get_visible(), [t.get_text() for t in ax.texts])
plt.close(fig)

# 12. Reusable Plot Helpers Returning (fig, ax)
# ------------------------------------
# - Wrap repeated plots in functions that (a) accept an optional ax=, (b)
#   return (fig, ax), (c) do NOT call plt.show() or plt.close() inside,
#   (d) never use global pyplot state except to create a figure.
# - The caller can then tweak, save, test or compose the result.
# - If ax is given, draw on it and return its figure - this is the same
#   convention seaborn uses.

def bar_compare(labels, values, *, title, xlabel, sort=True, ax=None):
    """Horizontal bars starting at zero, sorted, with value labels."""
    labels, values = list(labels), list(values)
    if sort:
        pairs = sorted(zip(values, labels))
        values, labels = [p[0] for p in pairs], [p[1] for p in pairs]
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure
    bars = ax.barh(labels, values)
    ax.bar_label(bars, padding=2)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_xlim(left=0)
    return fig, ax


def line_trend(x, y, *, title, xlabel, ylabel, highlight=None, ax=None):
    """Single trend line with an optional highlighted point."""
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure
    ax.plot(x, y, color="C0")
    if highlight is not None:
        ax.plot([x[highlight]], [y[highlight]], "o", color="C3")
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    return fig, ax


fig, ax = bar_compare(["A", "B", "C"], [3, 9, 5], title="B leads", xlabel="Units sold")
print("sorted widths:", [p.get_width() for p in ax.patches], "| returns:", type(fig).__name__, type(ax).__name__)
fig2, axs = plt.subplots(1, 2)
f_back, _ = line_trend([1, 2, 3], [2, 4, 3], title="t", xlabel="x", ylabel="y (m)", highlight=1, ax=axs[1])
print("helper reused caller's figure:", f_back is fig2)
plt.close("all")

# 13. A Style Guide Dict with rc_context
# ------------------------------------
# - Put the house style in ONE dict of rcParams and apply it with
#   plt.rc_context(STYLE). Style changes then apply to a block only and
#   nothing leaks into other code (unlike plt.style.use / rcParams[...] = ...).
# - Include: font sizes, colour cycle, spines, grid, figure size, dpi,
#   savefig defaults.
# - Keep it in one module so every chart in a project matches.
# - Alternative: a .mplstyle file loaded with plt.style.use("path").

STYLE = {
    "figure.figsize": (6, 4),
    "figure.dpi": 100,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.prop_cycle": matplotlib.cycler(color=OKABE_ITO),
    "savefig.bbox": "tight",
    "savefig.dpi": 150,
}
before = (plt.rcParams["font.size"], plt.rcParams["axes.spines.top"])
with plt.rc_context(STYLE):
    fig, ax = bar_compare(["A", "B"], [1, 2], title="styled", xlabel="n")
    inside = (plt.rcParams["font.size"], plt.rcParams["axes.spines.top"])
    top_visible = ax.spines["top"].get_visible()
    first_color = mcolors.to_hex(ax.patches[0].get_facecolor()).upper()
    plt.close(fig)
print("before / inside / after:", before, inside, (plt.rcParams["font.size"], plt.rcParams["axes.spines.top"]))
print("figure used the style (top spine hidden):", not top_visible, "| first colour:", first_color)

# 14. Testing Plots Instead of Eyeballing
# ------------------------------------
# - Do not compare pixels. Assert on the ARTISTS: line data, labels, titles,
#   bar heights, limits, number of axes, legend text.
# - Plot functions that return (fig, ax) are easy to test: call, then
#   inspect ax.lines, ax.patches, ax.get_xlabel() ...
# - In pytest use: matplotlib.use("Agg") (or MPLBACKEND), close figures in a
#   fixture/teardown, use np.testing.assert_allclose on data.
# - For visual regression use pytest-mpl (image comparison with tolerance) -
#   a separate, heavier tool.

def check_line_trend():
    x, y = [1, 2, 3], [2.0, 4.0, 3.0]
    fig, ax = line_trend(x, y, title="T", xlabel="Month", ylabel="Sales (k)", highlight=1)
    try:
        assert ax.get_title() == "T"
        assert ax.get_xlabel() == "Month" and ax.get_ylabel() == "Sales (k)"
        np.testing.assert_allclose(ax.lines[0].get_xdata(), x)
        np.testing.assert_allclose(ax.lines[0].get_ydata(), y)
        assert len(ax.lines) == 2                             # main line + highlight
        assert ax.lines[1].get_ydata()[0] == 4.0
    finally:
        plt.close(fig)
    return True

def check_bar_compare():
    fig, ax = bar_compare(["A", "B", "C"], [3, 9, 5], title="B leads", xlabel="Units")
    try:
        assert [p.get_width() for p in ax.patches] == [3, 5, 9]               # sorted
        assert [t.get_text() for t in ax.get_yticklabels()] == ["A", "C", "B"]
        assert ax.get_xlim()[0] == 0                                        # starts at zero
        assert len(ax.texts) == 3                                           # value labels
    finally:
        plt.close(fig)
    return True

print("line_trend checks pass:", check_line_trend())
print("bar_compare checks pass:", check_bar_compare())
fig, ax = bar_compare(["A"], [1], title="t", xlabel="x")
try:
    assert ax.get_title() == "wrong title"
except AssertionError:
    print("a deliberately wrong assertion is caught -> tests can fail")
buf = io.BytesIO()
fig.savefig(buf, format="png")
print("rendering also works (bytes > 0):", buf.tell() > 0)
plt.close(fig)

# 15. Before/After: Truncated Axis
# ------------------------------------
# - Mistake: bar axis starting at 95 turns a 3% gap into a 3x visual gap.
# - Fix: start bars at 0. If the small difference is the story, use a dot
#   plot / show the difference itself, and label it.

vals2 = [97, 100]
fig, (bad, good) = plt.subplots(1, 2)
bad.bar(["old", "new"], vals2)
bad.set_ylim(95, 101)
good.bar(["old", "new"], vals2)
good.set_ylim(0, 105)
def visual_ratio(ax):
    lo = ax.get_ylim()[0]
    h = [p.get_height() - lo for p in ax.patches]
    return round(h[1] / h[0], 2)
print("true ratio:", round(vals2[1] / vals2[0], 2))
print("visual ratio before (truncated):", visual_ratio(bad), "| after (from zero):", visual_ratio(good))
plt.close(fig)

# 16. Before/After: Spaghetti and Overplotting
# ------------------------------------
# - Mistake 1: 30 lines in one axes with 30 legend entries.
#   Fix: highlight one or two in colour, grey the rest, label directly.
# - Mistake 2: scatter of 100k points = solid blob.
#   Fix: alpha, smaller markers, hexbin/hist2d, or sample.
# - Mistake 3: default legend covering data.
#   Fix: loc / bbox_to_anchor outside, or direct labels.

n = 20000
ox = rng.normal(size=n)
oy = ox + rng.normal(size=n)
fig, (a1, a2) = plt.subplots(1, 2)
a1.scatter(ox, oy, s=10)
a2.hexbin(ox, oy, gridsize=20, mincnt=1)
cells = a2.collections[0].get_array()
print("before: one marker per point =", len(a1.collections[0].get_offsets()), "overlapping markers")
print("after: hexbin cells =", len(cells), "| densest cell holds", int(cells.max()), "points | total kept:", int(cells.sum()) == n)
plt.close(fig)

fig, ax = plt.subplots()
for i, y in enumerate(series.values()):
    focus = (i == 2)
    ax.plot(y, color="C3" if focus else "0.8", lw=2 if focus else 0.8, zorder=3 if focus else 1)
print("spaghetti fixed: 1 highlighted of", len(ax.lines), "| colours:",
      sorted({mcolors.to_hex(l.get_color()) for l in ax.lines}))
plt.close(fig)

# 17. Pre-Publish Checklist
# ------------------------------------
# - [ ] Is the question / message clear from the title?
# - [ ] Right chart for the question (section 01)?
# - [ ] Bars start at zero; log or cut axes are labelled?
# - [ ] Axis labels with units; readable font size?
# - [ ] Colours meaningful, colourblind-safe, not the only encoding?
# - [ ] Legend not covering data; or direct labels?
# - [ ] Nothing decorative left (3D, heavy grid, borders)?
# - [ ] Source / date noted; numbers match the data (test them)?
# - [ ] Saved at proper dpi/format; figures closed in scripts.

CHECKLIST = ["title says the message", "right chart type", "zero baseline for bars", "units on labels",
             "accessible colours", "legend clear", "decluttered", "source noted", "saved and closed"]
print("checklist items:", len(CHECKLIST))
print("open figures at end:", len(plt.get_fignums()))
plt.show()                                   # no-op under Agg
