# 0.34.0 under a real pty (`pty_tools.py`): ignore (`I`), the commit hooks and `v`, custom commands
# (`;`), work trees (`W`) and bisect (`t`), each compared with real git (bisect step for step against
# `git bisect`, and git carrying on a bisect mgit started). Sourced from `test.sh`.

if [ ! -x "$WORK/mgit" ]; then
    bash scripts/build.sh -o "$WORK/mgit" >"$WORK/tools_build.log" 2>&1 \
        || bad "tools: scripts/build.sh" "$(cat "$WORK/tools_build.log")"
fi
if [ -x "$WORK/mgit" ] && command -v python3 >/dev/null 2>&1; then
    if tl_out=$(python3 tests/pty_tools.py "$WORK/mgit" "$WORK/pty_tools" 2>&1); then
        note "tools pty: $(echo "$tl_out" | grep -c '^ok') ignore, hook, custom-command, work-tree and bisect checks passed under a real pty"
    else
        bad "tools pty" "$(echo "$tl_out" | grep -v '^ok' | head -30)"
    fi
fi
