# Technical Design Document: TUI Interrupt Notifier

**Version:** 1.0 &nbsp; **Date:** 2026-07-10 &nbsp; **Proposal:** A (user still in a terminal)

---

## Table of Contents

1. [Feature Overview](#1-feature-overview)
2. [System Architecture](#2-system-architecture)
3. [Semantic Event Protocol](#3-semantic-event-protocol)
4. [Attention Detection (In-TUI)](#4-attention-detection-in-tui)
5. [Delivery Router](#5-delivery-router)
6. [The Floating Overlay](#6-the-floating-overlay)
7. [Inline Action Surface](#7-inline-action-surface)
8. [Jump-to-Pane](#8-jump-to-pane)
9. [Pull Surface (Backlog Stack)](#9-pull-surface-backlog-stack)
10. [Interaction Model](#10-interaction-model)
11. [Verified Feasibility Notes](#11-verified-feasibility-notes)

---

## 1. Feature Overview

The TUI Interrupt Notifier serves the moment when an agent needs the user **and the user is still in a terminal** — a different command in the same terminal, another pane, or another tmux session. It provides:

- **A floating overlay** that pops into the focused pane when an agent becomes `done`, `needs_input`, or `error`, in the ephemeral idiom of fzf's `Ctrl-R` history overlay — summon, act, dismiss. It dwells for a configurable period (default 10s) then slides up into the stack if untouched.
- **A gist phrased as a question** — the parsed return-log summary presented as the question the agent is waiting on, not a raw dump.
- **Inline actions** — contextual templated responses plus a "Something else…" freeform prompt bar — that route a response straight back to the agent without leaving the current pane.
- **Jump-to-pane** — a keystroke that moves the user to the exact pane that's waiting, for interrupts that deserve full attention.
- **A backlog stack** — an on-demand pull list of unresolved interrupts, stacked newest-first, that stays until each specific interrupt is resolved.
- **Proportional nudges** — a chime or a tmux status-line message for events that don't warrant overlaying.

The notifier is **absent by default** and appears only on relevance. It is never persistently on screen.

## 2. System Architecture

Three components communicate over a small semantic protocol. The agents themselves never know the notifier exists — they emit semantic state, and everything downstream is decoupled from any particular harness.

```
┌──────────────┐  raw extract  ┌───────────────────┐  phrased    ┌──────────────────┐
│  Harness      │  (prompt +   │  Orchestrator      │  interrupt  │  Attention        │
│  Adapter(s)   │  candidates) │  parse→question    │  ────────►  │  Detector (in-TUI)│
│ observe+launch│  ─────────►  │  + template gen    │             │  focus reporting  │
└──────▲───────┘              └───────────────────┘             └────────┬─────────┘
       │                                                                  │
       │                                                        ┌─────────▼────────┐
       │                                                        │  Delivery Router  │
       │                        ┌──────────────────────┐        │  overlay / chime  │
       └──── response ◄──────────│ Inline Action Surface │◄──────│  / tmux status    │
             / jump              │  buttons + prompt bar │        └──────────────────┘
                                 └──────────────────────┘
```

- **Adapters (one per harness)** observe a harness and, on a state change, **parse its log output** into a *structured extraction*: the semantic state (`working`, `done`, `needs_input`, `error`), the raw prompt/question text the agent is waiting on, any candidate options it can pull from the log, and a **locator** (which tmux session/window/pane). Adapters observe and launch; they are not full interactive drivers. The harness-specific parsing lives here so log-format quirks stay isolated per harness.
- **The orchestrator** turns the structured extraction into what the user sees: it phrases the gist **as a summarized question**, generates the contextual **templated responses** to that question, appends the "Something else…" custom-reply option, and tracks each interrupt's lifecycle. This logic is shared across all harnesses.
- **The detector** answers one question — *is the agent's pane the one the user is looking at?* — and classifies the situation.
- **The router** maps the situation to a proportional channel and renders the overlay, the inline action surface, or a lighter nudge.

## 3. Semantic Event Protocol

The protocol has **two stages**: the adapter emits a `RawExtraction` (harness-specific parsing), and the orchestrator turns it into a `PhrasedInterrupt` (the shared, user-facing shape). This keeps log-parsing per-harness while the question-phrasing and template logic stay consistent everywhere.

```
// STAGE 1 — emitted by the adapter (per-harness log parsing)
interface RawExtraction {
  id: string;                 // stable, per-INTERRUPT (not per-command)
  harness: string;            // "claude-code", "codex", "opencode", ...
  command: string;            // the notification NAME — the command the user issued
  state: "working" | "done" | "needs_input" | "error";
  promptText: string;         // the raw question/prompt parsed from the log
  logTail: string;            // the parsed return-log excerpt (source of the gist)
  candidates: string[];       // option strings the adapter could extract from the log
  locator: PaneLocator;       // where to jump if the user wants full context
  createdAt: Date;
}

// STAGE 2 — produced by the orchestrator (shared, harness-agnostic)
interface PhrasedInterrupt {
  id: string;                 // carried through from RawExtraction
  command: string;            // shown as the notification name
  state: "working" | "done" | "needs_input" | "error";
  question: string;           // the gist, PHRASED AS A QUESTION to the user
  detail: string;             // the EXPAND view — full output / prompt / log
  actions: Action[];          // templated responses + a "Something else…" entry
  locator: PaneLocator;
  lifecycle: "raised" | "acknowledged" | "resolved" | "superseded";
}

interface Action {
  id: string;
  label: string;              // e.g. "In-place (A)", "Shadow table (B)", "Something else…"
  kind: "template" | "confirm" | "redirect" | "custom";  // "custom" opens the inline bar
  payload: string | null;     // text sent back to the agent; null for "custom"
}

interface PaneLocator {
  tmuxSession: string | null;
  tmuxWindow: string | null;
  tmuxPane: string | null;    // fully-qualified target for select-pane
  pid: number;
}
```

**The split:** the **adapter parses** (harness-specific log formats → structured `promptText` + `candidates`); the **orchestrator phrases and templates** (structured extraction → a question the user reads + contextual response buttons + the custom-reply option). The delivery layer then decides *where and how* to show it.

### Interrupt lifecycle

The tracked unit is the **interrupt**, not the command — one long-running command may raise several interrupts over its life, each with its own lifecycle:

- **`raised`** — the adapter detected the agent needs the user; the item enters the stack.
- **`acknowledged`** — the user has seen/expanded it but not yet answered. *Still in the stack.*
- **`resolved`** — the user's response has been routed back and the agent has moved on. **Only now does the item leave the stack.**
- **`superseded`** — the agent self-resolved or errored out before the user acted (e.g. it timed out and chose a default). The item is retired from the stack so it never lingers unresolved.

An item **stays in the stack until its specific interrupt reaches `resolved` or `superseded`** — merely glancing at it does not remove it. This is what "stacked until the interaction is completed" means precisely.

## 4. Attention Detection (In-TUI)

The primary signal is **focus event reporting** — a terminal mode a program turns on to be told when its window gains or loses focus. The notifier's overlay host enables it by emitting `ESC [ ?1004h`; the terminal then sends `ESC [ I` on focus-gained and `ESC [ O` on focus-lost, and the app emits `ESC [ ?1004l` to disable it. This is the established, widely supported mechanism (used by Emacs, Vim/Neovim, tmux) for a terminal program to learn whether it is the focused surface.

### tmux is a first-class hostile test target

tmux only relays focus events when `set -g focus-events on` is configured. Even then the semantics are quirky:

- It can fire a **spurious focus-gained on application startup** — the detector must debounce/ignore the first event within a startup window.
- In some setups an **outer window's focus change is not relayed** to the inner application as expected.
- Focus escape sequences can **leak as literal text** into the input under certain timing or keybinding conditions.

The design therefore:

1. Detects whether it is running inside tmux (`$TMUX`).
2. Checks whether `focus-events` is enabled, and guides the user to enable it if not.
3. Defends against the spurious startup focus-gained.
4. Guards against sequences leaking as text.

### Optional richer channel

Terminals such as WezTerm and iTerm2 support user variables via `OSC 1337 ; SetUserVar`, letting a pane push structured state to the terminal; wrapped in the tmux passthrough sequence with `allow-passthrough on`, this can survive across the multiplexer. This is an **enhancement, not the baseline**.

## 5. Delivery Router

The router maps the detected situation to a proportional channel:

| Situation                                       | Delivery                                             |
| ----------------------------------------------- | ---------------------------------------------------- |
| Agent's own pane is focused                     | Minimal / in-place — the user is already looking     |
| Different pane, terminal still foreground       | Floating overlay in the focused pane, optional chime |
| Non-urgent event, user in another pane          | tmux status-line message + chime, no overlay         |
| User idle / away (no focus event, quiet input)  | Hold and chime; surface on next pull                 |

Principle enforced by the router: **chime for minor, overlay for time-sensitive, never persistent.**

## 6. The Floating Overlay

The touchstone is fzf's `Ctrl-R`: a fast, ephemeral overlay that pops over whatever you are doing and vanishes when done. Prior art for the rendering technique: `fterm.nvim`, `floaterm`.

**Dwell and retraction.** The overlay drops down, stays for a **dwell period (default 10 seconds, user-configurable)** for the user to interact, then slides back up and takes its place in the backlog stack — a symmetric drop-in / slide-out animation mirroring a mobile notification. The dwell timer applies only to an **untouched** overlay: as soon as the user hovers, clicks, expands (`d`), or focuses the inline bar, the auto-retract is **cancelled**, and the overlay stays until the user acts or explicitly dismisses (`Esc`). Retraction is purely visual — it never resolves the interrupt (see below).

```
   ┌─ ● agent needs you ───────────────────────────────┐
   │  claude: refactor auth module          blocked ◐  │   ← name + state
   │  Which migration strategy should I use?            │   ← gist, phrased as a QUESTION
   │                                                    │
   │  [1 In-place (A)] [2 Shadow table (B)] [3 Skip]    │   ← templated responses
   │  [4 Something else…]                               │   ← opens the inline bar
   │  › _______________________________________  ↵send │   ← inline prompt bar
   │                                                    │
   │  d expand   g jump to pane   Esc dismiss   ⏱ 10s   │   ← hotkeys + dwell countdown
   └────────────────────────────────────────────────────┘
      2 more unresolved ▾                                   ← backlog indicator
```

- Renders over the focused pane, not as a new window
- The body is the parsed log gist **rephrased as a question** the user answers
- Status icon reflects state: `●` running, `◐` waiting/blocked, `✓` done, `✗` error
- After the dwell period an untouched overlay slides up into the stack; interacting cancels the timer
- Dismissing or auto-retracting does **not** resolve the interrupt — it returns to the stack (see [§9](#9-pull-surface-backlog-stack)); only a routed response or supersession resolves it

## 7. Inline Action Surface

The body the user reads is the **gist of the parsed return log, phrased as a question** (e.g. *"Which migration strategy should I use?"*). Two affordances answer it, both routing the response back through the adapter into the agent's session **without the user re-entering it**:

- **Templated responses** — rendered from the orchestrator's `actions`. Contextual options generated from the parsed candidates and history (approve, redirect, likely answers). Selected with `1`–`9`.
- **"Something else…"** — the `custom`-kind action; selecting it focuses the **inline prompt bar** (`›`), a ready-to-type field for a freeform reply, sent with `↵`.

This is the highest-emphasis element in the TUI variant: it removes the context switch that otherwise makes managing many agents painful. Sending a response transitions the interrupt toward `resolved`; it leaves the stack only once the agent has moved on.

## 8. Jump-to-Pane

For interrupts that deserve immediate, detailed attention, `g` moves the user to the waiting pane using the `PaneLocator`:

```
tmux select-window -t {session}:{window}
tmux select-pane   -t {session}:{window}.{pane}
```

Because tmux exposes stable, server-wide identifiers addressable with fully-qualified targets, the notifier focuses the exact pane with no ambiguity — no hunting for which of several panes is blocked. In the TUI variant this is present but **secondary** to inline action; the user is already in a terminal, so acting in place is usually cheaper than jumping.

## 9. Pull Surface (Backlog Stack)

A lightweight, on-demand list of unresolved and recent interrupts over the same event stream — the "swipe down to check" equivalent. It is **explicitly not always visible**.

```
┌─ Unresolved (3) ────────────────────────────┐
│ ◐ claude   refactor auth      blocked  now │   ← newest on top
│ ✗ codex    build             error    2m  │
│ ◐ opencode tests            waiting   5m  │
└─────────────────────────────────────────────┘
   j/k select   Enter open   x dismiss
```

- **Stacks newest-first**, giving the hierarchy when the user returns after ignoring several
- An interrupt **stays until its lifecycle reaches `resolved` or `superseded`** — glancing at or dismissing the overlay only marks it `acknowledged`, and it remains in the stack
- Items retired as `superseded` (agent self-resolved) leave automatically, so nothing lingers falsely
- It is the only review affordance in v1 — not a dashboard

## 10. Interaction Model

| Key         | Action                                      | Context          |
| ----------- | ------------------------------------------- | ---------------- |
| _(auto)_    | Overlay appears on new interrupt (`raised`) | Global           |
| _(dwell)_   | Untouched overlay slides up after ~10s (configurable) → stack | Overlay |
| `1`–`9`     | Select a templated response                 | Overlay          |
| _(last #)_  | "Something else…" → focus the inline bar     | Overlay          |
| `›` + `↵`   | Send freeform inline reply                  | Overlay          |
| `d`         | Expand to full detail view                  | Overlay          |
| `g`         | Jump to the waiting pane                     | Overlay          |
| `Esc`       | Dismiss overlay (→ `acknowledged`, stays in stack) | Overlay   |
| `▾` / pull  | Open backlog stack                          | Global           |
| `j` / `k`   | Navigate backlog                            | Backlog          |
| `Enter`     | Reopen selected interrupt                   | Backlog          |
| `x`         | Remove selected (only if `resolved`/`superseded`) | Backlog    |

## 11. Verified Feasibility Notes

| Fact                                        | Status                                          | Note                                 |
| ------------------------------------------- | ----------------------------------------------- | ------------------------------------ |
| Focus event reporting (`ESC [ ?1004h`)      | Confirmed — widely supported                    | Emacs, Vim/Neovim, tmux use it       |
| tmux relays focus only if `focus-events on` | Confirmed — must guide user / detect            | Quirky; spurious startup event       |
| Focus sequences can leak as text            | Confirmed — documented in real harnesses        | Guard required                       |
| `OSC 1337 ; SetUserVar` user variables      | Confirmed — WezTerm, iTerm2                      | Enhancement channel, not baseline    |
| tmux passthrough (`allow-passthrough on`)   | Confirmed                                        | Lets user-vars survive the mux       |
| Floating overlay in-pane                    | Confirmed — prior art `fterm.nvim`, `floaterm`  | Rendering technique                  |
| kitty keyboard protocol (CSI u) under tmux  | **Partial** — uneven, some latency mis-detection | tmux path warrants own test matrix   |
| Fully-qualified tmux pane targets           | Confirmed — stable server-wide IDs              | `select-pane`, `capture-pane`        |
