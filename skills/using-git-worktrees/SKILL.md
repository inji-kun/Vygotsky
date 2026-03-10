---
name: using-git-worktrees
description: "Use when starting feature work that needs isolation from the current workspace. Creates git worktrees with safety checks and keeps the human oriented on which directory holds which state."
---

# Using Git Worktrees

## The Rule

**The human must always know which worktree they're in and what state it holds.**

Worktrees are powerful but disorienting. Two copies of the repo, different branches,
different working states. If the human loses track of which directory has which code,
they'll make changes in the wrong place.

## Before Creating

### 1. Check Understanding

Call `check_concept` for git worktrees. If the diary has no entries:
- "Quick context — a worktree gives us a second checkout of the repo in a separate
  directory, on its own branch. Changes in one don't affect the other. We'll use it
  to keep main stable while we work."

If the diary shows prior experience, skip to creation.

### 2. Safety Checks

Before `git worktree add`:
- Verify the target directory doesn't already exist
- Confirm the branch name doesn't conflict
- Check for uncommitted changes in the current worktree — they won't carry over

### 3. Create and Orient

After creation, state clearly:
- "Worktree created at `/path/to/worktree` on branch `feature-x`."
- "Your main repo at `/path/to/main` is still on `main` — untouched."

## During Work

### When Switching Worktrees

Always orient:
- "Switching to the feature worktree at `/path/to/worktree` — this has our
  in-progress changes on `feature-x`."

### When Running Commands

If running commands that depend on directory (tests, builds), confirm which
worktree you're in before executing.

## Cleanup

When work is done and merged:
- `git worktree remove` the finished worktree
- Confirm the directory is gone
- "Back to just the main worktree now."

## Anti-Rationalization

| Rationalization | Reality |
|----------------|---------|
| "They know which directory they're in" | Two worktrees means two chances to be confused. State it. |
| "Worktrees are simple, no need to explain" | Simple concept, easy to lose track of in practice. Orient every time. |
| "I'll skip the safety checks, it's faster" | A conflicting worktree wastes more time than the check takes. |
