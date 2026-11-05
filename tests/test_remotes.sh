# 0.33.0 under a real pty: the local half (`pty_local.py`: squash and no-commit merge, stash of the staged
# changes, set/unset upstream, each beside a twin repository that real git changes) and the network half
# (`pty_remotes.py`: the remotes list, the push and fetch variants, tag push and remote delete, against
# `git http-backend` on localhost). Sourced from `test.sh` (no `set`, no `cd`, no `trap`).

if [ ! -x "$WORK/mgit" ]; then
    bash scripts/build.sh -o "$WORK/mgit" >"$WORK/remotes_build.log" 2>&1 \
        || bad "remotes: scripts/build.sh" "$(cat "$WORK/remotes_build.log")"
fi
if [ -x "$WORK/mgit" ] && command -v python3 >/dev/null 2>&1; then
    if rl_out=$(python3 tests/pty_local.py "$WORK/mgit" "$WORK/pty_local" 2>&1); then
        note "local pty: $(echo "$rl_out" | grep -c '^ok') squash-merge, staged-stash and upstream checks passed under a real pty"
    else
        bad "local pty" "$(echo "$rl_out" | grep -v '^ok' | head -30)"
    fi
    if rr_out=$(python3 tests/pty_remotes.py "$WORK/mgit" "$WORK/pty_remotes" 2>&1); then
        note "remotes pty: $(echo "$rr_out" | grep -c '^ok') remote-management, push, fetch and tag checks passed under a real pty"
    else
        bad "remotes pty" "$(echo "$rr_out" | grep -v '^ok' | head -30)"
    fi
fi
