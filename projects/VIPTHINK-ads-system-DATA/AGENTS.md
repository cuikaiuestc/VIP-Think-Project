# AGENTS.md instructions for this project

## Goal Gate

When the user writes `/goal`, or asks to start, rebuild, launch, automate,
publish, package, push to GitHub, or run a broad multi-step task, do not treat
that wording as immediate execution approval.

First run a Goal Gate check:

- `allow`: the task is long-running, multi-step, verifiable, and has clear
  acceptance criteria.
- `refine`: the task lacks outcome, scope, allowed actions, non-goals,
  acceptance criteria, or stop condition.
- `reject`: the task is a one-shot question, small edit, status check, or
  ordinary advice request.
- `plan-first`: the task involves GitHub changes, public release, production,
  recurring automation, credentials, account permissions, private data, or
  irreversible actions.

If allowed, rewrite the user's rough input into a stricter `/goal` prompt before
execution. If refine or plan-first, pause and ask for the missing information or
confirmation. If rejected, explain briefly and handle it as a normal task.
