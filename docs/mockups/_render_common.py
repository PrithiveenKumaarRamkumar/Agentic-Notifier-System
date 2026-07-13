"""Render the six proposal mockups as PNGs using matplotlib.
Terminal/notification UI aesthetic: flat xterm-256color TUI + Windows 11 desktop."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from matplotlib.font_manager import FontProperties
import matplotlib.font_manager as fm
import os

# Flat, crisp rendering — no line smoothing, hard edges for the terminal look
matplotlib.rcParams["lines.antialiased"] = True   # keep text legible
matplotlib.rcParams["patch.antialiased"] = True
matplotlib.rcParams["figure.dpi"] = 100

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- xterm-256color palette (flat, high-contrast, no anti-alias softening) ---
BG        = "#0c0c0c"   # true terminal charcoal/black
PANEL     = "#0c0c0c"   # panels are the same black — flat, borders define regions
PANEL_HI  = "#1c1c1c"   # xterm 234 — faint highlight row
BAR       = "#1c1c1c"
STROKE    = "#3a3a3a"   # xterm 237 — box-drawing border grey
STROKE_BT = "#585858"   # xterm 240 — brighter border
INK       = "#e4e4e4"   # xterm 254 — default foreground
INK_DIM   = "#bcbcbc"   # xterm 250
MUTED     = "#8a8a8a"   # xterm 245
FAINT     = "#585858"   # xterm 240 — dim/comment grey
DIMTEXT   = "#3a3a3a"   # xterm 237 — very dim background text
ACCENT    = "#ffff00"   # xterm 226 — neon yellow (highlight/attention)
ACCENT_BG = "#5f5f00"   # xterm 58 — dark yellow fill behind highlight
BTN_BG    = "#1c1c1c"
INPUT_BG  = "#080808"
GREEN     = "#00ff5f"   # xterm 47 — neon green (running/active)
RED       = "#ff5f5f"   # xterm 203 — neon red (error)
YELLOW    = "#ffff00"   # xterm 226
BLUE      = "#5fafff"   # xterm 75 — neon cyan-blue
CYAN      = "#00d7ff"   # xterm 45 — neon cyan ([Main])
MAGENTA   = "#ff5fff"   # xterm 207 — neon magenta ([Explore])
HL_BG     = "#ffff00"   # yellow highlight-bar background
HL_FG     = "#0c0c0c"   # black text on the yellow bar

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

def tbox(ax, x, y, w, h, title=None, ec=STROKE, fc=BG, lw=1.3, title_color=None):
    """A terminal-style panel: sharp corners, single-line border, optional
    title sitting inline in the top rule (─ Title ─). Flat, no rounding."""
    if fc is not None:
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec="none", zorder=0.5))
    # four sharp border edges
    ax.add_patch(Rectangle((x, y), w, h, fc="none", ec=ec, lw=lw, zorder=2,
                           joinstyle="miter", capstyle="projecting"))
    if title:
        tc = title_color or MUTED
        label = f" {title} "
        # measure using a temporary render-free estimate; ~7.4px per char at size 10.5
        tw = len(label) * 7.4
        cx = x + w/2
        # solid mask over the top rule, drawn ABOVE the border (higher zorder)
        ax.add_patch(Rectangle((cx - tw/2, y - 3), tw, 6, fc=fc, ec="none", zorder=3))
        txt(ax, cx, y, label, mono(10.5, "bold"), tc, ha="center")  # zorder default > 3

def hlbar(ax, x, y, w, h, text, fp, fg=HL_FG, bg=HL_BG):
    """A solid highlight bar (yellow background, dark text) — the xterm
    'selected line' / attention prompt look."""
    box(ax, x, y, w, h, bg)
    txt(ax, x + 8, y + h/2, text, fp, fg, ha="left", va="center")

def txt(ax, x, y, s, fp, color=INK, ha="left", va="center", zorder=5):
    # DejaVu Mono lacks the stopwatch and vertical-ellipsis glyphs; swap them
    s = s.replace("\u23f1", "\u25f7")      # stopwatch -> circle-with-upper-right-arc-ish
    s = s.replace("\u23f1\ufe0f", "\u25f7")
    s = s.replace("\u22ee", ":")           # vertical ellipsis -> colon-ish fallback
    ax.text(x, y, s, fontproperties=fp, color=color, ha=ha, va=va, zorder=zorder)

def clock(ax, x, y, r, color):
    """Draw a small clock face as the dwell/timer icon."""
    ax.add_patch(Circle((x, y), r, fc="none", ec=color, lw=1.2))
    ax.plot([x, x], [y, y-r*0.55], color=color, lw=1.2)      # minute hand up
    ax.plot([x, x+r*0.45], [y, y], color=color, lw=1.2)      # hour hand right

def dot(ax, x, y, r, c):
    ax.add_patch(Circle((x, y), r, fc=c, ec="none"))

def save(fig, name):
    out = os.path.join(OUT_DIR, name)
    fig.savefig(out, dpi=150, facecolor="none", bbox_inches=None,
                pad_inches=0, transparent=True)
    plt.close(fig)
    print("wrote", out)
