# The History mode's log menu (`f`) under a real pty (`pty_log.py`): filters by author, message,
# path and -S, the log of another revision or tag, the graph column and the diff between refs,
# the commits shown compared with `git log`'s. Fixtures under `$WORK/pty_log`.
# Sourced from `test.sh` (no `set`, no `cd`, no `trap`).

if [ ! -x "$WORK/mgit" ]; then
    bash scripts/build.sh -o "$WORK/mgit" >"$WORK/log_build.log" 2>&1 \
        || bad "log menu: scripts/build.sh" "$(cat "$WORK/log_build.log")"
fi
if [ -x "$WORK/mgit" ] && command -v python3 >/dev/null 2>&1; then
    if lg_out=$(python3 tests/pty_log.py "$WORK/mgit" "$WORK/pty_log" 2>&1); then
        note "log menu pty: $(echo "$lg_out" | grep -c '^ok') filter, graph and ref-diff checks passed under a real pty"
    else
        bad "log menu pty" "$lg_out"
    fi
fi
