# Pandas Plotting and Seaborn — Notes

## What this covers
Quick plots straight from DataFrames (`df.plot` and its kinds, grouping, secondary axis, subplots, stacking, rolling overlays, `scatter_matrix`) and seaborn's statistical plots (distributions, categorical, matrix, regression, facets, themes, palettes).

## Key points
- `df.plot()` / `Series.plot()` wrap matplotlib and return an Axes (or an array of them). Index = x-axis by default.
- `kind=` options: `line`, `bar`, `barh`, `hist`, `box`, `area`, `pie`, `scatter` (needs `x=` and `y=`), `hexbin`, `kde` (needs scipy).
- Pass `ax=ax` to draw on your own Axes.
- `df.groupby("g")["v"].plot()` draws one series per group; aggregate first for bars.
- `secondary_y="col"` adds a right axis; `subplots=True, layout=(r, c)` makes one panel per column.
- Stacked bars: `stacked=True`; normalise by row sums for shares.
- Overlay `rolling(window).mean()` on the raw series to show the trend.
- `pd.plotting.scatter_matrix(df)` for a first look at pairwise relationships.
- Seaborn wants tidy (long) data. **Axes-level** functions (`histplot`, `boxplot`, `barplot`, `heatmap`, `regplot`) take `ax=` and return an Axes. **Figure-level** functions (`displot`, `catplot`, `relplot`, `lmplot`, `pairplot`) make their own figure, support `col=`/`row=`, and return a grid object (`g.figure`).
- `hue` = colours in one axes; `col` / `row` = separate panels (small multiples).
- `sns.set_theme(style=, palette=)` is global; `sns.reset_defaults()` undoes it.

## Gotchas (the part worth revising twice)
- Figure-level functions have no `ax=`; size them with `height=` and `aspect=` (per facet). Close with `plt.close(g.figure)`.
- `sns.barplot` aggregates (mean + bootstrap CI), unlike `ax.bar`; countplot counts rows.
- `df.groupby(...).plot()` returns a Series of Axes, not one Axes.
- Pandas may create a new figure if you forget `ax=` in a subplot setup.
- Seaborn's global theme changes matplotlib rcParams for everything after it.
- Old style names (`seaborn-whitegrid`) and removed arguments (`ci=` in barplot, now `errorbar=`) break across versions.
- Seaborn is optional: guard `import seaborn` with `try/except ImportError`.

## When it matters
Exploratory analysis: one line from a DataFrame to a chart, then seaborn when you need distributions, group comparisons or facets without writing loops.

## One-line recap example
```python
import pandas as pd, seaborn as sns
df = pd.DataFrame({"g": list("aabb"), "v": [1, 2, 3, 5]})
sns.barplot(data=df, x="g", y="v", errorbar="sd")   # means with error bars per group
```
