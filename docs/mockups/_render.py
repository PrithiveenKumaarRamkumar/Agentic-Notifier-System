import sys
sys.path.insert(0, "/home/claude/repo/docs/mockups")
from _render_common import *

# glyphs for state
G_RUN, G_WAIT, G_DONE, G_ERR = "\u25cf", "\u25d0", "\u2713", "\u2717"

# ---------------------------------------------------------------- #1 TUI overlay
def tui_overlay():
    W, H = 900, 470
    fig, ax = new_canvas(W, H)
    # terminal shell
    box(ax, 0, 0, W, H, BG)
    box(ax, 0, 0, W, 30, BAR)
    dot(ax, 20, 15, 5, RED); dot(ax, 38, 15, 5, YELLOW); dot(ax, 56, 15, 5, GREEN)
    txt(ax, W/2, 15, "tmux \u00b7 pane 2 \u2014 running agents", mono(9.5), MUTED, ha="center")
    # dim content
    for i, s in enumerate(["$ npm test", "  PASS  src/auth/login.test.ts",
                           "  PASS  src/auth/token.test.ts", "  ."]):
        txt(ax, 24, 58 + i*22, s, mono(11), DIMTEXT)
    txt(ax, 24, 430, "$ \u2588", mono(11), DIMTEXT)
    box(ax, 0, 30, W, H-30, BG, alpha=0.55)   # veil

    # overlay card
    ox, oy, ow, oh = 155, 120, 480, 214
    rbox(ax, ox, oy, ow, oh, PANEL, ec=STROKE, lw=1.2, r=10)
    rbox(ax, ox, oy, ow, 34, PANEL_HI, r=10)
    dot(ax, ox+22, oy+17, 5, ACCENT)
    txt(ax, ox+34, oy+17, "agent needs you", mono(11.5, "bold"), ACCENT)
    clock(ax, ox+ow-52, oy+17, 5, MUTED)
    txt(ax, ox+ow-16, oy+17, "10s", mono(10), MUTED, ha="right")

    # name + state badge
    txt(ax, ox+18, oy+58, "claude: refactor auth module", mono(12), INK)
    bx = ox+ow-128
    rbox(ax, bx, oy+48, 108, 20, ACCENT_BG, ec=ACCENT, lw=0.8, r=10)
    txt(ax, bx+54, oy+58, "\u25d0 blocked", mono(10), ACCENT, ha="center")

    # question
    txt(ax, ox+18, oy+86, "Which migration strategy should I use?", mono(11.5), INK_DIM)

    # templated buttons
    by = oy+104
    for bxx, bw, lab in [(ox+18,120,"1 In-place (A)"), (ox+146,124,"2 Shadow (B)"),
                         (ox+278,64,"3 Skip")]:
        rbox(ax, bxx, by, bw, 26, BTN_BG, ec=STROKE_BT, lw=1, r=6)
        txt(ax, bxx+bw/2, by+13, lab, mono(10.5), INK_DIM, ha="center")
    # something else (dashed)
    rbox(ax, ox+18, by+34, 150, 26, INPUT_BG, ec="#4a5270", lw=1, r=6, dash=(3,2))
    txt(ax, ox+18+75, by+34+13, "4 Something else\u2026", mono(9.5), MUTED, ha="center")
    # prompt bar
    rbox(ax, ox+178, by+34, ow-178-18, 26, INPUT_BG, ec=STROKE, lw=1, r=6)
    txt(ax, ox+188, by+34+13, "\u203a type a reply\u2026", mono(10), FAINT)
    txt(ax, ox+ow-28, by+34+13, "\u21b5", mono(10), MUTED, ha="right")

    # divider + hotkeys
    ax.plot([ox+18, ox+ow-18], [oy+178, oy+178], color="#242a38", lw=1)
    txt(ax, ox+18, oy+194, "d expand     g jump to pane     Esc dismiss", mono(10), MUTED)

    # backlog indicator
    txt(ax, 24, 352, "2 more unresolved \u25be", mono(11), MUTED)

    # annotations (now inside widened canvas)
    for yy, s in [(oy+86,"\u2190 gist as a question"),
                  (by+13,"\u2190 templated responses"),
                  (by+47,"\u2190 custom reply"),
                  (oy+194,"\u2190 jump present, quieter")]:
        txt(ax, ox+ow+16, yy, s, sans(9.5, style="italic"), FAINT)
    save(fig, "tui-overlay-mockup.png")

# ---------------------------------------------------------------- #2 Desktop banner
def desktop_banner():
    W, H = 820, 500
    fig, ax = new_canvas(W, H)
    # "desktop" = a browser window (background app)
    box(ax, 0, 0, W, H, "#20242c")
    box(ax, 30, 60, W-60, H-90, "#f6f7f9")          # browser page
    box(ax, 30, 60, W-60, 34, "#e4e7ec")            # browser chrome
    dot(ax, 50, 77, 5, "#c9ced8"); dot(ax, 66, 77, 5, "#c9ced8"); dot(ax, 82, 77, 5, "#c9ced8")
    rbox(ax, 100, 68, 380, 18, "#ffffff", ec="#d2d6de", lw=1, r=9)
    txt(ax, 110, 77, "docs.example.com/guide", sans(9), "#8b93a3")
    # page text with a blinking caret (focus stays here)
    txt(ax, 55, 130, "Editing notes\u2026", sans(12, "bold"), "#2b2f38")
    txt(ax, 55, 156, "The migration plan needs a", sans(10.5), "#4a4f5a")
    txt(ax, 55, 176, "final review. |", sans(10.5), "#4a4f5a")
    txt(ax, 55, 210, "(caret still blinking here \u2014", sans(9, style="italic"), "#9aa0ab")
    txt(ax, 55, 226, " focus was NOT stolen)", sans(9, style="italic"), "#9aa0ab")

    # slide-down cue
    txt(ax, W/2, 46, "\u25bc  slides down from top edge \u2014 topmost, no focus steal  (dwells ~10s, then \u25b2 slides up)",
        sans(9.5, style="italic"), "#aeb4c4", ha="center")

    # banner card (own notification surface) — roomy, well-spaced
    bx, by, bw, bh = 235, 70, 380, 200
    rbox(ax, bx+4, by+6, bw, bh, "#000000", r=14, alpha=0.28)   # shadow
    rbox(ax, bx, by, bw, bh, PANEL, ec=STROKE, lw=1.2, r=14)
    # header
    dot(ax, bx+20, by+24, 5, ACCENT)
    txt(ax, bx+32, by+24, "Agent Interrupt Notifier", mono(10.5, "bold"), INK)
    clock(ax, bx+bw-52, by+24, 5, MUTED)
    txt(ax, bx+bw-16, by+24, "10s", mono(9), MUTED, ha="right")
    # title + state (own rows, no collision)
    txt(ax, bx+16, by+56, "claude \u2014 refactor auth module", mono(10.5), INK)
    rbox(ax, bx+bw-90, by+47, 74, 19, "#3a1414", ec="#ff6b6b", lw=0.8, r=9)
    txt(ax, bx+bw-90+37, by+57, "BLOCKED", mono(9, "bold"), "#ff8f8f", ha="center")
    # question
    txt(ax, bx+16, by+84, "Which migration strategy should I use?", mono(10.5), INK_DIM)
    txt(ax, bx+16, by+102, "(expand for both diffs)", mono(9), FAINT)
    # buttons row: two templates + Go to pane (primary)
    ry1 = by+118
    rbox(ax, bx+16, ry1, 92, 24, BTN_BG, ec=STROKE_BT, lw=1, r=6)
    txt(ax, bx+16+46, ry1+12, "In-place (A)", mono(9.5), INK_DIM, ha="center")
    rbox(ax, bx+114, ry1, 92, 24, BTN_BG, ec=STROKE_BT, lw=1, r=6)
    txt(ax, bx+114+46, ry1+12, "Shadow (B)", mono(9.5), INK_DIM, ha="center")
    rbox(ax, bx+212, ry1, 152, 24, "#243a24", ec=GREEN, lw=1.1, r=6)   # primary
    txt(ax, bx+212+76, ry1+12, "Go to pane \u2192", mono(9.5, "bold"), "#8fe89a", ha="center")
    # something else + input (own row)
    ry2 = by+150
    rbox(ax, bx+16, ry2, 128, 22, INPUT_BG, ec="#4a5270", lw=1, r=5, dash=(3,2))
    txt(ax, bx+16+64, ry2+11, "Something else\u2026", mono(9), MUTED, ha="center")
    rbox(ax, bx+152, ry2, bw-152-16, 22, INPUT_BG, ec=STROKE, lw=1, r=5)
    txt(ax, bx+160, ry2+11, "\u203a type a reply\u2026", mono(9), FAINT)
    txt(ax, bx+bw-24, ry2+11, "\u21b5", mono(9), MUTED, ha="right")

    # backlog stack below (pushed down to clear taller card)
    sx, sy = 235, 300
    txt(ax, sx, sy, "\u25b8 Backlog stack (unresolved, newest first)", mono(10, "bold"), MUTED)
    rows = [(GREEN, RED, "codex", "build failed", "2m ago", G_ERR, RED),
            (None, None, "claude", "waiting on input", "5m ago", G_WAIT, ACCENT),
            (None, None, "opencode", "waiting on input", "6m ago", G_WAIT, ACCENT)]
    for i, (_, __, name, st, ago, glyph, gc) in enumerate(rows):
        ry = sy + 20 + i*30
        rbox(ax, sx, ry, 350, 26, PANEL_HI if i else PANEL, ec=STROKE, lw=1, r=7)
        txt(ax, sx+16, ry+13, glyph, mono(11), gc)
        txt(ax, sx+36, ry+13, name, mono(10), INK)
        txt(ax, sx+130, ry+13, st, mono(9.5), INK_DIM)
        txt(ax, sx+350-14, ry+13, ago, mono(9), FAINT, ha="right")
    save(fig, "desktop-banner-mockup.png")

# ---------------------------------------------------------------- #3 Expanded detail
def expanded_detail():
    W, H = 780, 420
    fig, ax = new_canvas(W, H)
    box(ax, 0, 0, W, H, BG)
    cx, cy, cw, ch = 40, 30, W-80, H-70
    rbox(ax, cx, cy, cw, ch, PANEL, ec=STROKE, lw=1.2, r=12)
    # header
    rbox(ax, cx, cy, cw, 34, PANEL_HI, r=12)
    txt(ax, cx+18, cy+17, "claude: refactor auth module \u2014 detail", mono(11, "bold"), INK)
    txt(ax, cx+cw-16, cy+17, "\u25b4 collapse", mono(9.5), MUTED, ha="right")
    # question + state line
    txt(ax, cx+18, cy+56, "Q: Which migration strategy should I use?", mono(11.5), ACCENT)
    txt(ax, cx+18, cy+78, "State: blocked (needs_input)", mono(10), INK_DIM)
    txt(ax, cx+cw-16, cy+78, "runtime 4m 12s", mono(10), FAINT, ha="right")
    ax.plot([cx+18, cx+cw-18], [cy+92, cy+92], color="#242a38", lw=1)
    # diff content
    lines = [("Option A \u2014 in-place column migration", INK, mono(10.5,"bold")),
             ("  + ALTER TABLE users ADD COLUMN role text;", GREEN, mono(10)),
             ("  - (no data backfill \u2014 nulls until app writes)", RED, mono(10)),
             ("Option B \u2014 shadow table + backfill", INK, mono(10.5,"bold")),
             ("  + CREATE TABLE users_new (\u2026);", GREEN, mono(10)),
             ("  + backfill job, then atomic swap", GREEN, mono(10)),
             ("  \u22ee", FAINT, mono(10))]
    for i,(s,c,fp) in enumerate(lines):
        txt(ax, cx+18, cy+112+i*20, s, fp, c)
    txt(ax, cx+cw-24, cy+112+6*20, "\u25be", mono(10), MUTED, ha="right")  # scroll cue
    ax.plot([cx+18, cx+cw-18], [cy+ch-44, cy+ch-44], color="#242a38", lw=1)
    # action row
    ay = cy+ch-34
    rbox(ax, cx+18, ay, 96, 24, BTN_BG, ec=STROKE_BT, lw=1, r=6)
    txt(ax, cx+18+48, ay+12, "In-place (A)", mono(9.5), INK_DIM, ha="center")
    rbox(ax, cx+122, ay, 96, 24, BTN_BG, ec=STROKE_BT, lw=1, r=6)
    txt(ax, cx+122+48, ay+12, "Shadow (B)", mono(9.5), INK_DIM, ha="center")
    rbox(ax, cx+226, ay, 118, 24, INPUT_BG, ec="#4a5270", lw=1, r=6, dash=(3,2))
    txt(ax, cx+226+59, ay+12, "Something else\u2026", mono(9.5), MUTED, ha="center")
    rbox(ax, cx+352, ay, cw-352-18, 24, INPUT_BG, ec=STROKE, lw=1, r=6)
    txt(ax, cx+362, ay+12, "\u203a \u2026", mono(9.5), FAINT)
    txt(ax, cx+cw-26, ay+12, "\u21b5", mono(10), MUTED, ha="right")
    # caption
    txt(ax, W/2, H-24, "Concise \u2192 expandable: full detail, actions still reachable. "
        "(TUI renders in-pane; Desktop in the banner card.)", sans(9, style="italic"),
        ha="center")
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

# ---------------------------------------------------------------- #0 Concept sketch
def concept():
    W, H = 940, 460
    fig, ax = new_canvas(W, H)
    box(ax, 0, 0, W, H, "#12141b")
    txt(ax, W/2, 28, "The metaphor: mobile notifications \u2192 terminal agent interrupts",
        sans(13, "bold"), INK, ha="center")
    # phone on the left
    px, py, pw, ph = 40, 60, 240, 370
    rbox(ax, px, py, pw, ph, "#0a0c11", ec="#2b3040", lw=2, r=26)
    box(ax, px+pw/2-30, py+10, 60, 8, "#2b3040")   # speaker
    # pulled-down shade
    rbox(ax, px+14, py+34, pw-28, ph-84, "#161922", ec=STROKE, lw=1, r=14)
    txt(ax, px+24, py+52, "\u25bc  9:41", sans(9), MUTED)
    # collapsed notif
    rbox(ax, px+24, py+64, pw-48, 52, PANEL_HI, ec=STROKE, lw=1, r=8)
    dot(ax, px+40, py+82, 4, ACCENT)
    txt(ax, px+52, py+80, "claude \u2014 refactor auth", mono(8.5, "bold"), INK)
    txt(ax, px+52, py+96, "Which migration strategy?", mono(8), INK_DIM)
    txt(ax, px+pw-40, py+80, "\u25be", mono(9), MUTED)
    # expanded notif
    rbox(ax, px+24, py+124, pw-48, 92, PANEL, ec=ACCENT, lw=1, r=8)
    txt(ax, px+34, py+140, "expanded \u2014 full detail", mono(8, "bold"), ACCENT)
    txt(ax, px+34, py+156, "Option A / Option B diffs\u2026", mono(7.5), INK_DIM)
    rbox(ax, px+34, py+166, 70, 18, BTN_BG, ec=STROKE_BT, lw=0.8, r=5)
    txt(ax, px+34+35, py+175, "In-place (A)", mono(7), INK_DIM, ha="center")
    rbox(ax, px+108, py+166, 74, 18, "#243a24", ec=GREEN, lw=0.8, r=5)
    txt(ax, px+108+37, py+175, "Go to pane \u2192", mono(7), "#8fe89a", ha="center")
    rbox(ax, px+34, py+188, pw-96, 18, INPUT_BG, ec=STROKE, lw=0.8, r=5)
    txt(ax, px+40, py+197, "\u203a reply\u2026", mono(7.5), FAINT)
    # stack
    for i in range(3):
        rbox(ax, px+24+ i*4, py+224+i*10, pw-48-i*8, 26, PANEL_HI, ec=STROKE, lw=1, r=7, alpha=1-0.18*i)
    txt(ax, px+40, py+237, "stacked \u2014 newest on top", mono(8), MUTED)
    clock(ax, px+30, py+ph-18, 4, MUTED)
    txt(ax, px+40, py+ph-18, "dwell ~10s, then \u25b2 slide up \u2192 stack",
        sans(8, style="italic"), MUTED, ha="left")

    # arrows + mapping on the right
    mapx = 340
    pairs = [("name", "\u2192 the command you ran"),
             ("body", "\u2192 the agent\u2019s log gist, phrased as a question"),
             ("buttons", "\u2192 templated responses + \u201cSomething else\u2026\u201d"),
             ("reply bar", "\u2192 custom reply routed to the session"),
             ("stack", "\u2192 backlog of unresolved interrupts"),
             ("dwell / slide", "\u2192 comes to you, then gets out of the way")]
    txt(ax, mapx+75, 88, "Notification element", sans(10.5, "bold"), ACCENT, ha="center")
    txt(ax, mapx+265, 88, "Terminal-agent equivalent", sans(10.5, "bold"), ACCENT, ha="left")
    ax.plot([mapx, W-24],[100,100], color=STROKE, lw=1)
    for i,(a,b) in enumerate(pairs):
        yy = 128 + i*48
        rbox(ax, mapx, yy-16, 150, 32, PANEL, ec=STROKE, lw=1, r=8)
        txt(ax, mapx+75, yy, a, mono(9.5), INK, ha="center")
        txt(ax, mapx+265, yy, b, sans(9.5), INK_DIM, ha="left")
    save(fig, "original-concept.png")

if __name__ == "__main__":
    concept()
    tui_overlay()
    desktop_banner()
    expanded_detail()
    template_actions()
    pull_surface()
    print("all done")
