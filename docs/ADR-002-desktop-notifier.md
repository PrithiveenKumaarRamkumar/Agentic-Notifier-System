# ADR-002: GUI/Desktop Interrupt Notifier

**Status:** Proposed &nbsp; **Date:** 2026-07-10 &nbsp; **Proposal:** B (user has left the terminal) &nbsp; **Platform:** Windows

## Context

The same developer running multiple terminal agents frequently leaves the terminal **entirely** — a browser, another app, a second monitor. When an agent finishes or blocks needing input, no in-terminal mechanism can reach a user who is no longer in any terminal. This is the case nothing else addresses, and it is precisely when a notification is most valuable.

The Windows platform imposes hard constraints that shape any solution:

- **No concept of a terminal pane** — OS focus signals are window-granularity only.
- **Focus-activation is protected, but showing-on-top is not** — an application may make a window **topmost and visible over the user's current app without taking keyboard focus** (`SWP_NOACTIVATE`), which is exactly what a slide-in banner needs. What Windows forbids is *taking* keyboard focus (`SetForegroundWindow`) when the app was not the last one the user interacted with; there it flashes the taskbar instead. Only a genuine user interaction (a click on the banner) grants focus-activation rights.
- **The multiplexer may or may not be native** — tmux under WSL crosses the Windows↔WSL boundary on the return path, but [psmux](https://github.com/psmux/psmux) is a native Windows multiplexer (Rust/ConPTY) that speaks the tmux command language and spawns Claude Code agents one-per-pane, removing the boundary entirely. Both must be supported.
- **No clean first-party per-agent state API** — state attribution is imperfect ecosystem-wide (e.g. Claude Code's shared subagent session IDs).

## Decision

Build a **Windows GUI/Desktop Interrupt Notifier** that renders its **own custom slide-in banner** (an Android/iOS-style notification the tool draws and controls), consisting of:

### 1. Shared Adapters + Two-Stage Protocol

Reuse Proposal A's two-stage protocol unchanged: adapters parse harness logs into a structured extraction; the orchestrator phrases the gist as a question, generates templated responses plus "Something else…", and tracks the interrupt lifecycle. Adapters observe and launch; they do not inject replies.

### 2. OS-Level Attention Detection

Read the foreground window (`GetForegroundWindow` → `GetWindowThreadProcessId` → owning process) to classify the user's world; combine with `GetLastInputInfo` (idle) and `FocusSessionManager.IsFocusActive` (DND). Fuse with the in-terminal focus-event-reporting signal for pane granularity. Resolve ambiguous cases conservatively toward showing the banner.

### 3. Custom Slide-In Banner Delivery

Render an own-window banner that slides down from the top of the screen with a chime, dwells above the user's current app for a configurable period (default 10 seconds) without taking focus, then slides back up if untouched — **the interrupt stays in the backlog stack as unresolved**, it is not dropped. Interacting during dwell cancels the timer. The banner is shown topmost via `SetWindowPos(HWND_TOPMOST, …, SWP_NOACTIVATE)` so it appears on top **without stealing keyboard focus**. Non-urgent events skip the slide-in and go straight to the backlog stack; time-sensitive events slide in. Each interrupt follows the `raised → acknowledged → resolved / superseded` lifecycle and leaves the stack only at `resolved`/`superseded`.

### 4. User-Initiated Return (the defining decision)

The banner appears without focus. When the user **clicks it**, that click grants the tool focus-activation rights, so `SetForegroundWindow` on the terminal then succeeds. Jump-to-pane is therefore initiated by the click. Use `FlashWindowEx` as a no-focus-steal fallback nudge. This is jump-to-pane as **primary emphasis** for this variant.

### 5. Multiplexer-Aware Return Path

Detect the multiplexer at runtime. Under **native psmux**, the whole return is Windows-side (raise window, then `psmux`/`tmux` select-pane) — no bridge. Under **tmux in WSL**, raise the terminal-emulator window Windows-side, then `tmux select-pane` WSL-side. A single adapter targets both because psmux implements the tmux command vocabulary. Native psmux is the recommended setup and the cleanest substrate.

### 6. Inline Action Surface (secondary emphasis)

The gist is phrased as a question; templated response buttons + a "Something else…" input box (interactive once the user clicks) route responses back via the adapter. For `done` the user often acts/dismisses in place; for `needs_input`/`error`, navigation-first is the core interaction and inline reply is a minor convenience.

## Alternatives Considered

### A. Silently Auto-Raise the Terminal on Block

Detect a block and bring the terminal to the foreground automatically, without user action.

**Rejected because:**

- Windows **refuses** to grant focus-activation to a background process — it only flashes the taskbar.
- Even if it were possible, silently stealing focus mid-keystroke is hostile UX.
- The user-click model achieves the goal *and* respects attention.

### B. Native Toast + Action Center (instead of a custom banner)

Use the built-in Windows toast notification and Action Center rather than drawing our own window.

**Rejected because:**

- The toast system constrains the slide-in animation, the expand/collapse behavior, the templated-response layout, the inline prompt bar, and the stacking order — the tool cannot match the Android/iOS interaction model it is deliberately porting.
- Toast content, timing, and styling are largely dictated by the OS; the design wants full control of the notification's feel.
- The custom banner is achievable **without** fighting the OS: a topmost-no-activate window appears on top without stealing focus (the concern that a custom window would be blocked does not apply — that restriction is on focus-activation, not on showing-on-top). So the main argument *for* the native toast — that only it can appear over other apps — is false.
- Trade-off acknowledged: the custom path reimplements chime, backlog persistence, and DND-respect that the toast provides for free. This is accepted deliberately in exchange for interaction fidelity, and DND is still honored by querying `FocusSessionManager`.

### C. Cross-Platform From Day One

Build a portability layer covering macOS/Linux notifications too.

**Rejected because:**

- Speculative generality beyond v1 requirements; each OS has different focus/return constraints.
- Windows-first proves the differentiating away-from-terminal case; portability can follow without changing the protocol.

### D. Inline-Reply-First (mirror Proposal A's emphasis)

Make the banner input box the primary interaction, as in the TUI variant.

**Rejected as the primary emphasis because:**

- Resolving a blocked agent needs the terminal's full context (scrollback, exact prompt, state).
- Precise one-click navigation to the waiting pane is higher-value than typing a reply blind from a banner.
- Inline reply is retained as a secondary convenience, not dropped.

## Consequences

### Positive

- Reaches the user who has left the terminal — the unserved gap that justifies the tool.
- The foreground/focus model and good UX coincide: the banner appears on top without stealing focus, and the terminal is raised only on a one-click user-chosen return.
- Full control over the slide-in, expand, templated-response, inline-bar, and stacking behavior — a faithful port of the mobile-notification model.
- Built first, it proves the core thesis end-to-end before the TUI channel is added.
- State-source behind the adapter means the tool improves automatically as ecosystem observability matures.

### Negative

- Windows-only in v1; other platforms unserved until a later portability pass.
- The custom banner reimplements chime, backlog persistence, DND-respect, and stacking that the native toast would provide for free — accepted in exchange for interaction fidelity.
- The Windows↔WSL return bridge is the fiddliest implementation piece — though it applies only to the WSL configuration and is avoided entirely when the user runs native psmux.
- Distinguishing blocked-vs-busy relies on pane scraping, which is imperfect.

### Risks

- Coarse or shared agent state (e.g. Claude Code subagent session IDs) can misattribute events; mitigated by keeping state behind the adapter and degrading gracefully.
- Terminal-on-second-monitor and no-foreground-window cases are ambiguous; mitigated by conservative escalation to the slide-in banner.
- A topmost-no-activate banner over a fullscreen or exclusive app can behave inconsistently; must be tested against fullscreen games/video and multi-monitor setups. Do **not** work around this by disabling the global focus-lock timeout.
- DND integration must be correct (queried via `FocusSessionManager`) or the tool becomes a distraction it was designed to avoid.
