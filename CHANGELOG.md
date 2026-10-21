# Changelog

Each release's changes in one place (the details are in `README.md` and
`docs/GIT-COMPAT.md`).

## 0.29.0

- **Screen corruption on real Macs: pins tui 0.13.0** (f67234d; see its CHANGELOG). Opening mgit's help over a status list whose
  names hold a text emoji or a keycap left pieces of the names inside the overlay on a terminal that measures them
  differently (`tests/pty_variants.py` below, on the unchanged 0.28.0 binary: 10 of 17 steps wrong on 7 emulated
  terminals; here the help screen showed `U  t  unstage all`). tui 0.13.0 writes rows with clusters of uncertain width
  whole from the cluster to the end of the row, clears the column a narrower terminal leaves undrawn, turns autowrap
  off, and clears the screen on a full repaint.
- CTRL-L redraws the whole screen (`Loop.should_repaint_on_ctrl_l`); mgit had no such key.
- mgit picks its colour depth from `COLORTERM`, `TERM_PROGRAM` and `TERM` (`TUI_style.detect_depth`). It wrote 24-bit
  colours to every terminal; Terminal.app has none before macOS 26 and misreads `38;2;r;g;b` as other attributes.
- `tests/pty_variants.py` (run by `tests/test_loop.sh`; skips when `pyte` is missing): mgit driven over a repository whose names
  and diffs hold text emoji, keycaps, ZWJ sequences, Devanagari, halfwidth katakana, Nerd Font and new-emoji glyphs
  (selection moves, folds, the mode keys, help, resizes), replayed on seven emulated terminals; after each step every
  terminal's screen must equal that terminal's own repaint. Built and tested against m31 v0.9.0 and tui v0.13.0.
- The advertised user agent is `1git/0.29.0`.

## 0.28.0

- **mgit runs on tui's `Loop.run_with`; the private copy of the loop is gone.** `ui/GIT_ui_loop.m31`
  (`GIT_ui_loop.run`, a copy of `TUI_app.Loop.run` that called a ticker on every timed-out read) is deleted;
  nothing else used it. The new `ui/GIT_ui_app.m31` has `App`, which is the `Widget`, the `Handler` and the
  `Ticker` the loop is given, and `make_loop`, the loop's settings in one place (public, tested by
  `tests/t_loop.m31`). The migration follows tui-markdown 0.6.0 and 0.7.0 (`MDV_cli.make_loop`,
  `App`/`Screen` as `Handler`/`Ticker`/`AfterFrame`, tui's README mapping table). Built and tested against
  m31 v0.9.0 and tui v0.12.0 (ed5513a).
  - **Nothing changes for a user with `--sync off`; the bytes written to the terminal are identical to
    0.27.1.** Checked by driving both binaries through the same 21 scripted sessions under a pty
    (577 steps, 259532 bytes of output per binary; the harness is not in the repository, it needs a 0.27.1
    binary to compare with): every
    mode and its help and palette, the unified and side-by-side diff (keys, wheel, click, widening, staging
    lines), the merge, cherry-pick, revert and rebase overlays and flows (a conflict, the resolution view, an
    abort, a continue), the stash menu and list, the tag and branch menus, the commit flow (sign-off, amend,
    discard), the editor suspended and resumed (a stand-in `$EDITOR` that succeeds, one that fails, one that
    does not exist), a branch name taken from `$EDITOR`, mouse reports in every mode, resizes (also to
    5x20 and 50x200), bracketed paste, bursts of keys, the idle auto-refresh after files changed behind its
    back, escape sequences and a lone Escape, `--mouse off`, an 8x30 and a 60x220 terminal. Run twice on
    0.27.1 the output is itself identical byte for byte (the clock is fixed with a preloaded shim so commit
    ids repeat; after a step that changes the repository the harness waits for the auto-refresh to land).
    With `--sync off` the 0.28.0 output is the same file (same md5, 8a1666c48d9dedddf5dade2eacdd6091).
  - What the settings keep: one frame per event (`drain_events` 0: tui's default is one frame per burst of
    events, which would write fewer, different frames); mouse reports asked for with
    `should_report_raw_mouse` (the same modes as before, no motion) and passed to mgit's own hit testing
    unrouted; no paste, focus or keyboard mode; `tick_ms` 250 ms; keys from standard input; the terminal
    given back and taken again around `$EDITOR`, which still ends the loop and starts it again.
  - **The escape wait is the old one (tui 0.12.0).** Moving onto `run_with` first changed a lone Escape from
    a fixed 250 ms to 1 to 250 ms: the loop's read timeout is `min(tick_ms, time to the next tick)` and
    `term.Reader.read` resolves a lone Escape only on a timeout, so a tick could shorten the wait to 1 ms
    (and an arrow key's bytes arriving a few ms apart, as over a slow link, could be read as Escape plus
    two characters). tui 0.12.0 added `Loop.escape_wait_ms` for this (found by this migration, and it needs
    m31 v0.9.0's `term.Reader.read_keys`); `make_loop` sets it to 250, so a lone Escape, or a held start of an
    escape sequence, waits 250 ms for more input counted from the last byte, whatever the timer does.
    Checked by `tests/t_loop.m31` and `tests/pty_loop.py` (`ESC [ B` written in two pieces 80 ms apart is one
    key at twelve phases of the timer; a lone ESC quits).
  - **One difference in time, not in bytes.** The auto-refresh ticker (`GIT_ui_autorefresh`) is now called by
    the loop's timer every 250 ms, also while keys arrive; a tick that follows an event is not counted, so the
    repository is still polled after about a second of idleness (every `POLL_TICKS`-th idle tick), but the
    phase of the polls is that of the timer, not of the last key.
    `AutoRefresh.did_change_on_tick()` is now `AutoRefresh.tick(elapsed_ms)` (it answers a
    `TUI_app.Action`, `Redraw` when the repository changed) and `AutoRefresh.note_input()` is new.
- **tui is pinned to v0.12.0** (`ed5513a`, was v0.11.0, `e156723`); `syntax` stays at `e49e01c`, which tui
  v0.12.0 pins too. **m31 v0.9.0 is the toolchain** (tui 0.12.0 needs it): the workflows' `M31_REF` and
  `M31_MUSL_REF` are v0.9.0 (they were v0.6.0).
- **`--sync on|off|auto`: synchronized output (DEC mode 2026).** Each frame is written between `CSI ? 2026 h`
  and `l`, so a terminal shows it whole, never half drawn. It is on by default (`auto`): the terminal is asked
  (DECRQM) when mgit starts and the markers are written only after it answers that it has the mode (set,
  reset or permanently set); a terminal that does not answer, or answers "not recognised", gets the frames it
  got before. `auto` does not ask Terminal.app (it prints queries it does not know) or a dumb terminal
  (`TERM` unset, `dumb`, `linux`, `vt100`, `ansi`); `on` asks every terminal; `off` asks none and writes
  the bytes of 0.27.1. Oro's grammar: a value option (`--no-sync` is refused, like `--no-mouse`), and no short
  form, because one-letter forms are for what is typed daily (`docs/CLI.md`). With the answer given and the
  markers and the question taken out of the output, the 0.28.0 bytes are again those of 0.27.1 (checked on
  the same 21 sessions). `mgit --help`, `docs/CLI.md` and the completions (`bash`, `zsh`, `fish`) list it;
  the help and the three scripts are goldens now (`tests/golden/cli/mgit-*.txt`).
- **No clipboard.** mgit has no copy action, so `Loop.copy` (OSC 52) is not used.
- **For programs that use m31git as a library:** `ui.GIT_ui_loop` is gone (it was a copy of tui's loop; use
  `TUI_app.Loop.run_with` with a `Ticker`); `GIT_ui_autorefresh.AutoRefresh` implements `TUI_app.Ticker`
  (`tick`) instead of `GIT_ui_loop.Ticker` (`did_change_on_tick`).
- Tests: `tests/t_loop.m31` (the loop's settings against the loop 0.27.1 ran on, the `--sync` rule, the
  ticker's idle counting), `tests/pty_loop.py` (the bytes under a pty: entry and exit, `--sync` asked or not,
  markers only after an answer, the editor handoff), `tests/test_loop.sh`, and the mgit help and completion
  goldens in `tests/test_cli.sh`.

## 0.27.1

- **A program can now depend on m31git together with tui 0.9 or later.** m31 allows one
  source per dependency name across a whole build, and m31git pinned tui v0.8.0
  while the m3 editor (and anything else on tui 0.9.1 or later) pins a newer one, so the
  two could not be built together and downgrading the consumer did not compile. The
  pin below is the whole fix for that: m31git builds and passes against tui v0.11.0,
  and its `syntax` pin is the commit tui v0.11.0 uses, so both names resolve to one
  source. A consumer's `deps` names `tui` at v0.9.1 or later (v0.11.0 is what m31git is
  tested with), `syntax` at `e49e01c` and m31git at this version.
  Checked by compiling m3dit 0.11.0's `m3.m31` with `deps` naming tui v0.11.0, syntax
  `e49e01c` and this m31git.
- **For programs that use m31git as a library:** `GIT_index.Error` has three new
  variants (`RequiredExtension`, `Locked`, `Changed`), and `match` has no default, so a
  `match` over it has to handle them (m3dit's `ui/MED_gitlib.m31` has two, each needs
  three empty cases). `GIT_index.Index` has a new field `base` and `GIT_index.Entry`
  one (`ext_flags`), both with defaults, so the constructors keep their arguments.
- **tui is pinned to v0.11.0** (`e156723`, was v0.8.0, `57a63af`); `syntax` stays at
  `e49e01c`, the commit tui v0.11.0 itself pins, so the two resolve to one source. What
  the newer tui does to mgit's screens, checked against every pty suite, the unit
  programs that import tui and the side-by-side goldens:
  - 0.9.1 draws a control character in a cell as its Control Picture (U+2400 + code)
    where it used to write the raw byte. The blame overlay put each file line, newline
    included, in a cell, so every row would have ended in a visible `U+240A`; the overlay
    now cuts the line terminator (`GIT_ui_blame.without_eol`). Every other screen was
    scanned for Control Pictures across the pty suites and has none.
  - 0.9.0 to 0.11.0's other changes (emoji and ZWJ width fixes, a skin tone after a text
    base, synchronized output, OSC 52/8, keyboard protocols, the after-frame hook) are
    opt-in or touch only clusters of uncertain width; mgit enables none of them.
    Synchronized output is not turned on: mgit runs its own copy of the loop
    (`GIT_ui_loop.run`), so it is not a one-line opt-in.
  - **Golden changes: none.** `tests/golden/sbs` and `tests/golden/cli` are byte for byte
    what they were.
- Tests: `tests/pty_blame_undo.py` checks that no blame row holds a Control Picture.
- **The index writer follows git's lock protocol** (`GIT_index.write`). It takes
  `index.lock`, writes the new index there and renames it over `index`; if the lock
  exists it writes nothing, leaves the lock alone and says `index.lock exists`
  (`GIT_index.Error.Locked`). An index that git or another process wrote after this
  program read it is not overwritten (`Error.Changed`, "changed by another process").
  The language has no exclusive create (`O_EXCL`), so the lock is taken with a
  symbolic link, the one exclusive and atomic create there is, and the finished file is
  renamed over the link; git sees a lock either way. Where links cannot be made
  the lock is a plain file made after a check, which is not exclusive.
- **mgit and 1git wrote an entry size of -1**, which the file stores as 4294967295; git
  trusts a non-zero size that differs from the file's, so a fully staged hunk showed as
  `MM` (and a staged new file as `AM`). Every such entry (`GIT_index.without_stat`: staging
  a hunk or lines, unstaging, a stash that restores the index) now has times and size 0,
  byte for byte what `git update-index --cacheinfo` and `git apply --cached` write.
- **Entry flags and the other index extensions** (what the writer does, written down in
  `GIT_index.m31` and `docs/GIT-COMPAT.md`): intent-to-add and skip-worktree flags were
  dropped by every write (an `add -N` entry became a staged empty file); they are kept
  now, and an index with one is written as version 3, as git does. `TREE`, `UNTR`, `FSMN`,
  `EOIE` and `IEOT` are dropped (git rebuilds them); `REUC` is dropped too, which costs
  `git checkout -m -- <path>` and `git update-index --unresolve` a resolved conflict.
  dev, ino, uid and gid stay 0 (the library has no way to read them), which costs git one
  re-hash. A split index (`link`) or a sparse index (`sdir`) used to be read as if the
  file held every entry and was then overwritten; it is refused when read
  (`Error.RequiredExtension`).
- Tests: `tests/test_index_write.sh` (and `tests/run_index_write.sh` for it alone)
  builds twin repositories from one byte copy, does the operation with real git and with
  this program and compares the entries byte for byte (`tests/oracles/index_entries.py`),
  `ls-files --debug`, `status --porcelain`, `write-tree` and `fsck --strict`; it also
  covers an existing `index.lock`, a dangling one, git writing the index in the middle,
  extended flags, the dropped extensions, a split index and `1git add` under a lock.
  `tests/pty_lines.py` compares each staged entry's size and the porcelain status with
  `git apply --cached`'s.

## 0.27.0

- **1git: git's argument form is gone** (deprecated since 0.24.0, removal promised
  for 0.27.0). `1git log --oneline -n 5` is refused like any bare word (exit 2,
  nothing runs) with a one-line hint naming the new spelling, `1git -log --oneline
  --max 5`; a line with an option 1git no longer has gets a hint that says it has no
  equivalent. `1git -migrate 'git ...'` stays and prints the new line. `pull` runs
  merge, rebase and checkout again in git's grammar for itself, through
  `M31GIT_INTERNAL_ARGV=1`, which is for the program's own re-runs and not a spelling
  for people. The oracle scripts run the forms 1git no longer has through that
  internal path, so the code behind them keeps its checks, and say how many. Tests: `tests/test_cli.sh` checks that each of the
  old forms of `tests/cli_cases.txt` is refused with the hint `-migrate` gives, that
  nothing runs, and that the new form runs.
- **mgit: git's leftover `COMMIT_EDITMSG` is not a draft.** git keeps the file after
  every commit, and the Commit panel showed its message as if it were a draft (and `f`
  would have committed it again). A file older than HEAD's reflog (or, on a tie of timestamps,
  saying what HEAD's commit says) is now `(none yet: e to write one)`, is not committed by `f`, and
  `e` starts from the template; an amend's prefilled message is still a draft.
- **mgit: the "key moved" notice is said once, not once per session.** The keys already
  told about are kept in `$XDG_STATE_HOME/m31git/notified` (default
  `~/.local/state/m31git/`), written atomically; `M31GIT_STATE=off` reads and writes
  nothing, and the test runs set it.
- **mgit: the command palette lists every action**, including one whose binding has no
  key (`[no key]`).
- **mgit: a refused detached checkout names the file** that blocks it (`check out
  refused: a.txt has local changes (HEAD stays)`, `an untracked file is
  in the way of x.txt`). Library: `GIT_checkout.Error.Dirty` and `UntrackedCollision`
  carry the path, and a stash apply names the untracked file in the way.
- **mgit and 1git: a refused stash apply or pop names the file.** `GIT_stash.Error.Dirty`
  carries the path (`local changes to a.txt would be overwritten -- ...`; the first of
  the paths when a merge names several), as the checkout's refusals do.
- `scripts/compare_net_ssh.sh` starts its `sshd` with `-D`, so the script's own trap kills
  it (the daemonizing server outlived every run), and keeps `PerSourcePenalties no` where
  the installed sshd accepts it, as `tests/test_ssh.sh` does.
- Tests: `tests/pty_modes.py` (leftover message, notice memory, the named files),
  `tests/t_modes.m31` (palette rows without a key), `tests/test_checkout.sh` (the file
  in the message).

## 0.26.0

- **mgit: delete and rename a branch** (Branches mode, `docs/MGIT-MODES.md`). `D`
  deletes the branch under the cursor when it is merged (`git branch -d`: merged
  into its upstream when it has one, else into HEAD) and otherwise refuses, saying
  into what it is not merged; `X` force-deletes it (`-D`) after a question that says
  whether it is merged and how to get it back; `e` renames it (`-m`) from a prompt
  that starts with the current name, checks the name by `git check-ref-format`'s
  rules, and replaces an existing branch (`-M`) only after a question. The branch
  you are on, or one checked out in another work tree, is never deleted or
  replaced. Deleting removes the ref (loose and packed), the empty directories, the
  reflog and `branch.<name>.*`; renaming carries the reflog and the configuration
  and moves HEAD with the current branch.
- **mgit: reset and check out a commit** (History mode). `G` resets the current
  branch (or the detached HEAD) to the commit under the cursor: a menu of soft,
  mixed and hard; a hard reset asks first, naming the tracked files whose changes it
  discards and the commits the branch leaves. `o` checks the commit out with a
  detached HEAD (`git checkout --detach`), refusing, and changing nothing, where git
  refuses (local changes to a file the checkout would change, an untracked file in
  the way); the status line shows `detached @ <id>`. All four wait while a merge,
  cherry-pick, revert or rebase is under way and say why.
- **mgit: sign-off** (Commit mode). `s` switches a `Signed-off-by: Name <email>`
  trailer on or off for the commits made from the Commit mode: off by default,
  shown in the panel (with the exact line) and in the hint row, from the committer
  identity (`user.name` and `user.email`), placed as `git commit -s` places it and
  never added twice. `git config mgit.signoff true` makes it start on.
- Library: `GIT_branches.delete_branch`, `rename_branch`, `merge_state`,
  `is_checked_out` and `is_valid_branch_name`, and `GIT_checkout.reset` (soft,
  mixed, hard; `ORIG_HEAD` and git's `reset: moving to` reflog line), so a client
  does not have to run the command line to get git's behaviour. `1git -branch
  --delete` and `--rename` run on them. Deleting the last branch of a directory, or
  the last branch log, no longer removes `refs/heads` or `logs/refs/heads` (git keeps
  them).
- Tests: `tests/pty_modes.py` runs each of the actions beside an identical twin
  repository that the real `git` changes with the matching command, and compares
  refs, reflogs, index, files and configuration; where git refuses, mgit must too.
  `tests/t_modes.m31` checks the table (keys, hint row, palette), the trailer rules
  and the branch-name rules.
- The git-style argument shim of 0.24.0 is **not** removed in this release: it is
  planned for 0.27.0.
- Version 0.26.0.

## 0.25.0

0.24.0 (the Oro command line) was never tagged: its macOS CLI test depended on the repository it ran in. Its content ships here.

- **mgit is five modes, not one screen of every key** (`docs/MGIT-MODES.md`):
  1 Status, 2 Commit, 3 History, 4 Branches, 5 Stash. `Tab` / `Shift-Tab` cycle
  them (a click on the tab bar and `1`-`5` jump), the last row lists only the keys
  of the mode you are in, `?` is that mode's help, and `:` / `Ctrl-P` is a command
  palette of every action of every mode. A merge, cherry-pick, revert or rebase
  under way is named in every mode, its way out leads the bottom row, and what it
  forbids is refused with the reason. One table (`ui/GIT_ui_keymap.m31`) drives the
  bottom row, the help, the palette and the tests.
- Keys keep their letters and live in the mode where they make sense; pressing one
  in another mode says where it moved. Changed on purpose: `Tab` is the mode key,
  so folding is `Space` (`f` for a hunk in a diff); `Esc` goes back to Status (and
  quits from it); `c` goes to the Commit mode, whose `a` discards the draft (`Esc`
  no longer does).
- The screen has no border any more: the tab bar is the first row, the hint row the
  last. The statusline moved under the tab bar.
- Repository discovery honours `GIT_CEILING_DIRECTORIES`, as git does; the CLI test sets it so a `.git` above the temp directory (a macOS runner had one) cannot change what `checkout main` means.
- **Rendering fixes.** A tab, carriage return or escape in a diffed file, a file
  name, a branch name or a commit message reached the terminal raw and moved the
  cursor under the layout, leaving stale cells behind; text is now shown with tabs
  expanded and control characters as their U+2400 symbols, and a last pass over
  every frame removes any that are left. `tests/pty_modes.py` compares incremental
  screens against a full repaint, cell by cell, over wide, emoji, combining-mark,
  tabbed and over-long names at 80x24, 120x40 and 40x12 (it needs `pyte`).
- Version 0.25.0.

## 0.24.0

- **Breaking: 1git and mgit have a command line of their own** (`docs/CLI.md`):
  Oro's args grammar instead of git's argv. One dash is a command, two dashes an
  option, anything else data; several commands share a line and run in order
  (the whole line is validated first, the first failure ends it); `--help` per
  command; `--completions bash|zsh|fish`; exit status 0, 1 (a command failed) or 2
  (the line was not understood, nothing ran). `1git log --oneline -n 5` is
  `1git -log --oneline --max 5`; `-switch`, `-restore` and `-reset` replace
  `switch`/`checkout`/`restore`/`reset`; `stash`, `remote` and `worktree`
  subcommands are `-stash-pop`, `-remote-add`, `-worktree-add`, ...; `ls-remote` is
  `-remote-refs`; `push` takes `--to REMOTE` and Gerrit's `--for BRANCH --topic T`;
  `--force` pushes with a lease and `--overwrite` without; `--no-x` spellings are
  values (`--edit off`, `--renames off`) or named for what they do (`--skip-hooks`).
  New: `-fetch --pull-request N` and `--merge-request N`, `-migrate`.
  The table is `docs/MIGRATING-FROM-GIT.md`.
- Repository, protocol and output compatibility with git is unchanged; argv
  compatibility is no longer a goal (`docs/GIT-COMPAT.md`).
- **Transition: git-style arguments still work in 0.24.0**, rewritten into the new
  grammar with a warning on stderr (`1git: git-style arguments are deprecated; use
  '1git -log --max 5' (see 1git --help)`); a line with an option 1git dropped runs as
  git would. The shim is deleted in 0.27.0.
- mgit: `mgit [PATH] [--mouse on|off] [--help|--version|--completions SHELL]`;
  `--mouse` overrides `M31GIT_MOUSE` and `mgit.mouse`. Exit status 1 when there is no
  repository or no terminal, 2 for a bad command line.
- Needs m31 0.6.0 (`lib/args` with `version`, `completions`, `parse_or_exit`).
- Tests: `tests/test_cli.sh` (`tests/run_cli.sh` alone), `tests/cli_cases.txt` (every
  option, both directions), `tests/pty_cli.py`; the `scripts/compare_*.sh` oracles call
  1git through the table (`scripts/lib_cli.sh`) and compare with git as before.

## 0.23.0

- **The repository is qrazil/m31git** (it was qrazil/gitui); the programs stay `mgit` and `1git`.
  0.21.0 was skipped. Release assets are now `m31git-<os>-<arch>[-musl].tar.gz`
  (same layout) with a `SHA256SUMS` file; `install.sh` takes the new names, still
  finds the `gitui-` assets of releases up to v0.22.0, and verifies the checksum
  when the release has one.
- The entry file is `mgit.m31` (was `gitui.m31`), `tests/test_gitui.sh` is
  `tests/test_mgit.sh`; `deps` names the project `m31git`.
- Environment variables are `M31GIT_*` (was `GITUI_*`): `HTTP_CA_FILE`, `HTTP_USER`,
  `HTTP_PASSWORD`, `SSH_IDENTITY`, `SSH_KNOWN_HOSTS`, `SYNTAX`, `MOUSE`. Git config keys are
  `mgit.syntax`, `mgit.collapsed`, `mgit.mouse` (was `gitui.*`). The old names are
  still read when the new ones are unset. The user agent is `1git/0.23.0`.
- Housekeeping: `__pycache__/` and `*.pyc` are untracked and ignored.

## 0.22.0

- **mgit: side-by-side diff.** `D` in the diff view, the commit view and the stash
  list flips between the unified diff and old | new in two columns, with line
  numbers per side, a change marker in the gutter, a ruler naming each side,
  changed words marked inside paired lines, wrapped or sideways-scrolled long
  lines, collapsed unchanged regions (`e` widens, `E` resets), and syntax colours
  on both sides. Hunk and line staging, unstaging and discarding work from it
  through the same patch code (`h` / `l` pick the side), `j`/`k`/`[`/`]`/`{`/`}`
  as before, the wheel scrolls both sides together, a click picks a row.
  `diff.view = auto|unified|split` (auto: 120 columns or more) is read from git
  config and `D` writes the choice back; below 60 columns the unified view is
  always used. New keys: `D` `h` `l` `e` `E` `w` `<` `>` in the diff view.
- **mgit: mouse reports** are asked for (`M31GIT_MOUSE=off` or `mgit.mouse=off`
  turns them off): the wheel moves the diff, a click picks a row.
- **1git: `diff`, `show`, `log -p` accept `--side-by-side` / `-y`, `--width=N`
  and `--no-side-by-side`** (an m31git extension; git has none). Without the
  flag the output is git's bytes, as before.
- Tests: `tests/test_sbs.sh` (also `bash tests/run_sbs.sh`), `tests/pty_sbs.py`,
  golden layouts in `tests/golden/sbs/`.
