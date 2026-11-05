# mgit: parity with lazygit, magit and neogit

The goal: grow mgit's functionality to the union of the useful features of
lazygit, magit and neogit, keeping the UI as it is (five modes, `Tab` cycles,
at most eight keys in the hint row, one key table, overlays for menus).
This file is the matrix and the plan. Counts are generated from the tables below.

## Sources and how reachable they were (2026-11-05)

| source | reached | used |
|---|---|---|
| lazygit `docs/keybindings/Keybindings_en.md`, `docs/Config.md`, `docs/Undoing.md` (raw.githubusercontent.com, master) | yes | every panel's keys (Files, Commits, Local branches, Stash, Reflog, Worktrees, Submodules, merge panel, main panel) |
| neogit `README.md`, `doc/neogit.txt` (master) | yes | the popup list: bisect, branch, branch config, cherry-pick, commit, diff, fetch, log, merge, remote, remote config, pull, push, rebase, revert, reset, stash, tag, worktree, ignore |
| magit manual (magit.vc/manual/magit, docs.magit.vc) | **no**: both URLs failed from this machine | the matrix uses the manual's chapter structure from memory (status sections, the transients for commit, fetch, pull, push, branch, merge, rebase, cherry-pick, revert, reset, stash, tag, remote, worktree, bisect, log, diff, blame, notes, submodule, patch, apply, am, ignore); rows that rest only on that memory are marked `M` and should be re-checked when the manual is reachable |

Forge features (pull requests, issues), AI features, external difftool/mergetool
and Neovim-only integrations (diffview, telescope) are out of scope: they need
network APIs or a host editor.

## How mgit's state was verified

Not from the docs: `ui/GIT_ui_keymap.entries()` (the one table that drives the
hint row, `?` and the palette) was read, mgit was built with m31c 0.9.0 and the
PTY harnesses (`tests/pty_rebase.py`, `pty_modes.py`, the new `pty_quick.py`)
drive the real binary beside real git 2.49 as the oracle. A row says `done`
only when a key reaches it in the running program.

## Matrix

Legend: `yes` = the tool has it. mgit state: done, partial, missing, oos (out of scope, reason given). Priority P1 = daily value, P2 = common, P3 = rare.

## Status / staging

| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Stage / unstage file | yes | yes | yes | done | - |
| Stage / unstage all | yes | yes | yes | done | - |
| Hunk staging and unstaging | yes | yes | yes | done | - |
| Line / range staging (visual select) | yes | yes | yes | done | - |
| Discard file / hunk / lines (confirmed) | yes | yes | yes | done | - |
| Untracked files shown and stageable | yes | yes | yes | done | - |
| Side-by-side diff | yes | - | - | done | - |
| Diff context size change (+/-) | yes | yes | - | partial: side-by-side has more/less context, unified is fixed | P2 |
| Ignore-whitespace toggle in diff | yes | yes | yes | missing | P2 |
| Edit hunk in the editor before applying | yes | yes | - | missing | P3 |
| Intent-to-add / stage one file as new | - | yes | yes | missing | P3 |
| File tree / compact tree view toggle | yes | - | yes | missing (flat list; fold per section only) | P2 |
| Collapse / expand all sections | yes | yes | yes | done | - |
| Ignore / exclude a file (gitignore, info/exclude) | yes | yes | yes | missing | P1 |
| Clean untracked (dry-run, force) from the UI | - | yes | yes | missing (CLI -clean exists) | P2 |
| Open file in external editor from status | yes | yes | yes | missing | P2 |
| Copy path / hash to clipboard | yes | - | - | oos: needs a clipboard API from the terminal (OSC 52 could be added) | - |
| Mark file resolved / stage after conflict | yes | yes | yes | done | - |
| Find base commit for fixup (ctrl+f) | yes | - | - | missing | P3 |
| Filter files by status | yes | - | - | missing | P3 |

## Committing

| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Commit with editor | yes | yes | yes | done | - |
| Commit message in-panel | yes | - | - | partial: Commit mode panel plus $EDITOR, no inline text input | P3 |
| Amend HEAD | yes | yes | yes | done | - |
| Amend HEAD without editing the message (extend) | yes | yes | yes | missing | P2 |
| Reword HEAD (amend message only) | yes | yes | yes | partial: A in Commit mode amends with the staged files too | P2 |
| Sign-off | yes | yes | yes | done | - |
| Commit without hooks (--no-verify) | yes | yes | yes | missing (mgit runs no hooks; see doc below) | P2 |
| Run hooks (pre-commit, commit-msg) on commit | yes | yes | yes | missing | P1 |
| GPG / SSH signing (-S) | yes | yes | yes | oos for now: refused with a clear message, no crypto in the runtime | - |
| Amend author / reset author / co-author | yes | yes | - | missing | P2 |
| Allow empty commit | - | yes | yes | missing | P3 |
| Fixup / squash! commit creation for a commit | yes | yes | yes | done (0.31.0: E, F) | - |
| Autosquash apply | yes | yes | yes | done (rebase menu s toggles; E a amends in one step) | - |
| Commit all (-a) shortcut | - | yes | yes | missing | P3 |
| Commit message history / templates | - | yes | - | partial: commit.template honoured | P3 |

## History / log

| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Commit list with graph | yes | yes | yes | partial: linear list; graph exists in core (log --graph) but not in History mode | P1 |
| Commit details and file list | yes | yes | yes | done | - |
| Commit file diff | yes | yes | yes | done | - |
| Search in log (text) | yes | yes | yes | done | - |
| Filter log by author / path / grep / -S / date | yes | yes | yes | missing | P1 |
| Log of a branch / ref / all refs | yes | yes | yes | partial: History is the current branch | P1 |
| Diff between two commits / refs / range | yes | yes | yes | missing | P1 |
| Diff against the selected ref (W menu) | yes | yes | - | missing | P1 |
| Copy hash / attribute | yes | - | - | oos: clipboard | - |
| Open in browser / PR links | yes | yes | yes | oos: forge integration | - |
| Tag a commit | yes | yes | yes | done | - |
| New branch off a commit | yes | yes | yes | partial: b n branches from HEAD only | P1 |
| Move unpushed commits to a new branch | yes | - | - | missing | P2 |
| Notes (add / edit / show) | - | yes | yes | missing | P3 |
| Blame file | yes | yes | yes | done | - |
| File history | yes | yes | yes | done | - |
| Blame at parent (re-blame) | - | yes | yes | done | - |
| Show commit (read-only view) | yes | yes | yes | done | - |
| Reflog browse | yes | yes | yes | done (0.31.0: L) | - |
| Sub-commits of a branch (enter on branch) | yes | yes | - | missing | P2 |

## Rewriting history

| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Interactive rebase with todo editor (pick, reword, edit, squash, fixup, drop, exec, break, reorder) | yes | yes | yes | done | - |
| Rebase from a commit (r h) | yes | yes | yes | done | - |
| Rebase --onto | yes | yes | yes | done | - |
| Rebase onto upstream / elsewhere / pushremote menu | yes | yes | yes | partial: branch picker; no separate pushremote/upstream shortcut | P2 |
| Rebase continue / skip / abort / edit todo | yes | yes | yes | done | - |
| Autostash | yes | yes | yes | done | - |
| Rebase --rebase-merges / --keep-base | - | yes | yes | missing | P3 |
| Rebase update-refs | - | yes | yes | partial: engine ignores update-ref lines in the todo, not offered | P3 |
| One-key reword / edit / drop / squash / fixup / move on a log commit | yes | yes | yes | done (0.31.0: E) | - |
| Amend an older commit with the staged changes | yes | yes | yes | done (0.31.0: E a) | - |
| Mark base commit for rebase (B) | yes | - | - | missing | P3 |
| Remove/modify a file from an old commit (patch building) | yes | - | - | missing | P2 |
| Custom patch across commits (apply to index, move to new commit) | yes | - | - | missing | P2 |
| Cherry-pick (menu: -x, -n, range, mainline) | yes | yes | yes | done | - |
| Cherry-pick copy / paste selection of several commits | yes | - | - | missing | P2 |
| Revert commit (menu) | yes | yes | yes | done | - |
| Continue / skip / abort of sequencer | yes | yes | yes | done | - |
| Reset soft / mixed / hard (menu) | yes | yes | yes | done | - |
| Reset --keep / --merge | - | yes | yes | missing | P3 |
| Undo / redo via reflog | yes | - | - | done | - |
| Worktree-file reset (checkout file from a commit) | yes | yes | yes | missing | P2 |

## Branches / tags / remotes

| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Switch / create / delete / rename branches | yes | yes | yes | done | - |
| Checkout by name / previous branch (-) | yes | yes | yes | partial: picker; no "-" shortcut | P3 |
| Force checkout | yes | - | - | missing | P3 |
| Create branch from any ref (start point) | yes | yes | yes | partial | P1 |
| Spin-off / spin-out (move commits to new branch) | yes | yes | yes | missing | P2 |
| Branch config (description, upstream, pushRemote, rebase) | - | yes | yes | missing | P2 |
| Set / unset upstream | yes | yes | yes | partial: push -u only | P1 |
| Fast-forward a non-current branch from upstream | yes | - | - | missing | P2 |
| Merge menu (ff, no-ff, ff-only) | yes | yes | yes | done | - |
| Squash merge | yes | yes | yes | missing | P1 |
| Merge --no-commit / preview / --abort | - | yes | yes | partial: abort yes; no-commit no | P2 |
| Tags: list, lightweight, annotated, delete | yes | yes | yes | done | - |
| Tag push / delete remote tag | yes | yes | yes | missing | P1 |
| Signed tags | - | yes | yes | oos: signing | - |
| Remotes: add / remove / rename / set-url / prune | yes | yes | yes | missing | P1 |
| Fetch (remote, all, prune, tags) | yes | yes | yes | partial: fetch the upstream remote | P1 |
| Pull variants (ff-only, rebase, merge) | yes | yes | yes | done | - |
| Push variants (set upstream, force-with-lease, tags, other remote, refspec) | yes | yes | yes | partial: push, push -u | P1 |
| Delete remote branch | yes | yes | yes | missing | P1 |
| Remote branches list and checkout | yes | yes | yes | partial | P2 |
| Create pull request, open PR in browser | yes | yes | yes | oos: forge APIs | - |
| git-flow | yes | - | - | oos: separate tool, not git core | - |

## Stash

| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Stash push / untracked / keep index / message | yes | yes | yes | done | - |
| Stash staged only / unstaged only | yes | yes | yes | missing | P1 |
| Stash pop / apply / drop / branch | yes | yes | yes | done | - |
| Stash list with diff | yes | yes | yes | done | - |
| Stash apply --index | - | yes | yes | done | - |
| Rename a stash | yes | - | - | missing | P3 |
| Snapshot / wip modes | - | yes | - | missing | P3 |

## Conflicts

| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Merge conflict view (ours, theirs, both, base, edit) | yes | yes | yes | done | - |
| Undo last choice | yes | - | - | done | - |
| Resolve all conflicts of a file at once | yes | yes | yes | done | - |
| Rerere | - | yes | - | missing | P3 |
| Ediff / external merge tool | - | yes | yes | oos: external tools | - |

## Bisect, worktrees, submodules, advanced

| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Bisect (start, good, bad, skip, reset, run) | yes | yes | yes | missing | P1 |
| Worktrees (list, add, remove, switch) | yes | yes | yes | missing in the UI (CLI has them) | P1 |
| Submodules (list, init, update, add, remove, enter) | yes | yes | yes | missing | P2 |
| Patch: apply / am / format-patch | - | yes | yes | missing | P2 |
| Range-diff | - | yes | - | missing | P3 |
| Sparse checkout | - | yes | - | oos: very rare in TUI use | - |
| Git LFS | - | yes | - | oos | - |
| Command log | yes | yes | yes | done | - |
| Custom commands (user config) | yes | - | - | missing | P1 |
| Command palette / fuzzy | yes | yes | yes | done | - |
| Shell command prompt (:) | yes | yes | yes | missing (":" is the palette) | P2 |
| Config file with keybinding overrides | yes | - | - | missing | P2 |
| Mouse support | yes | - | - | done | - |
| Auto refresh on file changes | yes | yes | yes | done | - |
| Recent repos switch | yes | - | - | missing | P3 |
| Diff via difftool | yes | yes | yes | oos: external tool | - |
| Diffview / telescope integration | - | - | yes | oos: Neovim-only | - |
| Copilot / AI commit message | - | - | - | oos: not in any of the three core sets | - |

## Counts (128 rows, after 0.31.0)

| state | rows |
|---|---|
| done | 50 |
| partial | 16 |
| missing | 49 |
| out of scope | 13 |

(Rows counted as `done (0.31.0)` are included in done: reword/edit/drop/squash/fixup/move
of a log commit, amend an older commit, fixup! creation, autosquash apply, reflog browse.)

## Milestone log

### 0.31.0 (this branch)

Found already done before this work, contrary to the milestone-1 list in the brief: hunk and
line staging (`v` in the diff), interactive rebase with the todo editor, cherry-pick/revert menus,
stash menu with untracked/keep-index/message, the reset menu, conflict resolution (ours, theirs,
both, base, edit), undo/redo from the reflog. They were verified, not rewritten.

Added: **`E` in History**, a commit edit menu on the commit under the cursor (r reword, e edit,
d drop with confirmation, s squash down, f fixup down, k/j move up/down, a amend with the staged
changes via `fixup!` + autosquash with autostash, F make a `fixup!` commit). It builds the todo
and starts a real `.git/rebase-merge` rebase, so `r c`/`r s`/`r a` and `Z` work on it.
**`L` in History**, the HEAD reflog as a list: Enter/G reset menu, o detached checkout, A cherry-pick.
Tests: `tests/pty_quick.py` (31 checks, each compared with `git rebase -i`, `git commit --fixup`,
`git reset`; fsck clean) wired into `tests/test_rebase.sh`.

### Next, in priority order

1. P1: filter/search the log (author, path, grep, -S), log of another ref, history graph column, diff between refs.
2. P1: remotes management, tag push/delete remote, delete remote branch, force-with-lease and other-remote push, upstream set/unset, squash merge, stash staged/unstaged only.
3. P1: bisect UI, worktrees UI, custom commands config file, ignore file, hooks on commit.
4. P2: submodules, cherry-pick copy/paste, patch building, file tree toggle, clean, notes, shell prompt, config for keys.
