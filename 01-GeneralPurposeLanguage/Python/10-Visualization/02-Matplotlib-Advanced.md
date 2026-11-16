# Matplotlib Advanced — Notes

## What this covers
Multi-panel layouts, twin and inset axes, annotation, colormaps and norms, colorbars, image/mesh/contour plots, 2D histograms, vector fields, 3D axes, tick locators and formatters, dates, log/symlog scales, patches, a minimal FuncAnimation, and event notes.

## Key points
- `plt.subplots(r, c)` returns an array of Axes; use `axs.flat` to loop; `squeeze=False` always gives 2D.
- `sharex` / `sharey` link limits and hide inner labels. Use `layout="constrained"` to stop overlaps (`tight_layout` is the older tool).
- `GridSpec` and `plt.subplot_mosaic("AAB;CDB")` build irregular grids.
- `ax.twinx()` adds a second y-scale; `ax.inset_axes([x, y, w, h])` adds a small plot inside.
- `ax.annotate(text, xy, xytext, arrowprops=...)` points at data; `textcoords="offset points"` keeps the offset fixed.
- A colormap maps 0-1 to colours; a **Norm** maps your data to 0-1. `LogNorm` for wide ranges, `TwoSlopeNorm(vcenter=0)` for diverging data.
- `fig.colorbar(mappable, ax=ax, label=...)`. `imshow` shows an array as an image (row 0 on top); `pcolormesh` handles uneven grids.
- `contour` = lines, `contourf` = filled; `hist2d` / `hexbin` for dense scatter; `quiver` / `streamplot` for vector fields.
- 3D: `fig.add_subplot(projection="3d")`, `plot_surface`, `view_init`.
- Locators choose tick positions, Formatters choose tick text. Dates go straight in; use `mdates` for format.
- `set_yscale("log")` needs positive data; `"symlog"` copes with zero/negatives.
- Patches need `ax.add_patch(...)` and manual limits; `set_aspect("equal")` keeps circles round.
- `FuncAnimation` needs a kept reference; saving needs ffmpeg/pillow (not done here).

## Gotchas (the part worth revising twice)
- Drop the reference to a `FuncAnimation` and nothing runs (or a "deleted without rendering" warning appears).
- `LogNorm` on negative values yields masked output, not an error; log axes silently hide non-positive points.
- `imshow` has the origin at the top-left; `origin="lower"` or `extent=` changes that.
- `pcolormesh` with `shading="flat"` needs C one smaller than X/Y.
- Adding patches does not autoscale the axes.
- Event callbacks and widgets do nothing under Agg; keep widget objects referenced.
- Do not mix `constrained` layout and `tight_layout`.

## When it matters
Dashboards, scientific figures, heatmaps, time series with ticks, and any figure needing more than one simple panel.

## One-line recap example
```python
import matplotlib.pyplot as plt, numpy as np
fig, axs = plt.subplots(1, 2, sharey=True, layout="constrained")
im = axs[0].imshow(np.random.rand(5, 5)); fig.colorbar(im, ax=axs[0], label="value")
```
