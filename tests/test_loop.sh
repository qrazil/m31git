# The loop mgit runs on (tui's `Loop.run_with`, `ui/GIT_ui_app.m31`): its settings
# and the `--sync` rule at unit level (`t_loop`), then the bytes under a pty
# (`pty_loop.py`): entry and exit, synchronized output asked only where it may be
# and used only after an answer, the editor handoff.
#
# Sourced from `test.sh`: no `set`, `cd` or `trap` here; `$WORK`, `build`, `note`
# and `bad` are `test.sh`'s. Portable shell (BSD tools, bash 3.2).

if build t_loop; then
    loopfx="$WORK/loop_fx"
    mkdir -p "$loopfx"
    loopfx=$(cd "$loopfx" && pwd -P)
    (
        set -e
        cd "$loopfx"
        git init -q -b main .
        git config user.email l@example.com
        git config user.name 'Loop Tester'
        printf 'one\n' >a.txt
        git add -A
        GIT_AUTHOR_DATE='1700000000 +0000' GIT_COMMITTER_DATE='1700000000 +0000' git commit -q -m first
    ) >"$WORK/loop_fx.log" 2>&1 || bad "loop: fixture" "$(tail -5 "$WORK/loop_fx.log")"
    "$WORK/t_loop" "$loopfx/.git" "$loopfx" >"$WORK/loop.out" 2>"$WORK/loop.err"
    if grep -q 'FAIL' "$WORK/loop.out"; then
        bad "loop: unit tests (t_loop)" "$(grep 'FAIL' "$WORK/loop.out")" "$(cat "$WORK/loop.err")"
    elif ! tail -1 "$WORK/loop.out" | grep -q ' 0 failed'; then
        bad "loop: unit tests (t_loop) did not finish" "$(tail -3 "$WORK/loop.out")" "$(cat "$WORK/loop.err")"
    else
        note "loop: unit tests -- $(tail -1 "$WORK/loop.out")"
    fi
fi

if [ ! -x "$WORK/mgit" ]; then
    bash scripts/build.sh -o "$WORK/mgit" >"$WORK/loop_build.log" 2>&1 || bad "loop: scripts/build.sh" "$(tail -5 "$WORK/loop_build.log")"
fi
if [ -x "$WORK/mgit" ] && command -v python3 >/dev/null; then
    if out=$(python3 -I tests/pty_loop.py "$WORK/mgit" "$WORK/ptyloop" 2>&1); then
        note "loop: mgit under a pty -- $(printf '%s\n' "$out" | tail -1)"
    else
        bad "loop: mgit under a pty" "$(printf '%s\n' "$out" | grep -v '^ok' | head -12)"
    fi
fi

# mgit's screens on terminals that measure text differently: after every step each emulated terminal's
# screen equals that terminal's own repaint (names and diffs with text emoji, keycaps, Devanagari,
# halfwidth katakana, Nerd Font and new-emoji glyphs). Skips cleanly when pyte is missing.
if [ -x "$WORK/mgit" ] && command -v python3 >/dev/null; then
    if out=$(python3 tests/pty_variants.py "$WORK/mgit" "$WORK/ptyvariants" 2>&1); then
        note "loop: mgit on differently measuring terminals -- $(printf '%s\n' "$out" | tail -1)"
    else
        bad "loop: mgit on differently measuring terminals" "$(printf '%s\n' "$out" | head -12)"
    fi
fi

# The start-up width probe (tui 0.14.0) end to end through the real binary: an emulator that answers cursor position
# reports (an agreeing terminal, one that draws box characters wide, a mute one), `--width-probe`, `--borders`,
# TUI_WIDTH_PROBE, TUI_BORDERS. Skips cleanly when pyte is missing.
if [ -x "$WORK/mgit" ] && command -v python3 >/dev/null; then
    if out=$(python3 tests/pty_width.py "$WORK/mgit" "$WORK/ptywidth" 2>&1); then
        note "loop: mgit's width probe on a pty -- $(printf '%s\n' "$out" | tail -1)"
    else
        bad "loop: mgit's width probe on a pty" "$(printf '%s\n' "$out" | grep -v '^ok' | head -12)"
    fi
fi
