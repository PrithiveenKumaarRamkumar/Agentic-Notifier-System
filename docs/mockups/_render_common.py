"""Render the six proposal mockups as PNGs using matplotlib.
Terminal/notification UI aesthetic, dark theme, monospace."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from matplotlib.font_manager import FontProperties
import matplotlib.font_manager as fm

# --- palette ---
BG        = "#0f1117"
PANEL     = "#161922"
PANEL_HI  = "#1d2130"
BAR       = "#1b1e27"
STROKE    = "#2b3040"
STROKE_BT = "#33405e"
INK       = "#e6e9f0"
INK_DIM   = "#aeb4c4"
MUTED     = "#8a90a0"
FAINT     = "#5a6172"
DIMTEXT   = "#3a3f4b"
ACCENT    = "#f5b74a"
ACCENT_BG = "#3a2a12"
BTN_BG    = "#202636"
INPUT_BG  = "#0d0f15"
GREEN     = "#27c93f"
RED       = "#ff5f56"
YELLOW    = "#ffbd2e"
BLUE      = "#5b8def"

# pick a monospace font available on the system
def mono(size, weight="normal", color=INK, style="normal"):
    for fam in ["DejaVu Sans Mono", "Liberation Mono", "monospace"]:
        try:
            fm.findfont(FontProperties(family=fam), fallback_to_default=False)
            return FontProperties(family=fam, size=size, weight=weight, style=style)
        except Exception:
            continue
    return FontProperties(family="monospace", size=size, weight=weight, style=style)

def sans(size, weight="normal", style="normal"):
    return FontProperties(family="DejaVu Sans", size=size, weight=weight, style=style)

def new_canvas(w, h):
    fig = plt.figure(figsize=(w/100, h/100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w); ax.set_ylim(0, h)
    ax.invert_yaxis()            # so y grows downward like screen coords
    ax.axis("off")
    fig.patch.set_facecolor("none")
    return fig, ax

def rbox(ax, x, y, w, h, fc, ec=None, lw=1.0, r=8, dash=None, alpha=1.0):
    style = f"round,pad=0,rounding_size={r}"
    p = FancyBboxPatch((x, y+h), w, -h, boxstyle=style,
                       fc=fc, ec=(ec or fc), lw=(lw if ec else 0),
                       alpha=alpha, mutation_aspect=1)
    # FancyBboxPatch with negative height misbehaves; use plain approach:
    p = FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc,
                       ec=(ec or fc), lw=(lw if ec else 0), alpha=alpha)
    if dash: p.set_linestyle((0, dash))
    ax.add_patch(p)

def box(ax, x, y, w, h, fc, ec=None, lw=1.0, alpha=1.0, dash=None):
    p = Rectangle((x, y), w, h, fc=fc, ec=(ec or fc),
                  lw=(lw if ec else 0), alpha=alpha)
    if dash: p.set_linestyle((0, dash))
    ax.add_patch(p)

def txt(ax, x, y, s, fp, color=INK, ha="left", va="center"):
    # DejaVu Mono lacks the stopwatch and vertical-ellipsis glyphs; swap them
    s = s.replace("\u23f1", "\u25f7")      # stopwatch -> circle-with-upper-right-arc-ish
    s = s.replace("\u23f1\ufe0f", "\u25f7")
    s = s.replace("\u22ee", ":")           # vertical ellipsis -> colon-ish fallback
    ax.text(x, y, s, fontproperties=fp, color=color, ha=ha, va=va)

def clock(ax, x, y, r, color):
    """Draw a small clock face as the dwell/timer icon."""
    ax.add_patch(Circle((x, y), r, fc="none", ec=color, lw=1.2))
    ax.plot([x, x], [y, y-r*0.55], color=color, lw=1.2)      # minute hand up
    ax.plot([x, x+r*0.45], [y, y], color=color, lw=1.2)      # hour hand right

def dot(ax, x, y, r, c):
    ax.add_patch(Circle((x, y), r, fc=c, ec="none"))

def save(fig, name):
    out = f"/home/claude/repo/docs/mockups/{name}"
    fig.savefig(out, dpi=150, facecolor="none", bbox_inches=None,
                pad_inches=0, transparent=True)
    plt.close(fig)
    print("wrote", out)
