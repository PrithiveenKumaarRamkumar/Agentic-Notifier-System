# Technical Design Document: GUI/Desktop Interrupt Notifier

**Version:** 1.0 &nbsp; **Date:** 2026-07-10 &nbsp; **Proposal:** B (user has left the terminal) &nbsp; **Platform:** Windows

---

## Table of Contents

1. [Feature Overview](#1-feature-overview)
2. [System Architecture](#2-system-architecture)
3. [Semantic Event Protocol](#3-semantic-event-protocol)
4. [Attention Detection (OS-Level)](#4-attention-detection-os-level)
5. [Delivery: Custom Slide-In Banner + Backlog Stack](#5-delivery-custom-slide-in-banner--backlog-stack)
6. [The Foreground and Focus Model](#6-the-foreground-and-focus-model)
7. [Inline Action Surface](#7-inline-action-surface)
8. [Jump-to-Pane and the Multiplexer Configurations](#8-jump-to-pane-and-the-multiplexer-configurations)
9. [State Attribution Reality](#9-state-attribution-reality)
10. [Interaction Model](#10-interaction-model)
11. [Verified Feasibility Notes](#11-verified-feasibility-notes)

---

## 1. Feature Overview

The GUI/Desktop Interrupt Notifier serves the moment when an agent needs the user **and the user has left the terminal entirely** — a browser, another app, a second monitor. Only a desktop-level notification can reach them there.

The tool renders its **own custom notification banner** — a window that slides down from the top of the screen with a chime, in the idiom of an Android/iOS notification, dwells above the user's current app for a configurable period (default 10 seconds), and then slides back up into a background backlog stack if untouched. This is a deliberate choice over the native Windows toast + Action Center: the custom surface gives full control over the slide-in animation, the dwell period, the expand/collapse behavior, the templated responses, the inline prompt bar, and the stacking order, matching the mobile-notification interaction model precisely rather than accepting the toast system's constraints. (See [ADR-002](ADR-002-desktop-notifier.md) for the alternatives weighed.)

This is the case nothing else addresses — every existing agent-monitoring tool assumes the user is present and looking — and it is therefore **built first** to prove the core thesis end-to-end.

The variant carries the same two affordances as the TUI variant — inline actions and jump-to-pane — but with **jump-to-pane as the primary emphasis**: when the user is away in a GUI app and an agent is blocked, the highest-value move is one click that lands them in the exact pane, prompt visible.

**The defining platform fact** (detailed in [§6](#6-the-foreground-and-focus-model)): the banner can appear **on top of the user's current window without stealing keyboard focus** — this is permitted and is exactly what a mobile notification does. What Windows forbids is *taking* focus (the keyboard caret) before the user has interacted with the banner. The design never needs to; focus transfers only when the user clicks.

## 2. System Architecture

Three components over the same semantic protocol as the TUI variant. The agents never know the notifier exists.

```
┌──────────────┐  interrupt  ┌──────────────────┐  event  ┌────────────────────┐
│  Harness      │  event     │  Orchestrator     │  ────► │  Notifier           │
│  Adapter(s)   │ ─────────► │  event → banner   │        │  attention detect   │
│ observe+launch│            │  spec mapping     │        │  channel choice     │
└──────▲───────┘            └──────────────────┘        │  banner + return exec│
       │                                                  └─────────┬──────────┘
       │                                                            │
       │                        click on banner                     │
       └──── raise window + tmux select-pane  ◄─────────────────────┘
```

- **Adapters** — same contract as Proposal A: observe a harness, **parse its log output** into a structured extraction (semantic state, raw prompt text, candidate options, and a locator), launch tasks. They deliberately do **not** inject replies into a running session (the user answers in the real terminal), keeping them "observe-and-launch." Harness-specific parsing stays here.
- **Orchestrator** — turns the structured extraction into what the user sees: the command name, the gist **phrased as a question**, expandable detail, the **templated responses** plus a "Something else…" custom-reply option, and the jump locator. It also tracks each interrupt's lifecycle (`raised → acknowledged → resolved / superseded`). Shared across harnesses.
- **Notifier** — detects the user's attention state, chooses the channel, renders the custom slide-in banner (topmost, without taking focus), and on click executes the return (raise the terminal window, focus the exact pane).

## 3. Semantic Event Protocol

Identical to the TUI variant — this is the shared infrastructure. See [TUI TDD §3](TECHNICAL-DESIGN-TUI.md#3-semantic-event-protocol). The `PaneLocator` is what the notifier consumes on a banner click to execute the return.

## 4. Attention Detection (OS-Level)

The notifier determines which "world" the user is in by reading the current foreground window and resolving its owning process:

```
HWND  fg   = GetForegroundWindow();
DWORD pid;  GetWindowThreadProcessId(fg, &pid);
// resolve pid -> process name -> is it a terminal emulator? which one?
// is it the terminal hosting the agent, or a non-terminal GUI app?
```

Supporting signals:

- **`GetLastInputInfo()`** — time since last keyboard/mouse input, distinguishing *"user is at another app"* from *"user is away."*
- **`FocusSessionManager.IsFocusActive` / `IsFocusActiveChanged`** (Windows 11) — respects the user's Focus Assist / Do-Not-Disturb state, so the tool does not overlay when the user has asked for no distractions.
- **Browser Idle Detection API** — the equivalent OS-idle signal for any future web/PWA delivery surface.

**A critical constraint: Windows has no concept of a terminal "pane."** OS-level signals are window-granularity only. If the user runs multiple panes inside one terminal window, the OS cannot report *which pane* is focused — only which window. Pane-level focus must come from the in-terminal focus-event-reporting mechanism (Proposal A); the two layers are **fused** by the attention detector. Neither alone is sufficient.

Ambiguous cases (no foreground window, a terminal on a second monitor) resolve **conservatively** to "not clearly in the agent's terminal," which escalates to the desktop slide-in banner.

## 5. Delivery: Custom Slide-In Banner + Backlog Stack

Delivery is a **custom window the tool owns and draws itself**, not the native Windows toast. It reproduces the mobile-notification interaction model directly:

| Mobile-notification property | Custom-banner mechanism                                              |
| ---------------------------- | ------------------------------------------------------------------- |
| Slide-in from top + chime    | Topmost window animated down, audio cue                             |
| Transient popup              | Dwells for a configurable period (default 10s), then slides up      |
| Persistent backlog / stack   | Own backlog surface, newest-first (see [§9](#9-state-attribution-reality) note) |
| Concise + expandable         | Collapsed banner → click/hotkey expands to full detail             |
| Inline call-to-action        | Templated responses + inline prompt bar                             |
| Respect DND                  | Query `FocusSessionManager.IsFocusActive`; suppress banner, stack only |

**How the banner appears without stealing focus.** The window is shown topmost using `SetWindowPos` with `HWND_TOPMOST` and the **`SWP_NOACTIVATE`** flag (plus `SWP_SHOWWINDOW`). This makes the banner paint above the user's current application **without moving keyboard focus** — the user keeps typing in whatever they were in. This is the permitted, non-intrusive path and is exactly what a phone banner does. The tool **never** calls `SetForegroundWindow` on the banner at appearance time; doing so would be refused by the OS anyway (see [§6](#6-the-foreground-and-focus-model)) and would be the focus-stealing behavior the design exists to avoid.

**Lifecycle.** The tracked unit is the **interrupt**, not the command — one command may raise several over its life (`raised → acknowledged → resolved / superseded`):

1. Interrupt `raised` → banner slides down topmost-no-activate, with a chime.
2. It dwells on top for a **configurable period (default 10 seconds)**. The user's focus is untouched.
3. If the user does nothing for the full dwell period, the banner **slides back up** and the item stays in the backlog stack as `raised` — **not resolved**. It remains there until answered.
4. If the user **clicks** the banner (any time during dwell), that click is input to the notifier's process — the dwell timer is **cancelled**, focus transfer is permitted, the banner becomes interactive (→ `acknowledged`), and expand / templated-reply / custom-reply / jump-to-pane all work.
5. The interrupt leaves the stack only when it reaches `resolved` (response routed, agent moved on) or `superseded` (agent self-resolved/errored before the user acted).

```
   (background: a browser window, clearly not a terminal — focus stays here
    until the user clicks the banner)

   ▼ slides down from top edge, topmost, no-activate — dwells ~10s, then ▲ slides up
  ┌─ Agent Interrupt Notifier ──────────────────── now · ⏱10s ─┐
  │  ● claude — refactor auth module            BLOCKED        │   ← title (command) + state
  │  Which migration strategy should I use?                    │   ← gist, phrased as a QUESTION
  │  (expand for both diffs)                                    │
  │                                                             │
  │  [ In-place (A) ]  [ Shadow table (B) ]  [ Go to pane →]   │   ← templated responses + jump
  │  [ Something else… ]   › type a reply…                  ↵   │   ← custom-reply opens the bar
  └─────────────────────────────────────────────────────────────┘
      ▸ Backlog stack (unresolved):  3 items
        ● codex    build failed          2m ago                 ← stacked newest-first
        ◐ claude   waiting on input      5m ago                 ← stays until resolved
        ◐ opencode waiting on input      6m ago
```

Non-urgent events (e.g. a `done` the user need not act on) **skip the slide-in** and go straight to the backlog stack — no banner, catch up on pull. Time-sensitive events (`needs_input`, `error`) slide in with a chime.

## 6. The Foreground and Focus Model

**The key technical finding — and it has two halves that are easy to conflate.** Windows draws a hard line between *showing a window on top* and *giving a window keyboard focus*. The design depends on getting this distinction right.

### What is allowed: appear on top without focus

A window can be made **topmost and visible over the user's current application at any time**, using `SetWindowPos(HWND_TOPMOST, …, SWP_NOACTIVATE | SWP_SHOWWINDOW)`. The `SWP_NOACTIVATE` flag is the crucial part: the window paints on top but **does not take the keyboard caret** — the user keeps typing in whatever app they were in. Microsoft's own documentation demonstrates exactly this pattern (show a window "topmost without the foreground focus"). This is what makes the slide-in banner possible, and it is precisely how a mobile notification behaves: it appears over your app but does not hijack your keyboard.

### What is forbidden: taking focus unprompted

`SetForegroundWindow` — which moves a window to the front **and gives it keyboard focus** — is refused when the calling app was not the one the user last interacted with. Windows flashes the taskbar button instead. This is the OS protecting the user from a window that suddenly grabs their keystrokes mid-sentence.

**This restriction does not block the banner.** It only blocks *forcing focus onto the banner before the user has touched it* — which the design never does and never needs to. A mobile banner doesn't seize your keyboard on arrival either; you tap it first.

### How the two halves shape the design

- **Banner appearance** → topmost-no-activate. Always allowed, never blocked, no focus stolen. This is the whole slide-in experience.
- **Jump-to-pane return** → requires actual foreground activation, so it is **initiated by the user clicking the banner.** That click is input directed at the notifier's process, which grants it the right to call `SetForegroundWindow` and raise the terminal. The restriction and good UX coincide: the tool never steals focus, and offers a one-click return the user chose to take.
- **Do not** disable the protection globally (e.g. setting `SPI_SETFOREGROUNDLOCKTIMEOUT` to 0). It is fragile, mutates global system state, and reintroduces the exact focus-stealing the design avoids. The topmost-no-activate path gives the needed visual without fighting the OS.
- **`FlashWindowEx`** remains the sanctioned way to draw attention without stealing focus — a fallback nudge if a banner is suppressed by DND.

## 7. Inline Action Surface

The body the user reads is the **gist of the parsed return log, phrased as a question**. Same two affordances as the TUI variant, rendered as **templated response buttons** (the orchestrator's `actions`) and a **"Something else…" input box** (opens for a freeform reply), interactive once the user clicks the banner. In this variant they are **secondary** to jump-to-pane:

- For **`done`**, the notification often carries enough to decide in place — read the concise result, optionally hit a light action, frequently dismiss without returning at all.
- For **`needs_input` / `error`**, the real back-and-forth needs the terminal's full context (scrollback, exact prompt, surrounding state). The notification's most valuable feature is therefore **precise navigation**, not inline reply. Inline text reply is a minor convenience here, not the core interaction.

## 8. Jump-to-Pane and the Multiplexer Configurations

The return path depends on where the terminal multiplexer runs. Two configurations are supported, detected at runtime; the difference is whether the pane operations cross an OS boundary.

### Configuration 1 — Native Windows multiplexer (psmux): no bridge

[psmux](https://github.com/psmux/psmux) is a native Windows terminal multiplexer (built in Rust on ConPTY) that speaks the tmux command language, reads `.tmux.conf`, and — relevant here — has first-class Claude Code support: teammate agents spawn one-per-pane rather than in-process, which is exactly the topology this tool targets. When psmux is the multiplexer, **the entire return path is Windows-side** — no WSL, no boundary crossing:

```
  [user clicks banner]
        │
        ▼
  Windows side:  raise terminal-emulator window   (SetForegroundWindow — now permitted)
        │
        ▼
  Windows side:  psmux select-window -t {sess}:{win}     (ships a `tmux` alias)
                 psmux select-pane   -t {sess}:{win}.{pane}
```

The window raise, the pane selection, and the state read all run in the same OS process space. This is the cleanest substrate for the Windows variant and the recommended setup.

### Configuration 2 — tmux under WSL: the bridge

When tmux runs under WSL (or Cygwin), the return path crosses a boundary — the window raise is Windows-side, the pane selection is WSL-side:

```
  [user clicks banner]
        │
        ▼
  Windows side:  raise terminal-emulator window   (SetForegroundWindow — now permitted)
        │
        ▼
  WSL side:      tmux select-window -t {sess}:{win}
                 tmux select-pane   -t {sess}:{win}.{pane}
```

- **Windows-side** window raise on click (permitted because the click granted foreground rights).
- **WSL-side** pane selection via fully-qualified tmux targets — stable, server-wide identifiers, no ambiguity.
- Reading agent state likewise runs WSL-side.

This bridge is the fiddliest piece of implementation, **but it applies only to the WSL configuration** — the native-psmux path avoids it entirely. Because both multiplexers share the tmux command vocabulary and format variables, a single adapter targets both, selecting the invocation at runtime by detecting which multiplexer is present. Everything else rests on well-supported APIs.

## 9. State Attribution Reality

Reliably reading per-agent state is imperfect across the ecosystem today — every existing tool works around it by scraping hooks, polling panes, or parsing transcripts, with no clean first-party API. A well-known example: Claude Code's subagent-stop hook cannot identify *which* subagent finished because session IDs are shared.

The hardest detection problem is distinguishing an agent that is **blocked waiting for input** from one that is merely **busy working** — they look identical to a naive process monitor, yet the difference is the entire point of a `needs_input` notification. The strongest available signal is reading pane content and running processes (the same commands work under both multiplexer configurations from [§8](#8-jump-to-pane-and-the-multiplexer-configurations), since psmux implements the tmux command language):

```
tmux capture-pane -p -t {target}          # visible content + scrollback
tmux list-panes  -F "#{pane_current_command}"   # what each pane is running
```

The design absorbs the imperfection by keeping the state-source **behind the adapter interface**: adapters use the best signal available now (tmux panes, exit codes, process lifecycle), and if richer agent-observability infrastructure ships later (per-agent identifiers, enriched hooks), an adapter consumes it **without changing the protocol or the notifier**. The tool degrades gracefully when signals are coarse and improves automatically when they get richer.

## 10. Interaction Model

| Trigger                    | Action                                              |
| -------------------------- | --------------------------------------------------- |
| Interrupt `raised` (`needs_input`/`error`)| Slide-in banner (topmost, no-activate) + chime, unless DND |
| Agent `done` (no action)   | Straight to backlog stack, no slide-in              |
| Click templated response    | Send that response back via adapter → toward `resolved` |
| Click **Something else…**   | Open input box for a freeform reply                 |
| Type in input box + send   | Send freeform reply back via adapter → toward `resolved` |
| Click **Go to pane →**      | Raise terminal window, then `select-pane`           |
| Click body / expand         | Show full detail (→ `acknowledged`)                 |
| Dwell elapses (~10s, config) | Untouched banner slides up; item stays in stack as `raised` |
| Interact during dwell       | Dwell timer cancelled; banner stays until acted/dismissed |
| Agent self-resolves/errors  | Interrupt retired as `superseded`, leaves stack     |
| Ignore                      | Persists in backlog stack until resolved, newest-first |

## 11. Verified Feasibility Notes

| Fact                                            | Status                                          | Note                                   |
| ----------------------------------------------- | ----------------------------------------------- | -------------------------------------- |
| `GetForegroundWindow` + `GetWindowThreadProcessId` | Confirmed                                     | Foreground window → owning process     |
| `GetLastInputInfo`                              | Confirmed                                       | Idle vs. at-another-app                |
| `FocusSessionManager.IsFocusActive` (Win 11)    | Confirmed                                       | Respect Focus Assist / DND             |
| OS cannot report terminal **pane** focus        | Confirmed — window granularity only             | Must fuse with focus event reporting   |
| Topmost-no-activate window (`SWP_NOACTIVATE`)   | Confirmed — **enables the slide-in banner**     | Appears on top, does not take focus    |
| `SetForegroundWindow` steal prevention          | Confirmed — flash only unless last-input process | Blocks *focus theft*, not the banner   |
| Click grants foreground rights                  | Confirmed                                       | User click = input to notifier process |
| `FlashWindowEx`                                 | Confirmed                                       | Attention w/o stealing focus           |
| Custom banner: full control of anim/stack/inline | Confirmed — own-window rendering                | Chosen over native toast constraints   |
| tmux fully-qualified pane targets               | Confirmed                                       | `select-window` / `select-pane`        |
| `capture-pane` / `list-panes` state read        | Confirmed — strongest blocked-vs-busy signal    | Imperfect but best available           |
| psmux — native Windows multiplexer              | Confirmed — Rust/ConPTY, tmux command language  | No WSL bridge; first-class Claude Code panes |
| Windows↔WSL return bridge                       | Feasible — fiddliest piece, **WSL config only** | Avoided entirely under native psmux    |
| Shared subagent session IDs (Claude Code)       | Confirmed limitation                            | Absorbed behind adapter interface      |
