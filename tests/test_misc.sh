# 0.35.0 under a real pty (`pty_misc.py`): copy to the clipboard (OSC 52 bytes on the wire), clean, notes,
# cherry-picking marked commits, your own keys and the file tree, compared with real git. Sourced from `test.sh`.

if [ ! -x "$WORK/mgit" ]; then
    bash scripts/build.sh -o "$WORK/mgit" >"$WORK/misc_build.log" 2>&1 \
        || bad "misc: scripts/build.sh" "$(cat "$WORK/misc_build.log")"
fi
if [ -x "$WORK/mgit" ] && command -v python3 >/dev/null 2>&1; then
    if mc_out=$(python3 tests/pty_misc.py "$WORK/mgit" "$WORK/pty_misc" 2>&1); then
        note "misc pty: $(echo "$mc_out" | grep -c '^ok') copy, clean, notes, mark, keys and tree checks passed under a real pty"
    else
        bad "misc pty" "$(echo "$mc_out" | grep -v '^ok' | head -30)"
    fi
fi
