# ADR-001: TUI Interrupt Notifier

**Status:** Proposed &nbsp; **Date:** 2026-07-10 &nbsp; **Proposal:** A (user still in a terminal)

## Context

Developers run multiple terminal-based AI agents that work autonomously for minutes at a time. While an agent works, the user moves to another command, another pane, or another tmux session — but stays *within a terminal*. When an agent finishes or blocks needing input, the user has no graceful way to find out and act without babysitting the session or manually checking back.

The community has built agent-monitoring tools (session lists, agent trees, cost meters) and there is an active proposal for a native Claude Code dashboard, but all of them assume the user is **present and looking at a dashboard surface**. None addresses the *interrupt* moment for a user who has shifted attention to a different pane. The valuable moment is: an agent needs the user right now, and the user is looking elsewhere in the terminal.

Key constraints in the terminal environment:

- Pane/window focus is only knowable in-band via **focus event reporting** (a terminal mode that tells a program when its window gains or loses focus).
- **tmux is a hostile environment** for focus reporting: it relays events only when `focus-events on`, fires spurious startup events, and can leak escape sequences as text.
- The kitty keyboard protocol (CSI u) is unevenly supported under tmux and can introduce input latency.

## Decision

Build a **TUI Interrupt Notifier** delivered as a floating, ephemeral overlay in the idiom of fzf's `Ctrl-R`, consisting of:

### 1. Harness Adapters + Two-Stage Protocol

A two-stage protocol shared with Proposal B. The **adapter** (one per harness) parses harness log output into a structured extraction — semantic state (`working`, `done`, `needs_input`, `error`), the raw prompt text, candidate options, and a pane locator. The **orchestrator** turns that into the user-facing interrupt: the gist phrased as a question, the templated responses, the "Something else…" custom-reply option, and the lifecycle. Harness-specific parsing stays in the adapter; question-phrasing and templating stay shared in the orchestrator.

### 2. In-TUI Attention Detection

Use focus event reporting as the primary focus signal, with explicit tmux handling: detect `$TMUX`, check/guide `focus-events`, debounce spurious startup events, and guard against sequence leakage. Treat tmux as a first-class test target.

### 3. Floating Overlay Delivery

A transient overlay in the focused pane (prior art: `fterm.nvim`, `floaterm`), never persistent. It drops down, dwells for a configurable period (default 10s) for the user to interact, then slides back up into the backlog stack if untouched; interacting cancels the dwell timer. Lighter events get a tmux status-line nudge or a chime instead.

### 4. Inline Action Surface (primary emphasis)

The gist is phrased as a question; the user answers with contextual templated responses or a "Something else…" freeform prompt bar, routing the response back through the adapter without leaving the current pane. This is the highest-value element for a user already in a terminal.

### 5. Jump-to-Pane (secondary emphasis)

A keystroke that focuses the exact waiting pane via fully-qualified tmux targets, for interrupts deserving full attention.

### 6. Pull Surface (backlog stack)

An on-demand, newest-first stack of unresolved interrupts. Each interrupt is tracked through a lifecycle (`raised → acknowledged → resolved / superseded`) and **stays in the stack until its specific interrupt is resolved** (or the agent supersedes it) — glancing at it is not enough. The only review affordance in v1 — explicitly not a dashboard.

## Alternatives Considered

### A. Persistent In-Terminal Dashboard

A standing tree/status surface showing all agents at once.

**Rejected because:**

- It serves the *present-and-looking* user, not the user who shifted attention — the wrong moment.
- A persistent surface reintroduces the always-visible clutter good notification design avoids.
- It duplicates existing dashboard proposals rather than filling the interrupt gap.

### B. Terminal Bell / `notify-send` Only

Fire a bell or a generic desktop notification on state change.

**Rejected because:**

- No routing to where the user's attention is, no state semantics, no inline action, no backlog.
- Fire-and-forget: the user still has to hunt for which pane needs them.

### C. tmux Status-Line Only

Encode agent state into the tmux status line.

**Rejected as the primary solution because:**

- A single status line cannot carry a body, expandable detail, or inline actions.
- No interaction model. It *is* retained as the lighter, non-urgent nudge channel.

### D. Full Interactive Adapters (drive the agent)

Let adapters inject replies directly into a running agent's stdin.

**Rejected because:**

- It makes adapters complex, stateful interactive drivers rather than simple observe-and-launch components.
- The inline surface already routes responses back through a narrow, well-defined path; full driving is unnecessary for v1.

### E. Require Agents to Emit Structured Interrupt Events

Depend on each harness to emit a clean `summary` + `suggestedActions` itself, rather than parsing the log.

**Rejected because:**

- Most harnesses do not emit structured interrupt events today; requiring it would limit the tool to a handful of cooperating agents.
- Parsing the log tail works with *any* harness that prints to a pane, which is all of them — broader reach for v1.
- The chosen split keeps the fragile parsing per-adapter and can still *consume* structured events later where a harness offers them, without changing the orchestrator or protocol.
- Trade-off accepted: log-parsing is imperfect and is the riskiest component (see Risks), but it is the price of harness-agnostic reach.

## Consequences

### Positive

- Users get a graceful, proportional interrupt without leaving their current pane.
- Inline actions remove the context switch that makes managing many agents painful.
- Phrasing the gist as a question with ready responses makes triage fast and low-effort.
- The ephemeral overlay respects attention — absent by default, present only on relevance.
- The adapter/orchestrator/protocol layer is shared with Proposal B, so both variants reuse it.
- Adding a new harness is one adapter (parsing only) — a clean contribution point.

### Negative

- Focus event reporting under tmux is genuinely fiddly and needs a dedicated test matrix.
- The overlay must integrate with whatever renders the focused pane, which varies by terminal.
- Per-interrupt lifecycle state must be tracked and reconciled (resolved, superseded) so the stack neither drops unresolved items nor keeps stale ones.
- Log-parsing and question-phrasing add a component whose output quality varies by harness.

### Risks

- tmux focus quirks (spurious events, sequence leakage) could degrade the primary signal; mitigated by explicit detection and guards.
- Uneven CSI u support under tmux may introduce input latency in the prompt bar; mitigated by keeping the tmux path under its own test matrix.
- Overlay rendering across the diversity of terminal emulators may need per-terminal handling.
- **Log-parsing is the riskiest part**: mis-parsing "blocked waiting" vs "still working", or extracting wrong candidate options, produces a misleading question. Mitigated by keeping parsing per-adapter, defaulting to a conservative "agent needs you (open to see)" phrasing when confidence is low, and always offering "Something else…" so the user is never boxed in by bad templates.
