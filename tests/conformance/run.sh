#!/usr/bin/env bash
# The conformance harness: every case of cases.txt is run through the real
# `git` (the oracle) and through `1git` in two identical scratch repositories,
# and the two are compared:
#
#   stdout (bytes)  exit status (exactly: 1git passes git's numbers through)
#   repository state afterwards: refs, HEAD, index, status, config files,
#   state files (MERGE_HEAD ...), reflog of HEAD, stash list, work tree hashes
#
#   bash tests/conformance/run.sh <1git-binary> [-v] [-k REGEX] [-w DIR] [-o RESULTS] [cases-file]
#
# The 1git line is not written in the cases: `1git -migrate` turns git's own
# argument vector into it, so the grammar under test is the new one and a git
# form with no spelling in 1git is counted as MISSING rather than hidden.
# A case line is  `fixture | setup | git arguments [ @@ stdin ]`  where
# `setup` is a shell snippet run with real git on both sides first (`-` for
# none). A case that fails and is listed in known-failures.txt (same
# `fixture | setup | args` line) is a recorded gap (KNOWN), not a regression;
# stderr is not compared. Ends with the per-command table and the
# totals; the exit status is the number of FAIL cases (MISSING is reported,
# not failed, unless STRICT=1).
#
# bash 3.2 and BSD tools: no mapfile, no associative arrays, no GNU flags.
set -uo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
VERBOSE=0
PATTERN=""
WORK=""
RESULTS=""
BIN=""
CASES="$HERE/cases.txt"
KNOWN="$HERE/known-failures.txt"
while [ $# -gt 0 ]; do
    case "$1" in
        -v) VERBOSE=1 ;;
        -k) shift; PATTERN=$1 ;;
        -w) shift; WORK=$1 ;;
        -o) shift; RESULTS=$1 ;;
        *) if [ -z "$BIN" ]; then BIN=$1; else CASES=$1; fi ;;
    esac
    shift
done
[ -n "$BIN" ] || { echo "usage: run.sh <1git-binary> [-v] [-k REGEX] [-w DIR] [-o RESULTS] [cases]" >&2; exit 2; }
OURS=$(cd "$(dirname "$BIN")" && pwd)/$(basename "$BIN")
[ -n "$WORK" ] || WORK=$(mktemp -d "${TMPDIR:-/tmp}/conf.XXXXXX")
mkdir -p "$WORK"
WORK=$(cd "$WORK" && pwd -P)
[ -n "$RESULTS" ] || RESULTS=$WORK/results.tsv
: > "$RESULTS"

unset VISUAL EDITOR GIT_EDITOR GIT_SEQUENCE_EDITOR GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
export LC_ALL=C TZ=UTC GIT_CONFIG_NOSYSTEM=1 M31GIT_STATE=off GIT_TERMINAL_PROMPT=0
export GIT_AUTHOR_NAME="Ann Author" GIT_AUTHOR_EMAIL="ann@example.com"
export GIT_COMMITTER_NAME="Cy Committer" GIT_COMMITTER_EMAIL="cy@example.com"
export GIT_AUTHOR_DATE="1700100000 +0000" GIT_COMMITTER_DATE="1700100000 +0000"

# shellcheck source=fixtures.sh
. "$HERE/fixtures.sh"

write_global() {
    mkdir -p "$1"
    cat > "$1/gitconfig" <<'G'
[user]
	name = Ann Author
	email = ann@example.com
[init]
	defaultBranch = main
[gc]
	auto = 0
[maintenance]
	auto = false
[core]
	editor = true
G
}

# template repository of a fixture, built once
template() {
    local fx=$1 dir=$WORK/tpl/$1
    if [ ! -d "$dir/repo" ]; then
        mkdir -p "$dir"
        write_global "$dir/home"
        ( export HOME=$dir/home GIT_CONFIG_GLOBAL=$dir/home/gitconfig
          "fixture_$fx" "$dir/repo" > "$dir/build.log" 2>&1 ) || { echo "fixture $fx failed:" >&2; cat "$dir/build.log" >&2; exit 2; }
    fi
}

# prepare <side-dir> <fixture>
prepare() {
    rm -rf "$1"
    mkdir -p "$1"
    write_global "$1/home"
    cp -Rp "$WORK/tpl/$2/repo" "$1/repo"
}

dump() {
    git for-each-ref --format='%(refname) %(objectname) %(symref)' 2>&1
    echo "HEAD: $(git symbolic-ref -q HEAD 2>/dev/null || git rev-parse HEAD 2>&1)"
    git ls-files -s 2>&1
    git status --porcelain=v2 -b --untracked-files=all 2>&1 | grep -v -e '\.sample$' -e '/description$' -e '/info/exclude$' 
    git stash list 2>&1
    git reflog -n 20 HEAD 2>&1
    for f in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD ORIG_HEAD MERGE_MSG; do
        if [ -e ".git/$f" ]; then echo "== $f"; cat ".git/$f"; fi
    done
    echo "== config"; cat .git/config 2>&1
    echo "== global"; cat ../home/gitconfig 2>&1
    # a repository made below the work tree (init sub, clone): its config in full, so a difference shows
    find . -path ./.git -prune -o -name config -type f -path '*/*' -print 2>/dev/null | sort | while IFS= read -r f; do
        echo "== $f"; cat "$f"
    done
    echo "== tree"
    find . -path ./.git -prune -o -type f ! -name '*.sample' ! -name description ! -path '*/info/exclude' -print 2>/dev/null | sort | while IFS= read -r f; do
        printf '%s %s\n' "$(git hash-object -- "$f" 2>/dev/null)" "$f"
    done
}

# run_side <git|ours> <side-dir> <stdin-file> <args...>: stdout, rc, dump go to files
run_side() {
    local who=$1 d=$2 input=$3
    shift 3
    (
        cd "$d/repo" || exit 99
        export HOME=$d/home GIT_CONFIG_GLOBAL=$d/home/gitconfig
        if [ "$who" = git ]; then
            git "$@" < "$input" > "$d/out" 2> "$d/err"
            echo $? > "$d/rc"
        else
            local words=() word
            if ! printf '%s\0' "$@" | "$OURS" -migrate --nul > "$d/tr" 2> "$d/tr.err"; then
                echo MISSING > "$d/rc"
                exit 0
            fi
            while IFS= read -r -d '' word; do words[${#words[@]}]=$word; done < "$d/tr"
            "$OURS" ${words[@]+"${words[@]}"} < "$input" > "$d/out" 2> "$d/err"
            echo $? > "$d/rc"
        fi
        dump > "$d/state" 2>&1
    )
    # paths of the side differ: make them equal
    for f in out state; do
        [ -f "$d/$f" ] && sed "s#$d#@SIDE@#g" "$d/$f" > "$d/$f.n"
    done
}

total=0
fixed=0
while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in ''|'#'*) continue ;; esac
    fx=${line%% | *}
    rest=${line#* | }
    setup=${rest%% | *}
    rest=${rest#* | }
    args=${rest%% @@ *}
    stdin=""
    case "$rest" in *" @@ "*) stdin=${rest#* @@ } ;; esac
    if [ -n "$PATTERN" ] && ! printf '%s\n' "$args" | grep -Eq -- "$PATTERN"; then continue; fi
    template "$fx"
    total=$((total + 1))
    G=$WORK/g
    O=$WORK/o
    prepare "$G" "$fx"
    prepare "$O" "$fx"
    if [ "$setup" != "-" ]; then
        for side in "$G" "$O"; do
            ( cd "$side/repo" && export HOME=$side/home GIT_CONFIG_GLOBAL=$side/home/gitconfig && eval "$setup" ) > "$side/setup.log" 2>&1 || true
        done
    fi
    printf '%b' "$stdin" > "$WORK/stdin"
    [ -n "$stdin" ] || : > "$WORK/stdin"
    eval "set -- $args"
    cmd=$1
    case "$cmd" in -*) cmd="(global option)" ;; esac
    run_side git "$G" "$WORK/stdin" "$@"
    run_side ours "$O" "$WORK/stdin" "$@"
    class=PASS
    why=""
    if [ "$(cat "$O/rc")" = MISSING ]; then
        class=MISSING
    else
        if ! cmp -s "$G/out.n" "$O/out.n"; then class=FAIL; why="stdout"; fi
        if [ "$(cat "$G/rc")" != "$(cat "$O/rc")" ]; then class=FAIL; why="$why exit($(cat "$G/rc") vs $(cat "$O/rc"))"; fi
        if ! cmp -s "$G/state.n" "$O/state.n"; then class=FAIL; why="$why state"; fi
    fi
    # a failure listed in known-failures.txt is a recorded gap, not a regression
    if [ -f "$KNOWN" ] && grep -Fxq -- "$fx | $setup | $args" "$KNOWN"; then
        if [ "$class" = FAIL ]; then class=KNOWN; fi
        if [ "$class" = PASS ]; then echo "NOW PASSES (remove from known-failures.txt): $fx | $setup | $args"; fixed=$((fixed + 1)); fi
    fi
    printf '%s\t%s\t%s | %s\n' "$cmd" "$class" "$fx" "$args" >> "$RESULTS"
    if [ "$class" = FAIL ]; then
        printf 'FAIL %s | %s | %s  [%s]\n' "$fx" "$setup" "$args" "$why"
        # always: the differing lines ('<' git, '>' 1git) of stdout and of the state, and 1git's stderr
        echo "    (< git, > 1git; exit: git $(cat "$G/rc"), 1git $(cat "$O/rc"))"
        diff "$G/out.n" "$O/out.n" | head -20 | sed 's/^/    out: /'
        diff "$G/state.n" "$O/state.n" | head -40 | sed 's/^/    state: /'
        head -3 "$O/err" | sed 's/^/    stderr(1git): /'
    elif [ "$class" = MISSING ] && [ "$VERBOSE" = 1 ]; then
        printf 'MISSING %s | %s  (%s)\n' "$fx" "$args" "$(head -1 "$O/tr.err")"
    fi
done < "$CASES"

echo
echo "per command (pass / cases, missing):"
awk -F'\t' '{ n[$1]++; if ($2=="PASS") p[$1]++; if ($2=="MISSING") m[$1]++; if ($2=="FAIL") f[$1]++; if ($2=="KNOWN") k[$1]++ }
  END { for (c in n) printf "  %-16s %3d / %-3d  fail %-3d missing %d\n", c, p[c]+0, n[c], f[c]+0+k[c], m[c]+0 }' "$RESULTS" | sort
awk -F'\t' '{ n++; if ($2=="PASS") p++; if ($2=="MISSING") m++; if ($2=="FAIL") f++; if ($2=="KNOWN") k2++; c[$1]=1; if ($2=="PASS") cp[$1]=1 }
  END { nc=0; ncp=0; for (k in c) nc++; for (k in cp) ncp++;
        printf "\ncases %d: pass %d, fail %d, known-fail %d, missing %d; commands with a case: %d, with a passing case: %d\n", n, p, f, k2, m, nc, ncp }' "$RESULTS"
fails=$(grep -c "	FAIL	" "$RESULTS" || true)
[ "${STRICT:-0}" = 1 ] && fails=$((fails + $(grep -c "	MISSING	" "$RESULTS" || true)))
[ "${KEEP:-0}" = 1 ] || rm -rf "$WORK/g" "$WORK/o" "$WORK/tpl"
exit "$((fails > 255 ? 255 : fails))"
