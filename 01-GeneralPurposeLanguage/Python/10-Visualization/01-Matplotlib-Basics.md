# Matplotlib Basics — Notes

## What this covers
The core of matplotlib: the two APIs (pyplot vs object-oriented), the Figure/Axes/Axis/Artist anatomy, the common plot types (line, scatter, bar, hist, box, pie, errorbar, fill_between), labelling and limits, colour/marker formats, styles and rcParams, saving figures, and closing figures.

## Key points
- Prefer the OO style: `fig, ax = plt.subplots()` then `ax.plot(...)`. pyplot's `plt.plot` works on hidden "current" state.
- **Figure** = canvas, **Axes** = one plot area, **Axis** = the x or y axis object, **Artist** = everything drawn. Containers: `ax.lines`, `ax.patches`, `ax.collections`, `ax.texts`.
- OO setters are `set_title`, `set_xlabel`, `set_xlim`; `fig.suptitle` titles the whole figure.
- `ax.plot` returns a list of `Line2D`; read data back with `get_xdata()` / `get_ydata()`.
- `ax.hist` returns `(counts, edges, patches)`; `ax.boxplot` returns a dict of artists; `ax.errorbar` returns an `ErrorbarContainer`.
- Format string `"ro--"` = colour + marker + linestyle. Colours: names, hex, `"0.5"` grey, `"C0"` cycle refs.
- `plt.style.use(...)` changes defaults globally; `plt.style.context(...)` and `plt.rc_context({...})` are temporary.
- `savefig(target, format=, dpi=, bbox_inches="tight")` accepts a path or `io.BytesIO` (then `format=` is required).
- Pyplot keeps every figure alive until `plt.close(fig)` / `plt.close("all")`.

## Gotchas (the part worth revising twice)
- "Axes" is one plot, not the plural of "axis".
- `ax.legend()` with no labelled artists warns; labels starting with `_` are hidden from the legend.
- `set_xticklabels` before `set_xticks` misaligns labels - set ticks first.
- Unclosed figures in a loop leak memory (warning after 20 open figures). `Figure()` made directly is not tracked by pyplot.
- `plt.show()` under the Agg backend does nothing (and warns); in a notebook figures display automatically.
- A typo'd rcParams key raises `KeyError`; plt.style names like `seaborn-whitegrid` became `seaborn-v0_8-whitegrid`.
- `plt.title` (pyplot) vs `ax.set_title` (OO): mixing both styles in one script hides which axes you are changing.

## When it matters
Any time you plot from scripts, services or tests: explicit `fig, ax` objects make plots composable, testable and leak-free.

## One-line recap example
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9], label="squares")
ax.set(title="Demo", xlabel="n", ylabel="n squared")
ax.legend(); fig.savefig("out.png", dpi=150, bbox_inches="tight"); plt.close(fig)
```
