# 01. Two APIs: pyplot vs Object-Oriented
# 02. Anatomy: Figure, Axes, Axis, Artist
# 03. Line Plots
# 04. Scatter Plots
# 05. Bar and Barh
# 06. Histograms
# 07. Box Plots
# 08. Pie Charts
# 09. Error Bars
# 10. fill_between
# 11. Labels, Titles, Legend
# 12. Ticks, Limits, Grid
# 13. Markers, Linestyles, Colors
# 14. Styles
# 15. rcParams
# 16. Saving Figures
# 17. Closing Figures and Memory Leaks

import os
os.environ.setdefault("MPLBACKEND", "Agg")   # headless; in Jupyter the inline backend is already set

import io
import tempfile
import warnings

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# plt.show() under Agg only warns "cannot be shown"; silence just that message
warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive")

rng = np.random.default_rng(42)

# 01. Two APIs: pyplot vs Object-Oriented
# ------------------------------------
# - pyplot (state-machine) style: plt.plot(...), plt.title(...). It silently
#   works on "the current figure / current axes" - handy in quick scripts.
# - Object-oriented (OO) style: fig, ax = plt.subplots(); ax.plot(...).
#   You always say WHICH axes you are drawing on. Prefer this one.
# - Why OO wins: no hidden global state, works with many subplots, easy to
#   put inside functions, and every call is explicit.
# - plt.subplots() is just a convenience that creates the Figure and Axes
#   together.

print("backend:", matplotlib.get_backend().lower())

plt.plot([1, 2, 3], [1, 4, 9])           # pyplot style: uses the implicit current axes
plt.title("pyplot style")
implicit_ax = plt.gca()
print("pyplot title:", implicit_ax.get_title(), "| lines:", len(implicit_ax.lines))
plt.close()

fig, ax = plt.subplots()                  # OO style: explicit objects
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_title("OO style")
print("OO title:", ax.get_title(), "| lines:", len(ax.lines))
print("# Gotcha: OO methods are set_title / set_xlabel / set_xlim, not title() / xlabel() / xlim().")
plt.close(fig)

# 02. Anatomy: Figure, Axes, Axis, Artist
# ------------------------------------
# - Figure: the whole canvas (the window / the image). Holds one or more Axes.
# - Axes: ONE plot area (data region + its title, labels, ticks). The word
#   is confusing: "Axes" is the plot, not the plural of axis.
# - Axis: the actual x-axis or y-axis object (ax.xaxis, ax.yaxis) that
#   controls ticks and tick labels.
# - Artist: the base class. EVERYTHING you see (lines, text, patches,
#   ticks, even the Figure itself) is an Artist.
# - Containers on an Axes: ax.lines, ax.patches, ax.collections, ax.texts.

fig, ax = plt.subplots(figsize=(4, 3))
ax.plot([0, 1], [0, 1], label="diag")
ax.bar([0, 1], [0.5, 0.7])
ax.scatter([0.5], [0.5])
ax.text(0.1, 0.9, "hi")
print("figure size (inches):", tuple(fig.get_size_inches()))
print("axes in figure:", len(fig.axes))
print("lines / patches / collections / texts:",
      len(ax.lines), len(ax.patches), len(ax.collections), len(ax.texts))
print("x axis class:", type(ax.xaxis).__name__, "| y axis class:", type(ax.yaxis).__name__)
print("Axes is an Artist:", isinstance(ax, matplotlib.artist.Artist),
      "| Figure is an Artist:", isinstance(fig, matplotlib.artist.Artist))
print("children types:", sorted({type(c).__name__ for c in ax.get_children()})[:4], "...")
plt.close(fig)

# 03. Line Plots
# ------------------------------------
# - ax.plot(x, y) draws a line; it returns a LIST of Line2D (note the comma
#   when unpacking: (line,) = ax.plot(...)).
# - Read the data back with line.get_xdata() / get_ydata() - perfect for
#   verifying a plot without looking at it.
# - Only y given -> x defaults to 0, 1, 2, ...

x = np.linspace(0, 2 * np.pi, 5)
fig, ax = plt.subplots()
(line,) = ax.plot(x, np.sin(x), label="sin")
ax.plot([10, 20, 30])                                  # y only
print("returned type:", type(line).__name__)
print("y data (rounded):", np.round(line.get_ydata(), 3).tolist())
print("x of second line:", ax.lines[1].get_xdata().tolist())
print("plot() with 2D y draws one line per column:", len(ax.plot(np.zeros((4, 3)))))
plt.close(fig)

# 04. Scatter Plots
# ------------------------------------
# - ax.scatter(x, y, s=size, c=color_or_values, alpha=...) draws markers.
# - It makes ONE PathCollection (not many Line2D) - fast for per-point
#   size/color. Data lives in get_offsets().
# - Use plot(x, y, "o") when all points look the same and you have lots.

x, y = rng.normal(size=50), rng.normal(size=50)
fig, ax = plt.subplots()
sc = ax.scatter(x, y, s=20 + 30 * np.abs(y), c=y, cmap="viridis", alpha=0.7)
print("collection type:", type(sc).__name__, "| points:", len(sc.get_offsets()))
print("sizes vary:", len(set(sc.get_sizes().round(3))) > 1)
print("color data range ok:", bool(np.isclose(sc.get_array().min(), y.min())))
print("lines on axes (scatter adds none):", len(ax.lines))
plt.close(fig)

# 05. Bar and Barh
# ------------------------------------
# - ax.bar(x, heights) vertical, ax.barh(y, widths) horizontal.
# - Each bar is a Rectangle in ax.patches (also ax.containers[0]).
# - Use barh when category names are long.
# - Bars should start at zero - cutting the axis exaggerates differences.
# - bottom= (or left=) stacks bars; ax.bar_label adds value labels.

cats = ["A", "B", "C"]
vals = [3, 7, 5]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))
bars = ax1.bar(cats, vals, color="tab:blue")
ax1.bar(cats, [1, 1, 1], bottom=vals, color="tab:orange")      # stacked on top
ax1.bar_label(bars, padding=2)
ax2.barh(["long category name", "another long one"], [4, 9])
print("bars on ax1:", len(ax1.patches), "| heights:", [p.get_height() for p in ax1.patches])
print("barh widths:", [p.get_width() for p in ax2.patches])
print("category tick labels:", [t.get_text() for t in ax1.get_xticklabels()])
print("value labels:", [t.get_text() for t in ax1.texts])
plt.close(fig)

# 06. Histograms
# ------------------------------------
# - ax.hist(data, bins=...) returns (counts, bin_edges, patches).
# - Counts sum to len(data). bins can be an int or explicit edges.
# - density=True makes the AREA equal 1 (not the heights).
# - Bin choice changes the story: try several.

data = rng.normal(loc=50, scale=10, size=1000)
fig, ax = plt.subplots()
counts, edges, patches = ax.hist(data, bins=10)
print("bins:", len(counts), "| edges:", len(edges), "| patches:", len(patches))
print("counts sum == n:", int(counts.sum()) == len(data))
fig2, ax2 = plt.subplots()
dens, e2, _ = ax2.hist(data, bins=20, density=True)
print("density area ~ 1:", bool(np.isclose((dens * np.diff(e2)).sum(), 1.0)))
plt.close(fig)
plt.close(fig2)

# 07. Box Plots
# ------------------------------------
# - ax.boxplot(list_of_arrays) shows median, quartiles (box), whiskers and
#   fliers (outliers, default beyond 1.5 * IQR).
# - It returns a dict of artists: 'medians', 'boxes', 'whiskers', 'fliers'.
# - Pass labels=[...] (matplotlib >= 3.9; older versions used `labels`,
#   newer prefer `tick_labels`).

g1, g2 = rng.normal(0, 1, 100), rng.normal(1, 2, 100)
fig, ax = plt.subplots()
bp = ax.boxplot([g1, g2], tick_labels=["g1", "g2"])
print("keys:", sorted(bp.keys()))
print("boxes:", len(bp["boxes"]), "| medians:", len(bp["medians"]))
print("median of g1 matches:", bool(np.isclose(bp["medians"][0].get_ydata()[0], np.median(g1))))
print("x tick labels:", [t.get_text() for t in ax.get_xticklabels()])
plt.close(fig)

# 08. Pie Charts
# ------------------------------------
# - ax.pie(sizes, labels=..., autopct="%1.1f%%") - wedges are Wedge patches.
# - Sizes are normalised to fractions of the total automatically.
# - Pies are hard to compare by eye; a bar chart is usually better
#   (see 04-Visualization-Best-Practices).

fig, ax = plt.subplots()
wedges, texts, autotexts = ax.pie([50, 30, 20], labels=["x", "y", "z"], autopct="%1.0f%%")
print("wedges:", len(wedges), "| percent labels:", [t.get_text() for t in autotexts])
print("aspect is equal (circle):", ax.get_aspect())
plt.close(fig)

# 09. Error Bars
# ------------------------------------
# - ax.errorbar(x, y, yerr=..., xerr=...) draws points plus error lines.
# - Returns an ErrorbarContainer: (data_line, caplines, barlinecols).
# - Say what the bar means (std, SEM, 95% CI) in the caption or legend.

x = np.arange(4)
y = np.array([2.0, 3.0, 2.5, 4.0])
err = np.array([0.2, 0.4, 0.3, 0.5])
fig, ax = plt.subplots()
eb = ax.errorbar(x, y, yerr=err, fmt="o-", capsize=3, label="mean +- std")
print("container:", type(eb).__name__, "| caplines:", len(eb.lines[1]))
segs = eb.lines[2][0].get_segments()
print("first bar spans:", [round(float(v), 2) for v in segs[0][:, 1]])
plt.close(fig)

# 10. fill_between
# ------------------------------------
# - ax.fill_between(x, y1, y2) shades the area between two curves - great
#   for confidence bands and thresholds.
# - Returns a PolyCollection. alpha keeps the line underneath visible.

x = np.linspace(0, 1, 50)
y = x ** 2
fig, ax = plt.subplots()
ax.plot(x, y)
band = ax.fill_between(x, y - 0.1, y + 0.1, alpha=0.3)
print("band type:", type(band).__name__, "| alpha:", band.get_alpha())
print("collections:", len(ax.collections), "| lines:", len(ax.lines))
plt.close(fig)

# 11. Labels, Titles, Legend
# ------------------------------------
# - ax.set_xlabel / set_ylabel / set_title; fig.suptitle for the whole figure.
# - Put units in labels: "Temperature (C)".
# - Give each artist label="..." then call ax.legend(). Labels starting with
#   an underscore are ignored by the legend.
# - ax.legend() with NO labelled artists warns "No artists with labels" -
#   always label before calling it.
# - loc="best" (default), or loc="upper left", bbox_to_anchor to push outside.

fig, ax = plt.subplots()
ax.plot([0, 1], [0, 1], label="up")
ax.plot([0, 1], [1, 0], label="down")
ax.plot([0, 1], [0.5, 0.5], label="_hidden")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Speed (m/s)")
ax.set_title("Demo")
fig.suptitle("Figure title")
leg = ax.legend(loc="upper right", title="Series")
print("labels:", ax.get_xlabel(), "|", ax.get_ylabel(), "|", ax.get_title())
print("suptitle:", fig.get_suptitle())
print("legend entries:", [t.get_text() for t in leg.get_texts()], "| title:", leg.get_title().get_text())
plt.close(fig)

# 12. Ticks, Limits, Grid
# ------------------------------------
# - ax.set_xlim(lo, hi) / set_ylim; swap the order to invert an axis.
# - ax.set_xticks(positions) then set_xticklabels(names) - set ticks FIRST.
# - ax.tick_params(axis="x", rotation=45) rotates labels.
# - ax.grid(True, alpha=0.3) adds a light grid; ax.set_axisbelow(True) puts
#   it under the data.
# - ax.margins() / autoscale control the padding around data.

fig, ax = plt.subplots()
ax.plot([0, 10], [0, 100])
print("auto xlim:", tuple(round(v, 2) for v in ax.get_xlim()))
ax.set_xlim(0, 10)
ax.set_ylim(100, 0)                       # inverted y-axis
ax.set_xticks([0, 5, 10])
ax.set_xticklabels(["zero", "five", "ten"])
ax.tick_params(axis="x", labelrotation=45)
ax.grid(True, alpha=0.3)
ax.set_axisbelow(True)
print("xlim:", ax.get_xlim(), "| ylim (inverted):", ax.get_ylim())
print("x tick labels:", [t.get_text() for t in ax.get_xticklabels()])
print("y axis inverted:", ax.yaxis_inverted())
plt.close(fig)

# 13. Markers, Linestyles, Colors
# ------------------------------------
# - Format string "[marker][line][color]": "ro--" = red circles dashed.
# - Keywords: marker="o", linestyle="--" (ls), linewidth (lw), color (c),
#   markersize (ms).
# - Colors: names ("tab:blue"), hex ("#1f77b4"), grey as string "0.5",
#   RGB/RGBA tuples in 0-1 range, and cycle refs "C0", "C1", ...
# - Default colors come from the property cycle (C0, C1, ...).

fig, ax = plt.subplots()
(l1,) = ax.plot([0, 1], [0, 1], "ro--")
(l2,) = ax.plot([0, 1], [1, 0], marker="s", linestyle=":", color="#1f77b4", lw=3)
(l3,) = ax.plot([0, 1], [0.5, 0.5], color="0.5")
(l4,) = ax.plot([0, 1], [0.2, 0.2], color="C2")
print("l1:", l1.get_marker(), l1.get_linestyle(), l1.get_color())
print("l2:", l2.get_marker(), l2.get_linestyle(), l2.get_color(), l2.get_linewidth())
print("l3 colour:", l3.get_color(), "| l4 colour:", l4.get_color())
print("named -> RGBA:", matplotlib.colors.to_rgba("tab:blue"))
print("hex  -> hex :", matplotlib.colors.to_hex("C1"))
plt.close(fig)

# 14. Styles
# ------------------------------------
# - plt.style.use("ggplot") changes defaults GLOBALLY for later figures.
# - List them with plt.style.available ("seaborn-v0_8-whitegrid", "ggplot",
#   "bmh", "dark_background", ...). Old "seaborn-whitegrid" names were
#   renamed with the "-v0_8-" part.
# - Temporary style: with plt.style.context("bmh"): ... restores afterwards.
# - Style does NOT change figures that already exist; it applies when
#   artists are created.

print("'ggplot' available:", "ggplot" in plt.style.available)
before = plt.rcParams["axes.facecolor"]
with plt.style.context("dark_background"):
    fig, ax = plt.subplots()
    inside = plt.rcParams["axes.facecolor"]
    plt.close(fig)
print("facecolor before / inside / after:", before, "/", inside, "/", plt.rcParams["axes.facecolor"])
plt.style.use("default")                  # always safe way back to the defaults

# 15. rcParams
# ------------------------------------
# - plt.rcParams is a dict-like of every default (font size, line width,
#   figure size, colour cycle, ...).
# - Change one: plt.rcParams["lines.linewidth"] = 3.
# - Change temporarily: with plt.rc_context({...}): ...
# - Reset: plt.rcdefaults() (or matplotlib.rcdefaults()).
# - Gotcha: values are validated; a typo in the key raises KeyError.

print("default linewidth:", plt.rcParams["lines.linewidth"])
with plt.rc_context({"lines.linewidth": 4, "font.size": 14}):
    fig, ax = plt.subplots()
    (ln,) = ax.plot([0, 1])
    print("in context linewidth:", ln.get_linewidth(), "| font.size:", plt.rcParams["font.size"])
    plt.close(fig)
print("after context linewidth:", plt.rcParams["lines.linewidth"])
try:
    plt.rcParams["lines.linewith"] = 3
except KeyError:
    print("misspelt rcParam key -> KeyError")

# 16. Saving Figures
# ------------------------------------
# - fig.savefig(target, dpi=..., bbox_inches="tight", format=..., transparent=...).
# - Target can be a file path OR a file-like object (io.BytesIO) - then you
#   MUST pass format= because there is no extension to guess from.
# - Formats: png (raster), pdf/svg (vector), jpg, tif. Use vector for
#   papers, png for web.
# - dpi scales raster size: pixels = inches * dpi.
# - bbox_inches="tight" trims whitespace and keeps labels that would be cut.
# - Call savefig BEFORE plt.show() in plain scripts (show may clear the figure).

fig, ax = plt.subplots(figsize=(3, 2))
ax.plot([0, 1], [0, 1])
ax.set_xlabel("a fairly long x label")
sizes = {}
for fmt in ("png", "svg", "pdf"):
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=100, bbox_inches="tight")
    sizes[fmt] = buf.tell() > 0
    if fmt == "png":
        header_ok = buf.getvalue()[:8] == b"\x89PNG\r\n\x1a\n"
print("saved non-empty by format:", sizes, "| PNG signature ok:", header_ok)

lo, hi = io.BytesIO(), io.BytesIO()
fig.savefig(lo, format="png", dpi=50)
fig.savefig(hi, format="png", dpi=200)
print("higher dpi -> bigger file:", hi.tell() > lo.tell())
import struct
w, h = struct.unpack(">II", hi.getvalue()[16:24])
print("200 dpi pixel size == inches * dpi:", (w, h) == (600, 400))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "fig.png")
    fig.savefig(path)
    print("file written to temp dir:", os.path.getsize(path) > 0)
print("temp dir cleaned up:", not os.path.exists(path))
plt.show()                                 # no-op under Agg; displays in a notebook
plt.close(fig)

# 17. Closing Figures and Memory Leaks
# ------------------------------------
# - Every plt.figure()/plt.subplots() stays registered in pyplot until you
#   close it. Loops that make figures without closing leak memory and
#   eventually warn after 20 open figures ("More than 20 figures...").
# - plt.close(fig) closes one, plt.close("all") closes everything,
#   plt.get_fignums() lists the open ones.
# - In Jupyter inline mode, figures are closed after the cell displays them;
#   in scripts YOU must do it.
# - Alternative without pyplot state: matplotlib.figure.Figure() objects are
#   not registered, so nothing leaks (good for servers).

plt.close("all")
print("open before:", len(plt.get_fignums()))
for _ in range(3):
    plt.subplots()
print("after 3 unclosed:", len(plt.get_fignums()))
plt.close("all")
print("after close('all'):", len(plt.get_fignums()))

from matplotlib.figure import Figure
f = Figure()
f.subplots().plot([1, 2])
print("Figure() not tracked by pyplot:", len(plt.get_fignums()) == 0)
