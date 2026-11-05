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
| magit manual: `magit.org` / `magit.texi` in magit/magit `docs/` (raw.githubusercontent.com, main) | yes (magit.vc and docs.magit.vc were not reachable; the repository copy was) | the chapter structure: Inspecting (status, logging, reflog, cherries, diffing, ediffing, references buffer, bisecting, blaming), Manipulating (staging, applying, committing, branching, merging, conflicts, rebasing, cherry-picking, reverting, resetting, stashing), Transferring (remotes, fetching, pulling, pushing, plain and maildir patches), Miscellaneous (tagging, notes, submodules, subtree, worktree, sparse checkouts, bundle, wip modes) |

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
| Commit list with graph | yes | yes | yes | done (0.32.0: `f` then `G`; the lane markers of the commit rows, not the connector rows) | P1 |
| Commit details and file list | yes | yes | yes | done | - |
| Commit file diff | yes | yes | yes | done | - |
| Search in log (text) | yes | yes | yes | done | - |
| Filter log by author / path / grep / -S / date | yes | yes | yes | partial: author, message, path, -S done (0.32.0, `f`); no date range | P1 |
| Log of a branch / ref / all refs | yes | yes | yes | partial: any branch, tag or commit done (0.32.0, `f r`); not `--all` | P1 |
| Diff between two commits / refs / range | yes | yes | yes | done (0.32.0: `f d`, A..B, A...B, A against HEAD) | P1 |
| Diff against the selected ref (W menu) | yes | yes | - | done (0.32.0: `f D`) | P1 |
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
| Set / unset upstream | yes | yes | yes | done (0.33.0: `b u` / `b U`) | P1 |
| Fast-forward a non-current branch from upstream | yes | - | - | missing | P2 |
| Merge menu (ff, no-ff, ff-only) | yes | yes | yes | done | - |
| Squash merge | yes | yes | yes | done (0.33.0: `m s`; the commit takes SQUASH_MSG as its message) | P1 |
| Merge --no-commit / preview / --abort | - | yes | yes | partial: abort and --no-commit (`m x`, 0.33.0) done; no preview | P2 |
| Tags: list, lightweight, annotated, delete | yes | yes | yes | done | - |
| Tag push / delete remote tag | yes | yes | yes | done (0.33.0: `T` then `P` / `X`) | P1 |
| Signed tags | - | yes | yes | oos: signing | - |
| Remotes: add / remove / rename / set-url / prune | yes | yes | yes | done (0.33.0: `M` in Branches) | P1 |
| Fetch (remote, all, prune, tags) | yes | yes | yes | done (0.33.0: `F` then f, a, x, t, o) | P1 |
| Pull variants (ff-only, rebase, merge) | yes | yes | yes | done | - |
| Push variants (set upstream, force-with-lease, tags, other remote, refspec) | yes | yes | yes | partial: push, -u, force-with-lease, tags, other remote (0.33.0, `P`); no custom refspec | P1 |
| Delete remote branch | yes | yes | yes | done (0.33.0: `P d`) | P1 |
| Remote branches list and checkout | yes | yes | yes | partial | P2 |
| Create pull request, open PR in browser | yes | yes | yes | oos: forge APIs | - |
| git-flow | yes | - | - | oos: separate tool, not git core | - |

## Stash

| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Stash push / untracked / keep index / message | yes | yes | yes | done | - |
| Stash staged only / unstaged only | yes | yes | yes | partial: staged only done (0.33.0, `z s`; a file with both staged and unstaged changes is refused); unstaged only is `z k` (keep index) | P1 |
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

## Added after reading the magit manual
| feature | lazygit | magit | neogit | mgit state | priority |
|---|---|---|---|---|---|
| Cherries (`git cherry`: which commits of a branch are not upstream) | - | yes | - | missing | P3 |
| References buffer (all branches and tags with their tips, compare) | - | yes | - | partial: Branches mode lists local branches and tags are in `T` | P2 |
| Repository list (several repositories) | yes | yes | - | missing | P3 |
| Applying a patch or hunk to the work tree or index (`a`) | yes | yes | yes | partial: custom patch not built; hunks staged | P2 |
| Maildir patches (`git am`) and plain patches (`git apply`) | - | yes | yes | missing | P2 |
| Subtree commands | - | yes | - | oos: rarely used, shells out to a contrib script | - |
| Bundle | - | yes | - | missing | P3 |
| Wip modes (autosave to refs/wip) | - | yes | - | missing | P3 |
| Visit a file at a revision (blob view) | - | yes | yes | partial: the blame and commit views show blobs' diffs | P3 |

## Counts

Generated by `python3 scripts/parity_counts.py` (137 rows after 0.33.0):

| state | rows |
|---|---|
| done | 59 |
| partial | 18 |
| missing | 46 |
| out of scope | 14 |

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

### 0.32.0

`f` in History: the log menu. Filter by author, message, path or `-S`; the log of another branch, tag or
commit; the graph column (git's own graph state machine, commit rows only); diff of two refs (`A..B`, `A...B`,
`A` against HEAD) and of the commit under the cursor against HEAD. `tests/pty_log.py` (22 checks, `tests/test_log.sh`)
compares the commits shown with `git log` for each filter and the diff totals with `git diff --numstat`.
Filters are plain substrings, not regular expressions, and look at the newest 2000 commits; the path filter uses
the first-parent diff of each commit.

### 0.33.0

Remotes and sync. `M` in Branches: the remotes list (add, remove, rename, set the URL, prune, fetch; run by the
library's own `git remote` code). Push menu: `f` force-with-lease, `t` tags, `o` another remote, `d` delete a remote
branch. Fetch (in the `F` menu): `a` all, `x` prune, `t` tags, `o` a named remote. Tags: `P` push, `X` delete on
the remote. `b u` / `b U` set and unset the upstream. `m s` squash merge, `m x` merge without the commit. `z s`
stash the staged changes only. Network operations run on the terminal like the existing fetch and push, so
credentials, progress and errors are git-compatible. Tests: `tests/pty_local.py` (17 checks) and
`tests/pty_remotes.py` (24 checks, a local `git http-backend`), beside twin repositories changed by real git.

### Next, in priority order

1. P1: bisect UI, worktrees UI, custom commands config file, ignore file, hooks on commit.
2. P2: submodules, cherry-pick copy/paste, patch building, file tree toggle, clean, notes, shell prompt, config for keys.
