import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _render_common import *

# glyphs for state
G_RUN, G_WAIT, G_DONE, G_ERR = "\u25cf", "\u25d0", "\u2713", "\u2717"

# ---------------------------------------------------------------- #1 TUI overlay
def tui_overlay():
    W, H = 900, 500
    fig, ax = new_canvas(W, H)
    box(ax, 0, 0, W, H, BG)                       # true-black terminal
    # dim terminal content behind (very faint)
    for i, s in enumerate(["$ npm test", "  PASS  src/auth/login.test.ts",
                           "  PASS  src/auth/token.test.ts", "  RUNS src/auth/session.test.ts"]):
        txt(ax, 20, 34 + i*20, s, mono(11), DIMTEXT)

    # overlay panel — sharp terminal box with inline title in the top rule
    ox, oy, ow, oh = 150, 110, 490, 300
    tbox(ax, ox, oy, ow, oh, title="agent needs you", ec=GREEN, fc=BG,
         lw=1.4, title_color=GREEN)

    # name + state line: neon green dot, command name, blocked state at right
    dot(ax, ox+22, oy+34, 5, GREEN)
    txt(ax, ox+36, oy+34, "claude: refactor auth module", mono(12.5, "bold"), INK)
    txt(ax, ox+ow-20, oy+34, "\u25d0 blocked", mono(11), YELLOW, ha="right")

    # the gist, phrased as a question
    txt(ax, ox+22, oy+66, "Which migration strategy should I use?", mono(12), INK_DIM)

    # templated responses — plain terminal rows; [1] selected = yellow highlight bar
    by = oy+92
    hlbar(ax, ox+18, by, ow-36, 26, "  1  In-place (A)", mono(11.5, "bold"))
    txt(ax, ox+ow-30, by+13, "\u21b5", mono(11), HL_FG, ha="right")
    txt(ax, ox+22, by+26+20, "  2  Shadow table (B)", mono(11.5), INK)
    txt(ax, ox+22, by+26+46, "  3  Skip", mono(11.5), INK)
    txt(ax, ox+22, by+26+72, "  4  Something else\u2026", mono(11.5), MAGENTA)

    # inline prompt bar (clear separation below the options)
    py = by+26+98
    box(ax, ox+18, py, ow-36, 28, INPUT_BG)
    ax.add_patch(Rectangle((ox+18, py), ow-36, 28, fc="none", ec=STROKE, lw=1))
    txt(ax, ox+28, py+14, "\u203a type a reply\u2026", mono(11), FAINT)
    txt(ax, ox+ow-30, py+14, "\u21b5 send", mono(10), MUTED, ha="right")

    # bottom hotkey rule
    ax.plot([ox+1, ox+ow-1], [oy+oh-30, oy+oh-30], color=STROKE, lw=1)
    txt(ax, ox+22, oy+oh-15, "d expand   g jump to pane   Esc dismiss",
        mono(10.5), MUTED)
    txt(ax, ox+ow-20, oy+oh-15, "\u23f1 10s", mono(10.5), YELLOW, ha="right")

    # backlog indicator below the panel
    txt(ax, 20, oy+oh+22, "2 more unresolved \u25be", mono(11), MUTED)

    # annotations to the right
    for yy, s in [(oy+66,"gist as a question"),
                  (by+13,"selected (yellow bar)"),
                  (by+26+72,"custom reply"),
                  (oy+oh-15,"jump present, quieter")]:
        txt(ax, ox+ow+18, yy, "\u2190 "+s, sans(9.5, style="italic"), FAINT)
    save(fig, "tui-overlay-mockup.png")

# ---------------------------------------------------------------- #2 Desktop banner
def desktop_banner():
    W, H = 860, 540
    fig, ax = new_canvas(W, H)

    # ---- Windows 11 desktop backdrop ----
    box(ax, 0, 0, W, H, "#1e5a6e")                    # teal desktop wallpaper
    # Chrome window fills most of the screen
    winx, winy, winw, winh = 0, 0, W, H-40
    # -- title bar (teal, Windows 11 Chrome) --
    box(ax, winx, winy, winw, 34, "#3f7d90")
    # active tab
    box(ax, winx+40, winy+6, 200, 28, "#dfe3e8")
    dot(ax, winx+56, winy+20, 6, "#4285f4")           # google 'G' dot stand-in
    txt(ax, winx+70, winy+20, "Google", sans(9.5), "#3c4043")
    txt(ax, winx+228, winy+18, "\u00d7", sans(11), "#5f6368", ha="center")
    txt(ax, winx+258, winy+20, "+", sans(13), "#e8eaed", ha="center")
    # window controls (Windows: min, max, close — glyphs, top right)
    txt(ax, winx+winw-72, winy+18, "\u2013", sans(12), "#e8eaed", ha="center")   # minimize
    ax.add_patch(Rectangle((winx+winw-48, winy+13), 11, 11, fc="none", ec="#e8eaed", lw=1.1))
    txt(ax, winx+winw-20, winy+18, "\u2715", sans(11), "#e8eaed", ha="center")   # close
    # -- toolbar / address bar --
    box(ax, winx, winy+34, winw, 40, "#dfe3e8")
    txt(ax, winx+22, winy+54, "\u2190", sans(13), "#5f6368", ha="center")
    txt(ax, winx+48, winy+54, "\u2192", sans(13), "#9aa0a6", ha="center")
    txt(ax, winx+74, winy+54, "\u21bb", sans(12), "#5f6368", ha="center")
    box(ax, winx+96, winy+44, winw-200, 22, "#ffffff")
    ax.add_patch(Rectangle((winx+96, winy+44), winw-200, 22, fc="none", ec="#c6cace", lw=1))
    txt(ax, winx+108, winy+55, "https://www.google.com", sans(9.5), "#3c4043")
    # -- page area (white) --
    box(ax, winx, winy+74, winw, winh-74, "#ffffff")
    txt(ax, W/2-40, winy+300, "Google", sans(34, "bold"), "#4285f4", ha="center")
    box(ax, W/2-240, winy+330, 400, 30, "#ffffff")
    ax.add_patch(Rectangle((W/2-240, winy+330), 400, 30, fc="none", ec="#dfe1e5", lw=1.2))
    txt(ax, W/2-226, winy+345, "The migration plan needs a final review |",
        sans(10), "#3c4043")
    txt(ax, W/2-40, winy+390, "(caret still blinking in the page \u2014 banner did NOT steal focus)",
        sans(9, style="italic"), "#9aa0a6", ha="center")

    # ---- Windows 11 taskbar (bottom, centered icons) ----
    box(ax, 0, H-40, W, 40, "#202830")
    cxs = W/2
    # windows logo (four squares)
    for dx,dy in [(-6,-6),(1,-6),(-6,1),(1,1)]:
        box(ax, cxs-40+dx, H-24+dy, 4, 4, "#4cc2ff")
    for i,ic in enumerate(["\u25a3","\u25c9","\u25a0","\u2b24","\u25b6"]):
        txt(ax, cxs+i*34, H-20, ic, sans(12), "#c9d1d9", ha="center")
    # system tray: wifi / volume / battery / clock
    txt(ax, W-150, H-24, "\u25b2", sans(8), "#c9d1d9", ha="center")
    txt(ax, W-122, H-24, "\u2637", sans(10), "#c9d1d9", ha="center")   # wifi-ish
    txt(ax, W-98, H-24, "\u25c8", sans(10), "#c9d1d9", ha="center")    # volume-ish
    txt(ax, W-74, H-24, "\u25ad", sans(11), "#c9d1d9", ha="center")    # battery-ish
    txt(ax, W-40, H-27, "4:34 PM", sans(8.5), "#c9d1d9", ha="center")
    txt(ax, W-40, H-14, "7/12/2026", sans(8), "#c9d1d9", ha="center")

    # slide-down cue
    txt(ax, W/2, winy+92, "\u25bc  slides down from top edge \u2014 topmost, no focus steal   (dwells ~10s, then \u25b2 slides up)",
        sans(9.5, style="italic"), "#5f6368", ha="center")

    # ---- the notifier's own banner (flat dark card, top-right, Windows style) ----
    bx, by, bw, bh = W-410, winy+104, 380, 196
    box(ax, bx+3, by+4, bw, bh, "#000000", alpha=0.25)   # subtle shadow
    box(ax, bx, by, bw, bh, "#161616")                   # dark flat banner
    ax.add_patch(Rectangle((bx, by), bw, bh, fc="none", ec=STROKE, lw=1.2))
    # header
    dot(ax, bx+18, by+22, 5, GREEN)
    txt(ax, bx+32, by+22, "Agent Interrupt Notifier", mono(10.5, "bold"), INK)
    txt(ax, bx+bw-16, by+22, "now \u00b7 \u23f110s", mono(9), MUTED, ha="right")
    # command title + state (command ABOVE the query)
    txt(ax, bx+16, by+52, "claude \u2014 refactor auth module", mono(10.5, "bold"), INK)
    txt(ax, bx+bw-16, by+52, "BLOCKED", mono(9.5, "bold"), RED, ha="right")
    # question
    txt(ax, bx+16, by+78, "Which migration strategy should I use?", mono(10.5), INK_DIM)
    txt(ax, bx+16, by+96, "(expand for both diffs)", mono(9), FAINT)
    # buttons: two templates + Go to pane (primary, neon-green outline)
    ry1 = by+114
    for bxx, lab in [(bx+16,"In-place (A)"), (bx+114,"Shadow (B)")]:
        box(ax, bxx, ry1, 92, 24, BTN_BG)
        ax.add_patch(Rectangle((bxx, ry1), 92, 24, fc="none", ec=STROKE_BT, lw=1))
        txt(ax, bxx+46, ry1+12, lab, mono(9.5), INK_DIM, ha="center")
    box(ax, bx+212, ry1, 152, 24, "#00331a")
    ax.add_patch(Rectangle((bx+212, ry1), 152, 24, fc="none", ec=GREEN, lw=1.2))
    txt(ax, bx+212+76, ry1+12, "Go to pane \u2192", mono(9.5, "bold"), GREEN, ha="center")
    # something else + input
    ry2 = by+146
    box(ax, bx+16, ry2, 128, 22, INPUT_BG)
    ax.add_patch(Rectangle((bx+16, ry2), 128, 22, fc="none", ec="#5f5f5f", lw=1, ls=(0,(3,2))))
    txt(ax, bx+16+64, ry2+11, "Something else\u2026", mono(9), MAGENTA, ha="center")
    box(ax, bx+152, ry2, bw-152-16, 22, INPUT_BG)
    ax.add_patch(Rectangle((bx+152, ry2), bw-152-16, 22, fc="none", ec=STROKE, lw=1))
    txt(ax, bx+160, ry2+11, "\u203a type a reply\u2026", mono(9), FAINT)
    txt(ax, bx+bw-24, ry2+11, "\u21b5", mono(9), MUTED, ha="right")

    save(fig, "desktop-banner-mockup.png")

# ---------------------------------------------------------------- #3 Hybrid expand
def expanded_detail():
    W, H = 860, 440
    fig, ax = new_canvas(W, H)
    box(ax, 0, 0, W, H, BG)

    # ---- LEFT: committed inline expand ----
    lx, ly, lw, lh = 30, 46, 390, 320
    rbox(ax, lx, ly, lw, lh, PANEL, ec=STROKE, lw=1.2, r=12)
    txt(ax, lx+16, ly-14, "click / tap \u2014 committed inline expand", sans(10, "bold"), INK_DIM)
    rbox(ax, lx, ly, lw, 30, PANEL_HI, r=12)
    txt(ax, lx+16, ly+15, "Q: Which migration strategy should I use?", mono(9.5, "bold"), ACCENT)
    txt(ax, lx+lw-14, ly+15, "\u2303", mono(12), MUTED, ha="right")   # collapse caret
    # log slice box
    sx, sy, sw = lx+16, ly+42, lw-32
    rbox(ax, sx, sy, sw, 150, "#0d0f15", ec=STROKE, lw=1, r=8)
    txt(ax, sx+12, sy+16, "from the log \u00b7 lines 214\u2013219", mono(8.5), "#7f96c4")
    ax.plot([sx+10, sx+sw-10], [sy+26, sy+26], color="#242a38", lw=0.8)
    slice_lines = [('psql: column "role" cannot be added', FAINT),
                   ('  with NOT NULL and no default on a', FAINT),
                   ('  populated table.', FAINT),
                   ('I can migrate two ways \u2014 which?', INK),
                   ('  A) in-place ALTER  B) shadow+backfill', INK_DIM),
                   ('\u25b8 waiting for your choice\u2026', ACCENT)]
    for i,(s,c) in enumerate(slice_lines):
        txt(ax, sx+12, sy+42+i*18, s, mono(8.5, "bold" if c==INK else "normal"), c)
    # action row
    ay = ly+lh-40
    rbox(ax, lx+16, ay, 84, 24, BTN_BG, ec=STROKE_BT, lw=1, r=6)
    txt(ax, lx+16+42, ay+12, "In-place (A)", mono(8.5), INK_DIM, ha="center")
    rbox(ax, lx+106, ay, 84, 24, BTN_BG, ec=STROKE_BT, lw=1, r=6)
    txt(ax, lx+106+42, ay+12, "Shadow (B)", mono(8.5), INK_DIM, ha="center")
    rbox(ax, lx+196, ay, 122, 24, INPUT_BG, ec="#4a5270", lw=1, r=6, dash=(3,2))
    txt(ax, lx+196+61, ay+12, "Something else\u2026", mono(8.5), MUTED, ha="center")

    # ---- RIGHT: press-and-hold peek ----
    rx, ry, rw, rh = 440, 46, 390, 320
    # blurred stack hint behind
    for i in range(3):
        rbox(ax, rx+10+i*3, ry+10+i*6, rw-20-i*6, rh-20, PANEL_HI, ec=STROKE, lw=1, r=12, alpha=0.25)
    rbox(ax, rx, ry, rw, rh, PANEL, ec=ACCENT, lw=1.4, r=12)
    txt(ax, rx+16, ry-14, "press-and-hold \u2014 transient peek", sans(10, "bold"), INK_DIM)
    # header
    txt(ax, rx+16, ry+20, "\u25c9 Peeking full log", mono(9.5, "bold"), ACCENT)
    txt(ax, rx+rw-14, ry+20, "release to collapse", mono(8.5), MUTED, ha="right")
    txt(ax, rx+16, ry+40, "Which migration strategy should I use?", mono(9), INK_DIM)
    # wider log with dim context + hot source
    px, py, pw = rx+16, ry+52, rw-32
    rbox(ax, px, py, pw, 178, "#0d0f15", ec=STROKE, lw=1, r=8)
    peek_lines = [('[212] running migration: add users.role', FAINT, False),
                  ('[213] $ psql -f migrations/003_role.sql', FAINT, False),
                  ('[214] ERROR: column "role" cannot be', RED, True),
                  ('[215]   added with NOT NULL, no default', RED, True),
                  ('[216]   on a populated table (12,904 rows)', RED, True),
                  ('[217]', FAINT, False),
                  ('[218] I can migrate two ways \u2014 which?', INK, True),
                  ('[219]   A) in-place ALTER (brief lock)', INK_DIM, True),
                  ('[220]   B) shadow table + backfill (safe)', INK_DIM, True),
                  ('[221] \u25b8 waiting for your choice\u2026', ACCENT, True)]
    for i,(s,c,hot) in enumerate(peek_lines):
        yy = py+16+i*16
        if hot:
            box(ax, px+6, yy-7, pw-12, 15, "#1a1f2b", alpha=0.9)
        txt(ax, px+12, yy, s, mono(8, "bold" if (hot and c in (INK,RED,ACCENT)) else "normal"),
            c if hot else FAINT)
    txt(ax, rx+rw/2, ry+rh-16, "lines 214\u2013221 fed the summary \u00b7 the rest is context",
        sans(8.5, style="italic"), MUTED, ha="center")

    txt(ax, W/2, H-16, "Both render the same logSpan. The peek is a pure enhancement over the "
        "accessible inline expand.", sans(9, style="italic"), ha="center")
    save(fig, "expanded-detail-mockup.png")

# ---------------------------------------------------------------- #4 Templated responses
def template_actions():
    W, H = 760, 340
    fig, ax = new_canvas(W, H)
    box(ax, 0, 0, W, H, BG)
    cx, cy, cw = 40, 34, 470
    ch = 262
    rbox(ax, cx, cy, cw, ch, PANEL, ec=STROKE, lw=1.2, r=12)
    rbox(ax, cx, cy, cw, 34, PANEL_HI, r=12)
    txt(ax, cx+18, cy+17, "Q: Which migration strategy should I use?", mono(11, "bold"), ACCENT)
    rows = [("In-place (A)", "parsed from agent\u2019s prompt", STROKE_BT, INK_DIM),
            ("Shadow table (B)", "parsed from agent\u2019s prompt", STROKE_BT, INK_DIM),
            ("Rebase onto main", "from your history (used 3\u00d7 here)", "#3d5a3d", "#bfe6c0"),
            ("Skip / defer", "common redirect", STROKE_BT, INK_DIM),
            ("Something else\u2026", "always present \u2192 opens the bar", "#5a4a70", "#d5c8ea")]
    for i,(lab, why, ec, tc) in enumerate(rows):
        ry = cy+50 + i*36
        dash = (3,2) if i==4 else None
        rbox(ax, cx+18, ry, 190, 26, INPUT_BG if i==4 else BTN_BG, ec=ec, lw=1.1, r=6, dash=dash)
        txt(ax, cx+28, ry+13, lab, mono(10.5), tc)
        txt(ax, cx+220, ry+13, "\u2190 "+why, sans(9, style="italic"), FAINT)
    # input bar
    iy = cy+50+5*36
    rbox(ax, cx+18, iy, cw-36, 26, INPUT_BG, ec=STROKE, lw=1, r=6)
    txt(ax, cx+28, iy+13, "\u203a type your own reply\u2026", mono(10), FAINT)
    txt(ax, cx+cw-26, iy+13, "\u21b5", mono(10), MUTED, ha="right")
    # side caption
    txt(ax, cx+cw+20, cy+90, "Adapter parses", sans(10,"bold"), ha="left")
    txt(ax, cx+cw+20, cy+108, "candidates from the", sans(10), ha="left")
    txt(ax, cx+cw+20, cy+124, "log; orchestrator", sans(10), ha="left")
    txt(ax, cx+cw+20, cy+140, "phrases + templates.", sans(10), ha="left")
    txt(ax, cx+cw+20, cy+168, "\u201cSomething else\u2026\u201d", sans(10,"bold"), color="#d5c8ea", ha="left")
    txt(ax, cx+cw+20, cy+186, "always escapes the", sans(10), ha="left")
    txt(ax, cx+cw+20, cy+202, "templates.", sans(10), ha="left")
    save(fig, "template-actions-mockup.png")

# ---------------------------------------------------------------- #5 Pull surface
def pull_surface():
    W, H = 760, 340
    fig, ax = new_canvas(W, H)
    box(ax, 0, 0, W, H, BG, alpha=1)
    # dimmed backdrop to signal "overlay, will vanish"
    box(ax, 0, 0, W, H, "#000000", alpha=0.15)
    txt(ax, W/2, 40, "\u25b2 pull to check", mono(10.5), MUTED, ha="center")
    cx, cy, cw = 90, 60, 580
    rows = [(G_WAIT, ACCENT, "claude", "refactor auth", "blocked", "now", None),
            (G_ERR, RED, "codex", "build", "error", "2m", None),
            (G_WAIT, ACCENT, "opencode", "tests", "waiting", "5m", "\u27f6 resolving")]
    ch = 44 + len(rows)*34
    rbox(ax, cx, cy, cw, ch, PANEL, ec=STROKE, lw=1.2, r=12)
    rbox(ax, cx, cy, cw, 32, PANEL_HI, r=12)
    txt(ax, cx+16, cy+16, "Unresolved (3)", mono(10.5, "bold"), INK)
    txt(ax, cx+cw-16, cy+16, "summoned, will dismiss", sans(9, style="italic"), FAINT, ha="right")
    for i,(glyph, gc, name, task, st, ago, note) in enumerate(rows):
        ry = cy+42 + i*34
        fading = note is not None
        rbox(ax, cx+12, ry, cw-24, 28, PANEL_HI, ec=STROKE, lw=1, r=7,
             alpha=0.45 if fading else 1.0)
        txt(ax, cx+28, ry+14, glyph, mono(12), gc)
        txt(ax, cx+50, ry+14, name, mono(10.5), INK if not fading else FAINT)
        txt(ax, cx+150, ry+14, task, mono(10), INK_DIM if not fading else FAINT)
        if fading:
            # on the resolving row, replace state/time with the note so nothing overlaps
            txt(ax, cx+300, ry+14, "\u27f6 resolving", sans(10, style="italic"), "#8fe89a")
            txt(ax, cx+cw-24, ry+14, "(leaves once resolved)", sans(9, style="italic"),
                "#8fe89a", ha="right")
        else:
            txt(ax, cx+300, ry+14, st, mono(10), INK_DIM)
            txt(ax, cx+400, ry+14, ago, mono(9.5), FAINT)
    txt(ax, cx, cy+ch+22, "j/k select    Enter reopen    x remove (if resolved)",
        mono(9.5), MUTED)
    txt(ax, W/2, H-18, "Summoned, not standing \u2014 items persist until resolved. Not a dashboard.",
        sans(9, style="italic"), ha="center")
    save(fig, "pull-surface-mockup.png")

# ---------------------------------------------------------------- #6 Stepper (4+ questions)
def stepper():
    W, H = 760, 500
    fig, ax = new_canvas(W, H)
    box(ax, 0, 0, W, H, BG)

    # main stepper panel (sharp terminal box, green title)
    ox, oy, ow, oh = 40, 60, 560, 360
    tbox(ax, ox, oy, ow, oh, title="agent needs you \u00b7 3 of 4", ec=GREEN, fc=BG,
         lw=1.4, title_color=GREEN)

    # segmented progress bar: 2 done, 1 current, 1 ahead (leaves room for the count in the title)
    seg_w = (ow-40-3*8)/4
    states = [GREEN, GREEN, YELLOW, STROKE_BT]   # done, done, current, ahead
    for i,c in enumerate(states):
        sx = ox+20 + i*(seg_w+8)
        box(ax, sx, oy+18, seg_w, 5, c)

    # command name above the query
    dot(ax, ox+20, oy+46, 5, GREEN)
    txt(ax, ox+34, oy+46, "claude: refactor auth module", mono(11.5, "bold"), INK)
    txt(ax, ox+ow-20, oy+46, "\u25d0 blocked", mono(10), YELLOW, ha="right")

    # the current question (3rd of 4)
    txt(ax, ox+20, oy+74, "Assume native psmux, or WSL tmux too?", mono(12), INK_DIM)

    # options — [1] selected as a yellow highlight bar
    by = oy+98
    hlbar(ax, ox+18, by, ow-36, 26, "  1  Native psmux only \u2014 simplest path", mono(11, "bold"))
    txt(ax, ox+ow-30, by+13, "\u21b5", mono(11), HL_FG, ha="right")
    txt(ax, ox+22, by+26+20, "  2  Support both from day one", mono(11), INK)
    txt(ax, ox+22, by+26+46, "  3  WSL tmux only \u2014 no native dep", mono(11), INK)
    txt(ax, ox+22, by+26+72, "  \u270e  Something else", mono(11), MAGENTA)

    # "Answered" chip row — pins the earlier answers so a stepper isn't a void
    chy = by+26+100
    txt(ax, ox+20, chy+10, "Answered", sans(9), MUTED)
    chips = ["1 \u00b7 GUI banner first", "2 \u00b7 Claude Code"]
    cxp = ox+90
    for c in chips:
        cw = 12 + len(c)*6.0
        rbox(ax, cxp, chy, cw, 20, "#00331a", ec=GREEN, lw=0.8, r=10)
        txt(ax, cxp+cw/2, chy+10, c, sans(8.5), GREEN, ha="center")
        cxp += cw + 8

    # bottom nav rule + Back / Skip / Next
    ay = oy+oh-34
    ax.plot([ox+1, ox+ow-1], [ay-8, ay-8], color=STROKE, lw=1)
    # Back (left)
    rbox(ax, ox+18, ay, 74, 24, BG, ec=STROKE, lw=1, r=6)
    txt(ax, ox+18+37, ay+12, "\u2190 Back", mono(9.5), MUTED, ha="center")
    # Skip (right group)
    rbox(ax, ox+ow-186, ay, 66, 24, BG, ec=STROKE_BT, lw=1, r=6)
    txt(ax, ox+ow-186+33, ay+12, "Skip", mono(9.5), INK_DIM, ha="center")
    # Next (primary, green)
    rbox(ax, ox+ow-112, ay, 94, 24, "#00331a", ec=GREEN, lw=1.2, r=6)
    txt(ax, ox+ow-112+47, ay+12, "Next \u2192", mono(9.5, "bold"), GREEN, ha="center")

    # reply bar below the panel
    ry = oy+oh+14
    box(ax, ox, ry, ow, 30, INPUT_BG)
    ax.add_patch(Rectangle((ox, ry), ow, 30, fc="none", ec=STROKE, lw=1))
    txt(ax, ox+14, ry+15, "\u203a Or reply directly\u2026", mono(10.5), FAINT)
    # footer hint
    txt(ax, ox+ow/2, ry+52, "\u2191\u2193 options   \u00b7   \u2190\u2192 questions   \u00b7   Enter select   \u00b7   Skip all to defer",
        sans(9), MUTED, ha="center")

    # caption — why a stepper (appears for a stack of questions)
    txt(ax, ox+ow+18, oy+90, "Stepper: one", sans(9.5, "bold"), ha="left")
    txt(ax, ox+ow+18, oy+106, "question at a", sans(9.5), ha="left")
    txt(ax, ox+ow+18, oy+122, "time \u2014 used when", sans(9.5), ha="left")
    txt(ax, ox+ow+18, oy+138, "an interrupt", sans(9.5), ha="left")
    txt(ax, ox+ow+18, oy+154, "raises multiple", sans(9.5), ha="left")
    txt(ax, ox+ow+18, oy+170, "questions.", sans(9.5), ha="left")
    save(fig, "stepper-mockup.png")

# ---------------------------------------------------------------- #0 Concept sketch
def concept():
    W, H = 1080, 470
    fig, ax = new_canvas(W, H)
    box(ax, 0, 0, W, H, "#12141b")
    txt(ax, W/2, 28, "The model: the Claude follow-up card \u2192 terminal agent interrupts",
        sans(13, "bold"), INK, ha="center")

    # ---- LEFT: a faithful light "Claude follow-up card" ----
    px, py, pw = 40, 62, 420
    # the small Claude asterisk mark above the card
    txt(ax, px+14, py-4, "\u2733", sans(15, "bold"), "#d97757", ha="center")
    # the question card (light)
    qh = 250
    rbox(ax, px, py+14, pw, qh, "#ffffff", ec="#e6e6e6", lw=1, r=14)
    # stepper progress bars at the top: current (blue) + next in the stack (grey)
    seg_w = (pw-44-2*8)/3
    seg_colors = ["#2563d9", "#d6d6d6", "#d6d6d6"]   # present in stack, then ahead
    for i,c in enumerate(seg_colors):
        box(ax, px+22 + i*(seg_w+8), py+30, seg_w, 4, c)
    txt(ax, px+22, py+62, "Where should the log-parsing / summarize-", sans(11, "bold"), "#1a1a1a")
    txt(ax, px+22, py+80, "as-a-question logic live?", sans(11, "bold"), "#1a1a1a")
    txt(ax, px+pw-22, py+64, "\u00d7", sans(12), "#9a9a9a", ha="right")
    # options
    opts = [("1", "Adapter \u2014 per-harness parsing", True),
            ("2", "Orchestrator \u2014 shared phrasing", False),
            ("3", "Split \u2014 adapter extracts, orch phrases", False),
            ("4", "Not sure \u2014 recommend one", False)]
    oy = py+96
    for i,(n,lab,sel) in enumerate(opts):
        ry = oy + i*34
        if sel:
            rbox(ax, px+14, ry, pw-28, 30, "#f0f0f0", r=8)
            txt(ax, px+pw-26, ry+15, "\u21b5", sans(11), "#9a9a9a", ha="right")
        rbox(ax, px+22, ry+6, 20, 18, "#efefef" if sel else "#f6f6f6", r=5)
        txt(ax, px+32, ry+15, n, sans(9.5), "#6a6a6a", ha="center")
        txt(ax, px+52, ry+15, lab, sans(10.5), "#1a1a1a" if sel else "#2a2a2a")
    # "Something else" row with pencil + Skip button
    sry = oy + 4*34 + 2
    txt(ax, px+32, sry+15, "\u270e", sans(11), "#9a9a9a", ha="center")
    txt(ax, px+52, sry+15, "Something else", sans(10.5), "#9a9a9a")
    rbox(ax, px+pw-84, sry+2, 62, 26, "#ffffff", ec="#d6d6d6", lw=1, r=8)
    txt(ax, px+pw-53, sry+15, "Skip", sans(10, "bold"), "#1a1a1a", ha="center")

    # the "Or reply directly" bar (separate rounded card below)
    ry2 = py+14+qh+12
    rbox(ax, px, ry2, pw, 54, "#ffffff", ec="#e6e6e6", lw=1, r=14)
    txt(ax, px+22, ry2+20, "Or reply directly\u2026", sans(11), "#9a9a9a")
    txt(ax, px+22, ry2+40, "+", sans(13), "#4a4a4a")
    txt(ax, px+pw-150, ry2+40, "Opus 4.8", sans(9.5), "#4a4a4a")
    txt(ax, px+pw-95, ry2+40, "High \u2304", sans(9.5), "#9a9a9a")
    txt(ax, px+pw-45, ry2+40, "\u2b1c", sans(10), "#9a9a9a", ha="center")
    txt(ax, px+pw-24, ry2+40, "\u2637", sans(10), "#9a9a9a", ha="center")
    # nav hint
    txt(ax, px+pw/2, ry2+74, "\u2191\u2193 to navigate   \u00b7   Enter to select   \u00b7   or type below",
        sans(9), MUTED, ha="center")

    # ---- RIGHT: mapping card element -> terminal-agent equivalent ----
    mapx = 500
    pairs = [("question", "\u2192 the agent\u2019s log gist, phrased as a question"),
             ("command name", "\u2192 the command that\u2019s calling you (shown above)"),
             ("numbered options", "\u2192 templated responses parsed from the log"),
             ("\u270e Something else", "\u2192 custom reply routed to the session"),
             ("Skip", "\u2192 ignore, or auto-pick the most relevant"),
             ("stepper", "\u2192 one question at a time for a stack of interrupts"),
             ("Enter / \u2191\u2193 / \u2190\u2192", "\u2192 select, move in a question, move between")]
    txt(ax, mapx+90, 92, "Follow-up card element", sans(10.5, "bold"), ACCENT, ha="center")
    txt(ax, mapx+320, 92, "Terminal-agent equivalent", sans(10.5, "bold"), ACCENT, ha="left")
    ax.plot([mapx, W-24],[104,104], color=STROKE, lw=1)
    for i,(a,b) in enumerate(pairs):
        yy = 130 + i*44
        rbox(ax, mapx, yy-16, 180, 32, PANEL, ec=STROKE, lw=1, r=8)
        txt(ax, mapx+90, yy, a, mono(8.5), INK, ha="center")
        txt(ax, mapx+196, yy, b, sans(9), INK_DIM, ha="left")
    save(fig, "original-concept.png")

if __name__ == "__main__":
    concept()
    tui_overlay()
    desktop_banner()
    expanded_detail()
    template_actions()
    pull_surface()
    stepper()
    print("all done")
