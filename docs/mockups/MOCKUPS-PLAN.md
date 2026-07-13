# Mockups Plan

This document specifies the visuals the proposal needs, what each one must show, and how to produce it. It mirrors the role of the `docs/mockups/` folder in a design-proposal repo: the README embeds the rendered images, and this plan is the brief a designer (or an image-generation pass) works from.

Every mockup must reinforce the two theses: **(1)** the tool is absent-by-default and proportional, never a persistent dashboard; and **(2)** both variants carry inline actions *and* jump-to-pane, differing only in emphasis.

| # | File                          | Surface                                   | Used in                          |
| - | ----------------------------- | ----------------------------------------- | -------------------------------- |
| 0 | `original-concept.png`        | The Claude follow-up card, mapped         | README (Documentation)           |
| 1 | `tui-overlay-mockup.png`      | In-TUI floating overlay (fzf-style)       | README (Proposal A), TUI TDD §6  |
| 2 | `desktop-banner-mockup.png`   | Custom slide-in banner (topmost, no focus) | README (Proposal B), Desktop TDD §5 |
| 3 | `expanded-detail-mockup.png`  | Hybrid expand: log-slice inline + press-hold peek | Both TDDs (§7 expand)|
| 4 | `template-actions-mockup.png` | Templated responses to the question + "Something else…" | Both TDDs (inline action surface)|
| 5 | `pull-surface-mockup.png`     | Pull surface / backlog stack              | TUI TDD §9, Desktop TDD §5       |
| 6 | `stepper-mockup.png`          | Stepper card for an interrupt with 4+ questions | Both TDDs (multi-question follow-ups) |

The ASCII sketches below double as (a) the layout brief for a rendered image and (b) a usable fallback if the PNG isn't produced — the reference repo embeds ASCII previews directly in Markdown, and this repo does the same.

---

## 0. Original Concept Sketch

**Purpose:** anchor the whole proposal in the **Claude follow-up card** — the interaction pattern the design borrows from — so a reader immediately understands the design language.

**Must show:** on the left, a faithful rendering of the Claude follow-up card: the question at top, a set of numbered options (the first one selected/highlighted with a return arrow), a "✎ Something else" row, a "Skip" button, an "Or reply directly…" input bar showing the model label, and the navigation hint (`↑↓ to navigate · Enter to select · or type below`). On the right, a two-column table mapping each card element to its terminal-agent equivalent: question → **the agent's log gist phrased as a question**; command name → the command that's calling you (shown above the query); numbered options → templated responses parsed from the log; ✎ Something else → custom reply routed to the session; Skip → ignore or auto-pick the most relevant; Enter / ↑↓ / ←→ → select, move within a question, move between questions.

**How to produce:** a clean annotated illustration; can be hand-sketched or generated. It is explicitly the "here is the model we're borrowing" figure — the left half should look like the real Claude follow-up card, the right half like a plain mapping table.

**Rendered:**

![Original concept](original-concept.png)

---

## 1. TUI Floating Overlay

**Purpose:** show delivery when the user is still in a terminal — an ephemeral overlay in the focused pane, fzf `Ctrl-R` in feel.

**Must show:** the overlay floating over dimmed terminal content behind it; name + state on the top line; the gist **phrased as a question**; a row of numbered templated responses plus a "Something else…" entry; the inline prompt bar; the hotkey legend (`d expand · g jump · Esc dismiss`); a dwell countdown (`⏱ 10s`) conveying it auto-retracts; and the backlog indicator (`N more unresolved`). Emphasis cue: inline actions visually prominent, jump-to-pane present but quieter.

**Layout brief (also the Markdown fallback):**

```
  ┌─ terminal content (dimmed) ─────────────────────────┐
  │  $ npm test                                          │
  │  ⋮                                                    │
  │     ┌─ ● agent needs you ─────────────────────────┐  │
  │     │  claude: refactor auth module      blocked ◐ │  │
  │     │  Which migration strategy should I use?       │  │  ← gist as a question
  │     │                                               │  │
  │     │  [1 In-place (A)] [2 Shadow (B)] [3 Skip]     │  │  ← templated responses
  │     │  [4 Something else…]  › ____________  ↵send   │  │  ← custom reply
  │     │                                               │  │
  │     │  d expand   g jump to pane   Esc dismiss      │  │  ← jump present, quieter
  │     └───────────────────────────────────────────────┘  │
  │  2 more unresolved ▾                                  │
  └───────────────────────────────────────────────────────┘
```

**How to produce:** render a real terminal, screenshot, composite the overlay; or generate to match this layout with a monospace terminal aesthetic (dark background, box-drawing characters, a single accent color for the status dot).

**Rendered:**

![TUI overlay](tui-overlay-mockup.png)

---

## 2. Desktop Slide-In Banner

**Purpose:** show delivery when the user has left the terminal — the differentiating case, built first. Must read as an Android/iOS-style banner the tool draws itself, sliding down from the top edge, *on top of* the user's current app but not stealing their keyboard.

**Must show:** a banner sliding down from the **top edge** over a non-terminal app (e.g. a browser) to make "the user is away" legible; a motion cue for the drop-down (and a note that it dwells ~10s then slides back up) and a caption noting it is topmost-but-not-focused (the browser's text caret still blinks); title = command, state badge = BLOCKED; the gist **phrased as a question** with an "(expand for diffs)" affordance; templated response buttons including a prominent **Go to pane →** (primary emphasis for this variant); a "Something else…" custom-reply entry with an input box (noted as active only after a click); and, below, the tool's own backlog stack of unresolved interrupts, three items newest-first, each with a state glyph and relative time.

**Layout brief (also the Markdown fallback):**

```
  (background: a browser window, clearly not a terminal — caret still
   blinks in the browser; the banner has NOT stolen focus)

     ▼ slides down from top edge — topmost, SWP_NOACTIVATE
  ┌─ Agent Interrupt Notifier ─────────────── now ─┐
  │  ● claude — refactor auth module      BLOCKED  │
  │  Which migration strategy should I use?         │  ← gist as a question
  │  (expand for both diffs)                         │
  │                                                  │
  │  [ In-place (A) ] [ Shadow (B) ] [ Go to pane →]│  ← jump = primary emphasis
  │  [ Something else… ]  › type a reply…        ↵   │  ← custom reply, active on click
  └──────────────────────────────────────────────────┘

     ▸ Backlog stack (unresolved, newest first)
       ● codex    build failed        2m ago
       ◐ claude   waiting on input    5m ago
       ◐ opencode waiting on input    6m ago
```

**How to produce:** compose over a real Windows desktop screenshot for authenticity, or generate a custom banner aesthetic (rounded card, drop shadow, top-edge slide). It should look like the tool's *own* notification, not a native Windows toast — the design owns this surface. Convey "on top but not focused" with the background app's caret/selection still visible.

**Rendered:**

![Desktop banner](desktop-banner-mockup-nanobanana.png)

---

## 3. Expand: the Hybrid Log-Slice View

**Purpose:** demonstrate the "concise, then verify against the source" principle. Expand is not a separate detail blob — it reveals the exact `logSpan` the summary was parsed from, so the user can check the question against the real log. Two gestures, borrowed from mobile: **click/tap** toggles a committed inline expand (`^` to collapse); **press-and-hold** peeks a wider view that springs back on release.

**Must show:** two states side by side or stacked — (a) the **inline expand**: the question with its log slice opened below it, labeled with the source range (`from the log · lines 214–219`), the agent's actual question highlighted within the slice, a `^` collapse caret, and the templated responses + "Something else…" still reachable below; and (b) the **press-and-hold peek**: the wider log with a few dimmed context lines above and below the highlighted source lines, a "release to collapse" hint, and the rest of the stack blurred behind it. Caption that both render the same `logSpan` and that the peek is a pure enhancement over the accessible inline expand.

**Layout brief — inline expand (committed):**

```
  ┌─ ⌃ collapse ──────────────────────────────────────┐
  │  Q: Which migration strategy should I use?         │
  │  ┌ from the log · lines 214–219 ─────────────────┐ │
  │  │ psql: column "role" cannot be added with       │ │
  │  │   NOT NULL and no default on a populated table │ │
  │  │ I can migrate two ways — which?         (bold) │ │  ← the slice the
  │  │   A) in-place ALTER   B) shadow table+backfill │ │     summary came from
  │  │ ▸ waiting for your choice…                     │ │
  │  └─────────────────────────────────────────────────┘ │
  │  [ In-place (A) ] [ Shadow (B) ] [ Something else… ] │
  └──────────────────────────────────────────────────────┘
```

**Layout brief — press-and-hold peek (transient, springs back on release):**

```
  ┌─ 👁 Peeking full log ───────────── release to collapse ─┐
  │  Which migration strategy should I use?                 │
  │  ┌──────────────────────────────────────────────────┐  │
  │  │ [212] running migration: add users.role   (dim)   │  │  ← context, dimmed
  │  │ [213] $ psql -f migrations/003_role.sql    (dim)  │  │
  │  │ [214] ERROR: column "role" cannot be added (hot)  │  │  ← source lines,
  │  │ [218] I can migrate two ways — which?      (hot)  │  │     highlighted
  │  │ [221] ▸ waiting for your choice…           (hot)  │  │
  │  └──────────────────────────────────────────────────┘  │
  │  lines 214–221 fed the summary · the rest is context    │
  └──────────────────────────────────────────────────────────┘
     (the stack sits blurred behind this; lifting the press restores it)
```

**How to produce:** same rendering approach as #1/#2. The essential storytelling points are (1) the source range label tying the slice to the summary, (2) the highlighted-vs-dimmed distinction in the peek, and (3) a visible `^` caret on the committed expand versus a "release to collapse" hint on the peek. Show real log content, not lorem, so the provenance point lands.

**Rendered:**

![Expanded detail](expanded-detail-mockup-nanobanana.png)

---

## 4. Templated Responses to the Question

**Purpose:** show that the response buttons are **derived** — the adapter parses candidate options from the log, the orchestrator phrases the question and turns candidates + history into templated replies — not fixed labels. And that "Something else…" always escapes the templates.

**Must show:** the question at top, then a button set with a small "why these" annotation indicating each template's source (parsed from the agent's prompt, from your history, from repo convention), plus the always-present "Something else…" that opens the freeform bar. Include a mix: options lifted from the log (In-place / Shadow table), a history-derived redirect (Rebase onto main first), and the custom escape hatch.

**Layout brief:**

```
  ┌─ Q: Which migration strategy should I use? ─────────────────┐
  │  [ In-place (A) ]        ← parsed from agent's prompt        │
  │  [ Shadow table (B) ]    ← parsed from agent's prompt        │
  │  [ Rebase onto main ]    ← from your history (used 3× here)  │
  │  [ Skip / defer ]        ← common redirect                   │
  │  [ Something else… ]     ← always present → opens the bar    │
  │                                                              │
  │  › type your own reply…                                  ↵   │
  └──────────────────────────────────────────────────────────────┘
```

**How to produce:** annotated version of the button set from #1/#2; the annotations (showing adapter-parsed vs orchestrator-generated vs history) are the whole point, so keep them legible. Make "Something else…" visually distinct as the escape hatch.

**Rendered:**

![Templated responses](template-actions-mockup.png)

---

## 5. Pull Surface / Backlog Stack

**Purpose:** show the "swipe down to check" equivalent — on-demand, newest-first, items leave only when their interrupt is resolved. Reinforces "not a dashboard": it is summoned, not standing.

**Must show:** the backlog opened on demand (a pull affordance at the top edge), items stacked newest-first with state glyphs and times, one item mid-removal to convey "an item leaves only when its interrupt is resolved (or superseded)," and a clear visual that this surface is transient (e.g. a dimmed background it overlays and will vanish back into). For the desktop variant, note in-caption that this is the tool's own backlog stack; for TUI, it is the summoned overlay list.

**Layout brief:**

```
   ▲ pull to check
  ┌─ Unresolved (3) ────────────────── summoned, will dismiss ─┐
  │ ◐ claude    refactor auth        blocked   now             │  ← newest on top
  │ ✗ codex     build                error     2m              │
  │ ◐ opencode  tests              waiting    5m   ⟶ resolving │  ← leaves once resolved
  └────────────────────────────────────────────────────────────┘
     j/k select   Enter reopen   x remove (if resolved)
```

**How to produce:** render the stack with a subtle motion cue (the resolving row fading/sliding out) if the medium allows; otherwise annotate. Emphasize transience of the *surface* (summoned, not standing) while making clear items *persist until resolved* — it must not read as a dashboard.

**Rendered:**

![Pull surface](pull-surface-mockup.png)

---

## 6. Stepper Card (interrupt with 4+ questions)

**Purpose:** show how the follow-up card scales when a single interrupt needs to ask **several** questions. When the agent's block resolves into more than three questions, the stacked card would grow too tall (the reply bar scrolls off), so the card switches to a **stepper**: one question at a time, fixed height. This is the ≥4-question counterpart to the templated-response card — the two differ only by question count (≤3 → stacked, all visible; ≥4 → stepper, one at a time).

**Must show:** a segmented progress bar at the top (filled segments = answered, a distinct current segment, faint segments ahead) with a "3 of 4" counter; the command name above the current question; the current question with its numbered options (first selected as a highlight bar) plus a "✎ Something else"; an **"Answered" chip row** pinning the earlier answers (since they're no longer visible, this is what keeps the stepper from feeling like a void); a **Back / Skip / Next** control row (Next as the primary action); the shared "Or reply directly…" bar; and a footer hint covering both axes of navigation (`↑↓ options · ←→ questions · Enter select · Skip all to defer`). A short caption should make explicit that the stepper appears **for an interrupt that raises a stack of questions**, and that ≤3 questions use the stacked card instead.

**Layout brief:**

```
  ┌─ agent needs you · 3 of 4 ─────────────────────────────┐
  │  ▓▓▓▓  ▓▓▓▓  ▓▓▓▓  ░░░░                                  │  ← progress: 2 done, current, ahead
  │  ● claude: refactor auth module              ◐ blocked  │  ← command above the query
  │  Assume native psmux, or WSL tmux too?                  │
  │  ▏1  Native psmux only — simplest path            ↵ ▕   │  ← selected (highlight bar)
  │   2  Support both from day one                          │
  │   3  WSL tmux only — no native dep                      │
  │   ✎  Something else                                     │
  │  Answered  [1 · GUI banner first] [2 · Claude Code]     │  ← pinned prior answers
  │  ─────────────────────────────────────────────────────  │
  │  [← Back]                        [Skip]   [ Next → ]    │
  └──────────────────────────────────────────────────────────┘
     › Or reply directly…
     ↑↓ options · ←→ questions · Enter select · Skip all to defer
```

**How to produce:** same flat xterm rendering as the other TUI mockups. The essential storytelling points are (1) the segmented progress bar conveying "how much is left" that the stacked card gives at a glance, (2) the Answered chip row standing in for the hidden earlier questions, and (3) the caption tying the stepper to the multi-question / stack-of-interrupts case.

**Rendered:**

![Stepper card](stepper-mockup.png)

---

## Production notes

- **Consistency:** one status-glyph vocabulary across every mockup — `●` running, `◐` waiting/blocked, `✓` done, `✗` error, `○` pending.
- **Emphasis discipline:** in TUI mockups the inline bar/buttons are visually dominant; in Desktop mockups **Go to pane →** is dominant. Both affordances appear in both — never drop one.
- **Never persistent:** every mockup should read as transient/summoned. If a frame looks like it could sit on screen all day, it is off-brief.
- **Real content:** use plausible agent prompts and diffs, not lorem ipsum, so the expand/detail value is self-evident.
