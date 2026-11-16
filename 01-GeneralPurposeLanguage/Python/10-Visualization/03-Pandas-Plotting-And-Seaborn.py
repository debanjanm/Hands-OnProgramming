# 01. df.plot Basics
# 02. A Tour of kind=
# 03. Drawing on a Given ax
# 04. groupby + plot
# 05. Secondary y Axis
# 06. subplots=True
# 07. Stacked Bars
# 08. Rolling Mean Overlay
# 09. pd.plotting.scatter_matrix
# 10. Seaborn: Figure-Level vs Axes-Level
# 11. histplot, kdeplot, displot
# 12. boxplot and violinplot
# 13. barplot (Aggregates + Error Bars)
# 14. heatmap
# 15. pairplot
# 16. regplot and lmplot
# 17. catplot
# 18. relplot
# 19. Facets: hue, col, row
# 20. Themes and Palettes

import os
os.environ.setdefault("MPLBACKEND", "Agg")   # headless; in Jupyter the inline backend is already set

import warnings

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# plt.show() under Agg only warns "cannot be shown"; silence just that message
warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive")

try:                                         # seaborn is optional: the file must still run without it
    import seaborn as sns
    HAVE_SNS = True
except ImportError:
    sns = None
    HAVE_SNS = False
    print("seaborn not installed - seaborn sections (10-20) will be skipped")

rng = np.random.default_rng(7)

dates = pd.date_range("2024-01-01", periods=60, freq="D")
ts = pd.DataFrame({
    "sales": 100 + np.cumsum(rng.normal(0, 5, 60)),
    "visits": 1000 + np.cumsum(rng.normal(0, 40, 60)),
}, index=dates)

df = pd.DataFrame({
    "team": rng.choice(["red", "green", "blue"], 120),
    "size": rng.choice(["S", "M", "L"], 120),
    "x": rng.normal(0, 1, 120),
})
df["y"] = 2 * df["x"] + rng.normal(0, 1, 120)
df["score"] = 50 + 10 * df["x"] + rng.normal(0, 3, 120)

# 01. df.plot Basics
# ------------------------------------
# - df.plot() and Series.plot() are thin wrappers over matplotlib: they
#   return a matplotlib Axes (or an array of Axes).
# - With no x=, the INDEX is the x-axis and each numeric column is one line.
#   A DatetimeIndex gives a nicely formatted time axis for free.
# - Everything you learned in file 01/02 applies to the returned ax:
#   ax.set_title, ax.set_ylabel, ax.get_lines(), ...
# - Non-numeric columns are silently skipped for most kinds.

ax = ts.plot(title="Sales and visits")
print("returned:", type(ax).__name__, "| lines:", len(ax.get_lines()))
print("legend labels:", [t.get_text() for t in ax.get_legend().get_texts()])
print("title:", ax.get_title(), "| line length:", len(ax.get_lines()[0].get_xdata()))
plt.close("all")

# 02. A Tour of kind=
# ------------------------------------
# - kind="line" (default), "bar", "barh", "hist", "box", "area", "pie",
#   "scatter" (needs x= and y=), "hexbin", "kde"/"density" (needs scipy).
# - Shortcuts: df.plot.bar(), df.plot.hist(), df.plot.scatter(x=, y=).
# - kind="area" stacks by default; kind="hist" overlays columns (alpha!).
# - kind="pie" needs a single column (y=) and uses the index as labels.

small = pd.DataFrame({"a": [3, 5, 2], "b": [4, 1, 6]}, index=["u", "v", "w"])
for kind in ("line", "bar", "barh", "area", "box", "hist"):
    ax = small.plot(kind=kind)
    print(f"{kind:5s} -> lines {len(ax.get_lines()):2d} | patches {len(ax.patches):2d}")
    plt.close("all")
ax = df.plot.scatter(x="x", y="y")
print("scatter points:", len(ax.collections[0].get_offsets()))
ax = small["a"].plot.pie()
print("pie wedges:", len(ax.patches), "| labels:", [t.get_text() for t in ax.texts if t.get_text()])
ax = df.plot.hexbin(x="x", y="y", gridsize=8)
print("hexbin sum == n:", int(ax.collections[0].get_array().sum()) == len(df))
plt.close("all")

# 03. Drawing on a Given ax
# ------------------------------------
# - Pass ax=ax to put a pandas plot onto an Axes you created. This is how
#   you mix pandas and matplotlib or build dashboards.
# - Without ax= pandas uses the current axes/figure, which can surprise you
#   (it may create a new figure).
# - The same works for seaborn axes-level functions.

fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3), layout="constrained")
ts["sales"].plot(ax=a1, color="tab:blue")
ts["visits"].plot(ax=a2, color="tab:green")
a1.set_title("Sales")
a2.set_title("Visits")
print("lines on each:", len(a1.get_lines()), len(a2.get_lines()), "| figures open:", len(plt.get_fignums()))
plt.close(fig)

# 04. groupby + plot
# ------------------------------------
# - df.groupby("g")["col"].plot() draws ONE LINE/HIST PER GROUP on the same
#   axes (legend from group names if you add legend=True).
# - Aggregate first for bars: df.groupby("g")["v"].mean().plot.bar().
# - Wide table via unstack/pivot gives one column per group: easy to plot
#   with df.plot().
# - Gotcha: groupby(...).plot() returns a Series of Axes, not one Axes.

means = df.groupby("team")["score"].mean()
ax = means.plot.bar(ylabel="mean score")
print("group means (rounded):", means.round(1).to_dict())
print("bar heights match:", [round(p.get_height(), 1) for p in ax.patches] == means.round(1).tolist())
plt.close("all")

fig, ax = plt.subplots()
res = df.groupby("team")["score"].plot.hist(ax=ax, alpha=0.5, bins=8, legend=True)
print("groupby.plot returns:", type(res).__name__, "| groups:", sorted(res.index))
print("legend:", sorted(t.get_text() for t in ax.get_legend().get_texts()))
plt.close(fig)

wide = df.pivot_table(index="size", columns="team", values="score", aggfunc="mean")
ax = wide.plot.bar()
print("pivot shape:", wide.shape, "| bars:", len(ax.patches))
plt.close("all")

# 05. Secondary y Axis
# ------------------------------------
# - df.plot(secondary_y="col") (or a list) draws that column against a
#   right-hand axis. The legend marks it as "col (right)".
# - Also df["col"].plot(secondary_y=True, ax=ax) to add onto an axes.
# - Same warning as before: two scales can mislead (see file 04).

ax = ts.plot(secondary_y="visits")
print("axes in figure:", len(ax.figure.axes), "(left ax + right ax)")
print("legend:", [t.get_text() for t in ax.get_legend().get_texts()])
print("right-hand ylim differs:", ax.get_ylim() != ax.right_ax.get_ylim())
plt.close("all")

# 06. subplots=True
# ------------------------------------
# - df.plot(subplots=True) gives one Axes per column (returns an ndarray).
# - layout=(rows, cols), sharex=True, sharey=False, figsize=...
# - Small multiples let each series use its own y-scale: much clearer than
#   one crowded plot.

axes = ts.plot(subplots=True, layout=(1, 2), sharex=True, figsize=(8, 3))
print("axes shape:", axes.shape, "| legend per axes:", [a.get_legend().get_texts()[0].get_text() for a in axes.ravel()])
print("each has 1 line:", [len(a.get_lines()) for a in axes.ravel()])
plt.close("all")

# 07. Stacked Bars
# ------------------------------------
# - df.plot.bar(stacked=True) stacks columns on top of each other;
#   df.plot.area() and barh work too.
# - For parts of a whole (100%), normalise first:
#   df.div(df.sum(axis=1), axis=0).
# - Order of columns = order of stack; put the baseline series first.
# - Gotcha: stacked bars only compare the BOTTOM segment accurately.

counts = pd.crosstab(df["team"], df["size"])
ax = counts.plot.bar(stacked=True)
print("crosstab:\n" + counts.to_string())
print("bars:", len(ax.patches), "(3 teams x 3 sizes)")
tops = [round(p.get_y() + p.get_height()) for p in ax.patches[-3:]]
print("top of stack equals row totals:", tops == counts.sum(axis=1).tolist())
share = counts.div(counts.sum(axis=1), axis=0)
print("row shares sum to 1:", bool(np.allclose(share.sum(axis=1), 1)))
plt.close("all")

# 08. Rolling Mean Overlay
# ------------------------------------
# - Noisy series: overlay a smoothed line with .rolling(window).mean().
# - First window-1 values are NaN: matplotlib just leaves a gap.
# - Plot both on the SAME ax; make the raw line pale and the smooth line bold.
# - center=True aligns the average with the middle of the window.

fig, ax = plt.subplots()
ts["sales"].plot(ax=ax, alpha=0.4, label="daily")
roll = ts["sales"].rolling(7).mean()
roll.plot(ax=ax, lw=2, label="7-day mean")
ax.legend()
print("lines:", len(ax.get_lines()), "| NaNs at start of rolling line:", int(roll.isna().sum()))
print("smooth line is smoother (std of diffs):",
      bool(roll.diff().std() < ts["sales"].diff().std()))
plt.close(fig)

# 09. pd.plotting.scatter_matrix
# ------------------------------------
# - pd.plotting.scatter_matrix(df) draws every numeric column against every
#   other (histogram or KDE on the diagonal). Returns a 2D array of Axes.
# - Good first look at relationships; breaks down beyond ~8 columns.
# - diagonal="hist" (default) or "kde"; alpha helps with overlap.

num = df[["x", "y", "score"]]
axs = pd.plotting.scatter_matrix(num, figsize=(5, 5), diagonal="hist")
print("matrix of axes:", axs.shape)
print("diagonal bars (hist) in [0,0]:", len(axs[0, 0].patches) > 0,
      "| off-diagonal points:", len(axs[0, 1].collections[0].get_offsets()))
plt.close("all")

# --- Seaborn part (sections 10-20) ---
# - seaborn builds on matplotlib + pandas. It works best with TIDY ("long")
#   data: one row per observation, one column per variable.
# - pip install seaborn if you do not have it; guarded below.

# 10. Seaborn: Figure-Level vs Axes-Level
# ------------------------------------
# - AXES-level functions (histplot, kdeplot, scatterplot, lineplot, boxplot,
#   violinplot, barplot, heatmap, regplot ...) draw on ONE Axes and return it.
#   They accept ax= so you can place them in your own subplots.
# - FIGURE-level functions (displot, relplot, catplot, lmplot, pairplot,
#   jointplot) create their OWN figure, can facet with col=/row=, and return
#   a grid object (FacetGrid/PairGrid). They do NOT take ax=; size is set
#   with height= and aspect= PER FACET.
# - Rule of thumb: need subplots/facets by a variable -> figure-level;
#   need to fit into your own layout -> axes-level.
# - Close a grid with plt.close(g.figure).

if HAVE_SNS:
    fig, ax = plt.subplots()
    out = sns.histplot(data=df, x="score", ax=ax)
    print("axes-level returns:", type(out).__name__, "| same ax:", out is ax)
    g = sns.displot(data=df, x="score", col="team")
    print("figure-level returns:", type(g).__name__, "| facets:", g.axes.shape)
    print("sns version >= 0.13:", tuple(int(v) for v in sns.__version__.split(".")[:2]) >= (0, 13))
    plt.close(fig)
    plt.close(g.figure)

# 11. histplot, kdeplot, displot
# ------------------------------------
# - histplot(x=...): bins, stat="count"|"density"|"probability",
#   kde=True overlays a smooth curve, hue= splits by group,
#   multiple="layer"|"stack"|"dodge"|"fill".
# - kdeplot: smooth density; fill=True shades; common_norm=False scales each
#   group on its own.
# - displot(kind="hist"|"kde"|"ecdf") is the figure-level version.
# - Gotcha: bandwidth too small -> noisy, too big -> hides structure
#   (bw_adjust).

if HAVE_SNS:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3))
    sns.histplot(data=df, x="score", bins=10, kde=True, ax=a1)
    sns.kdeplot(data=df, x="score", hue="team", fill=True, common_norm=False, ax=a2)
    print("hist bars:", len(a1.patches), "| kde curve on hist ax:", len(a1.lines))
    print("kde groups drawn:", len(a2.collections), "| legend:", sorted(t.get_text() for t in a2.get_legend().get_texts()))
    g = sns.displot(data=df, x="score", kind="ecdf", hue="team")
    print("ecdf lines:", len(g.ax.lines), "| y range ok:", g.ax.get_ylim()[1] >= 1.0)
    plt.close(fig)
    plt.close(g.figure)

# 12. boxplot and violinplot
# ------------------------------------
# - sns.boxplot(data=df, x="cat", y="num") one box per category; hue= splits
#   further. 1.5 * IQR whiskers, dots = outliers.
# - violinplot adds the density shape; inner="quart"|"box"|"point".
# - Show the data too: sns.stripplot or swarmplot on top.
# - Gotcha: a box on <10 points hides the real data - show the points.

if HAVE_SNS:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3))
    sns.boxplot(data=df, x="team", y="score", ax=a1)
    sns.violinplot(data=df, x="team", y="score", inner="quart", ax=a2)
    sns.stripplot(data=df, x="team", y="score", color="k", size=2, ax=a1)
    print("boxes:", len(a1.patches), "| violins:", len(a2.collections))
    print("category order on x:", [t.get_text() for t in a1.get_xticklabels()])
    print("y label auto-set:", a1.get_ylabel())
    plt.close(fig)

# 13. barplot (Aggregates + Error Bars)
# ------------------------------------
# - sns.barplot computes the MEAN of y per category and draws a 95%
#   bootstrap confidence interval as the error bar (errorbar=("ci", 95)).
#   Change with estimator="median", errorbar="sd" or errorbar=None.
# - Different from matplotlib's ax.bar which draws exactly the heights you
#   pass. barplot aggregates raw rows for you.
# - sns.countplot(x=...) counts rows per category.
# - The bootstrap is random: pass seed= for reproducible CIs.

if HAVE_SNS:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3))
    sns.barplot(data=df, x="team", y="score", errorbar="sd", ax=a1)
    sns.countplot(data=df, x="team", ax=a2)
    expected = df.groupby("team")["score"].mean()
    labels = [t.get_text() for t in a1.get_xticklabels()]
    heights = [p.get_height() for p in a1.patches]
    print("bar heights are group means:",
          all(np.isclose(h, expected[l]) for h, l in zip(heights, labels)))
    print("countplot sums to n:", int(sum(p.get_height() for p in a2.patches)) == len(df))
    plt.close(fig)

# 14. heatmap
# ------------------------------------
# - sns.heatmap(matrix, annot=True, fmt=".2f", cmap=..., center=0, vmin/vmax).
# - Typical input: df.corr(numeric_only=True) or a pivot table.
# - Use a DIVERGING cmap with center=0 for correlations; sequential for counts.
# - The heatmap is axes-level; the colorbar is added as a second Axes.
# - Gotcha: heatmap draws row 0 on TOP and fixes aspect by cell, so tall
#   matrices need figsize tuning.

if HAVE_SNS:
    corr = df[["x", "y", "score"]].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, center=0, ax=ax)
    print("axes in figure (plot + colorbar):", len(fig.axes))
    print("annotations:", len(ax.texts), "| tick labels:", [t.get_text() for t in ax.get_xticklabels()])
    print("diagonal annotated as 1.00:", ax.texts[0].get_text())
    plt.close(fig)

# 15. pairplot
# ------------------------------------
# - sns.pairplot(df, hue="cat", vars=[...], diag_kind="hist"|"kde",
#   corner=True) - seaborn's richer scatter_matrix; returns a PairGrid.
# - Slow for many columns/rows; use vars= and sample().
# - g.axes is a 2D array; g.figure is the Figure.

if HAVE_SNS:
    g = sns.pairplot(df, vars=["x", "y", "score"], hue="team", diag_kind="hist", height=1.5)
    print("PairGrid:", type(g).__name__, "| grid:", g.axes.shape)
    print("legend labels:", sorted(t.get_text() for t in g.legend.get_texts()))
    plt.close(g.figure)

# 16. regplot and lmplot
# ------------------------------------
# - regplot(x=, y=) (axes-level) draws scatter + a fitted regression line
#   with a confidence band. lmplot is the figure-level twin (hue/col/row).
# - order=2 fits a polynomial; lowess=True a local smoother (needs
#   statsmodels); ci=None removes the band; scatter_kws / line_kws tweak
#   the parts.
# - It is a VISUAL aid; use statsmodels / scikit-learn for real fits.

if HAVE_SNS:
    fig, ax = plt.subplots()
    sns.regplot(data=df, x="x", y="y", ci=95, ax=ax)
    slope = np.polyfit(df["x"], df["y"], 1)[0]
    line = ax.lines[0]
    drawn = np.polyfit(line.get_xdata(), line.get_ydata(), 1)[0]
    print("drawn slope equals OLS slope:", bool(np.isclose(slope, drawn, atol=1e-6)), "| slope ~", round(float(slope), 2))
    print("points:", len(ax.collections[0].get_offsets()), "| band drawn:", len(ax.collections) == 2)
    g = sns.lmplot(data=df, x="x", y="y", hue="team", height=3)
    print("lmplot lines (one per hue):", len(g.ax.lines))
    plt.close(fig)
    plt.close(g.figure)

# 17. catplot
# ------------------------------------
# - sns.catplot(kind=...) is the figure-level interface to the categorical
#   family: "strip", "swarm", "box", "violin", "boxen", "point", "bar",
#   "count".
# - Facet with col= / row=; size with height= and aspect=.
# - orient="h" flips to horizontal (put the category on y).

if HAVE_SNS:
    g = sns.catplot(data=df, x="team", y="score", hue="size", kind="box", col="size", height=2.5)
    print("catplot facets:", g.axes.shape, "| col titles:", [a.get_title() for a in g.axes.flat])
    print("boxes in first facet:", len(g.axes.flat[0].patches))
    plt.close(g.figure)

# 18. relplot
# ------------------------------------
# - sns.relplot(kind="scatter"|"line") is the figure-level relational plot.
# - Encode more variables: hue (colour), size, style (marker/dash).
# - lineplot aggregates repeated x values: mean line + 95% CI band by
#   default (errorbar=...). Use estimator=None to see raw lines.
# - Do not encode too many variables at once: readers cannot decode it.

if HAVE_SNS:
    g = sns.relplot(data=df, x="x", y="y", hue="team", style="size", kind="scatter", height=3)
    print("relplot figure axes:", len(g.figure.axes), "| legend entries >= 6:", len(g.legend.get_texts()) >= 6)
    plt.close(g.figure)
    long = ts.reset_index(names="date").melt("date", var_name="metric", value_name="value")
    g = sns.relplot(data=long, x="date", y="value", col="metric", kind="line",
                    facet_kws={"sharey": False}, height=2.5)
    print("line facets:", g.axes.shape, "| lines per facet:", [len(a.lines) for a in g.axes.flat])
    plt.close(g.figure)

# 19. Facets: hue, col, row
# ------------------------------------
# - hue = colours inside ONE axes; col / row = separate small axes
#   (small multiples). col_wrap= wraps a long row of facets.
# - Under the hood: sns.FacetGrid(data, col=, row=) then g.map_dataframe(...)
#   (use map_dataframe with seaborn functions).
# - g.set_axis_labels, g.set_titles("{col_name}"), g.add_legend() polish it.
# - Sharing: sharex/sharey (default True) keeps scales comparable.

if HAVE_SNS:
    g = sns.FacetGrid(df, col="team", row="size", height=1.4, margin_titles=True)
    g.map_dataframe(sns.histplot, x="score", bins=6)
    g.set_axis_labels("score", "count")
    print("facet grid shape (rows x cols):", g.axes.shape)
    print("col names:", list(g.col_names), "| row names:", list(g.row_names))
    print("all facets share xlim:", len({a.get_xlim() for a in g.axes.flat}) == 1)
    plt.close(g.figure)

# 20. Themes and Palettes
# ------------------------------------
# - sns.set_theme(style="whitegrid", context="notebook", palette="deep",
#   font_scale=1.0) sets global defaults (it changes matplotlib rcParams!).
#   Styles: darkgrid, whitegrid, dark, white, ticks.
#   Contexts: paper, notebook, talk, poster (scale of labels and lines).
# - sns.despine() removes the top/right spines.
# - Palettes: sns.color_palette("deep") (categorical), "colorblind"
#   (colourblind-safe), "viridis"/"mako"/"rocket" (sequential),
#   "vlag"/"coolwarm" (diverging). sns.color_palette(name, n) returns n
#   RGB tuples.
# - sns.axes_style() shows the current style; with sns.axes_style("dark"):
#   applies a style temporarily.
# - Gotcha: set_theme is GLOBAL - reset with sns.reset_defaults() (or
#   plt.rcdefaults()) so later plots look as expected.

if HAVE_SNS:
    sns.set_theme(style="whitegrid", palette="colorblind")
    print("palette size (colorblind):", len(sns.color_palette("colorblind")))
    print("first colour hex:", matplotlib.colors.to_hex(sns.color_palette("colorblind")[0]))
    print("sequential 5 colours:", len(sns.color_palette("mako", 5)))
    fig, ax = plt.subplots()
    sns.despine(ax=ax)
    print("top/right spines hidden:", not ax.spines["top"].get_visible(), not ax.spines["right"].get_visible())
    print("grid on under whitegrid:", plt.rcParams["axes.grid"])
    plt.close(fig)
    with sns.axes_style("dark"):
        print("temporary style grid:", plt.rcParams["axes.grid"])
    sns.reset_defaults()
    plt.rcdefaults()
    print("after reset grid:", plt.rcParams["axes.grid"])
plt.show()                                   # no-op under Agg
