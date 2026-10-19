#!/usr/bin/env bash
# Only the index writer checks (`test_index_write.sh`), without the rest of `test.sh`:
#
#   M31_ROOT=/path/to/m31 LANGC=/path/to/m31c bash tests/run_index_write.sh
#
# `IW_1GIT` names a 1git you already built, to skip building it.
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
unset VISUAL GIT_EDITOR EDITOR GIT_SEQUENCE_EDITOR
export LC_ALL=C TZ=UTC
TEST_HASH=${TEST_HASH:-sha1}
export GIT_DEFAULT_HASH=$TEST_HASH
# mgit remembers nothing between sessions in a test run (ui/GIT_ui_state.m31)
export M31GIT_STATE=off
if [ -z "${M31_ROOT:-}" ] || [ ! -f "$M31_ROOT/config.sh" ]; then
    echo "M31_ROOT is not set to an m31 release or checkout" >&2
    exit 1
fi
. "$M31_ROOT/runtime/arch.sh"
LANGC=${LANGC:-./m31c}
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
pass=0
fail=0
note() { printf '\033[32mok\033[0m   %s\n' "$1"; pass=$((pass + 1)); }
bad()  { printf '\033[31mFAIL\033[0m %s\n' "$1"; shift; printf '%s\n' "$@" | sed 's/^/     /'; fail=$((fail + 1)); }
build() {
    local name=$1
    local src="tests/$name.m31"
    [ -f "$src" ] || src="$name.m31"
    if ! "$LANGC" -emit-c "$src" --out "$WORK/$name.c" 2>"$WORK/$name.diag"; then
        bad "compile $name" "$(grep -v '^warning' "$WORK/$name.diag" | head -5)"
        return 1
    fi
    if ! cc -O2 -w -I "$M31_ROOT/runtime" -pthread -o "$WORK/$name" "$WORK/$name.c" \
           "$M31_ROOT/runtime/rt.c" "$M31_ROOT/runtime/scheduler.c" "$M31_ROOT/$RT_REACTOR_C" "$M31_ROOT/$RT_CTX_ASM" \
           2>"$WORK/$name.cc"; then
        bad "cc $name" "$(head -5 "$WORK/$name.cc")"
        return 1
    fi
    return 0
}
[ -n "${IW_1GIT:-}" ] && cp "$IW_1GIT" "$WORK/1git"
source tests/test_index_write.sh
echo "$pass passed, $fail failed"
[ "$fail" = 0 ]
