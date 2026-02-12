# Task Proposals from Codebase Review

## 1) Typo fix task
**Task:** Correct the product name typo in the help output from `Termichat` to `TermiChat`.

- **Why:** The branded name is spelled `TermiChat` in the header/UI, but the `/help` text currently says `Termichat`, which looks inconsistent and unpolished.
- **Where:** `app/ui.py` (`show_help` function).
- **Acceptance criteria:** `/help` consistently shows `TermiChat` (capital `C`) everywhere.

## 2) Bug fix task
**Task:** Stop exiting the process during module import when `TERMI_API_KEY` is missing; defer validation until runtime command handling.

- **Why:** `app/config.py` currently calls `sys.exit(1)` at import time if the key is not set. This prevents the app from running non-API flows (e.g., `/doctor`) that should help users diagnose missing configuration.
- **Where:** `app/config.py`, plus call sites that rely on `API_KEY` (`app/chat.py`, `app/doctor.py`).
- **Acceptance criteria:**
  - App can start without `TERMI_API_KEY`.
  - `/doctor` runs and reports missing key cleanly.
  - API calls still fail fast with actionable messaging when key is absent.

## 3) Comment/documentation discrepancy task
**Task:** Align command documentation with actual supported commands by adding `/doctor` to the help text and README usage docs.

- **Why:** `/doctor` is implemented in `app/chat.py` but omitted from `show_help`, and README currently provides no command reference.
- **Where:** `app/ui.py` (`show_help`) and `README.md`.
- **Acceptance criteria:**
  - `/help` lists `/doctor`.
  - README includes a minimal command section matching implemented commands.

## 4) Test improvement task
**Task:** Add unit tests for message conversion and command behavior, with emphasis on `_to_responses_input` and startup behavior without API key.

- **Why:** There is no test suite currently; regression risk is high for API payload formatting and config handling.
- **Where:** New test module(s), e.g. `tests/test_chat.py` and `tests/test_config.py`.
- **Suggested coverage:**
  - `_to_responses_input` drops assistant messages and preserves system/user payload shape.
  - Empty/whitespace input handling does not send blank user messages.
  - Missing `TERMI_API_KEY` no longer terminates import path (after bug fix task).
- **Acceptance criteria:** Tests run in CI and fail on regressions in these areas.
