# The index writer against real `git`, in twin repositories: the same starting
# repository (a byte copy, so every stat field starts equal) gets the same
# operation from real git and from this program, and the two are compared
# entry by entry (the bytes, `ls-files --stage --debug`, `status --porcelain`,
# `fsck`). Also what the writer does when `index.lock` is there or git writes
# the index while it works, and what it keeps and drops of an index git wrote.
#
# Sourced from `test.sh` (see `test_write.sh`'s header: no `set`, no `cd`, no
# `trap`; `WORK`, `build`, `note` and `bad` are `test.sh`'s). Runs on bash 3.2
# and BSD tools; every path is absolute and `GIT_CEILING_DIRECTORIES` is set, as
# a program built with an m31 runtime that has no `getcwd` needs.

iw="$WORK/index_write"
mkdir -p "$iw"
iw=$(cd "$iw" && pwd -P)
iw_raw=20
[ "$TEST_HASH" = sha256 ] && iw_raw=32
iw_entries() { python3 -I tests/oracles/index_entries.py "$1/.git/index" "$iw_raw"; }
# the entries and the header only: git keeps a cache-tree and the like that this drops
iw_only_entries() { iw_entries "$1" | grep -v '^extension'; }
iw_git() { GIT_CEILING_DIRECTORIES="$iw" git "$@"; }

# a repository with a committed a.txt, a b.txt and an executable x.sh
iw_make() {
    local dir=$1
    mkdir -p "$dir"
    (
        set -e
        cd "$dir"
        iw_git init -q -b main .
        iw_git config user.email i@example.com
        iw_git config user.name 'Index Writer'
        iw_git config gc.auto 0
        printf 'one\ntwo\n' >a.txt
        printf 'bee\n' >b.txt
        printf '#!/bin/sh\n' >x.sh
        chmod 755 x.sh
        iw_git add -A
        GIT_AUTHOR_DATE='1700000000 +0000' GIT_COMMITTER_DATE='1700000000 +0000' iw_git commit -q -m first
    ) >"$iw/make.log" 2>&1 || bad "index writer: fixture $dir" "$(tail -5 "$iw/make.log")"
}

if build t_index_write; then
    iw_make "$iw/base"

    # --- 1. an entry for a blob nobody stat'ed: git's own bytes -----------------
    # `git update-index --cacheinfo` is what staging a blob without a file is, and the
    # entry mgit writes must be the one it writes: size 0. A size of -1 was written as
    # 4294967295, which git trusts without reading the file: `status` said MM.
    cp -R "$iw/base" "$iw/ci_git"
    cp -R "$iw/base" "$iw/ci_us"
    printf 'one\nTWO\n' >"$iw/ci_git/a.txt"
    cp "$iw/ci_git/a.txt" "$iw/ci_us/a.txt"
    printf 'brand new\n' >"$iw/ci_git/new.txt"
    cp "$iw/ci_git/new.txt" "$iw/ci_us/new.txt"
    iw_blob_a=$(iw_git -C "$iw/ci_git" hash-object -w a.txt)
    iw_blob_n=$(iw_git -C "$iw/ci_git" hash-object -w new.txt)
    iw_git -C "$iw/ci_us" hash-object -w a.txt >/dev/null
    iw_git -C "$iw/ci_us" hash-object -w new.txt >/dev/null
    iw_git -C "$iw/ci_git" update-index --cacheinfo "100644,$iw_blob_a,a.txt"
    iw_git -C "$iw/ci_git" update-index --add --cacheinfo "100644,$iw_blob_n,new.txt"
    iw_out1=$("$WORK/t_index_write" set "$iw/ci_us/.git" 100644 "$iw_blob_a" a.txt 2>&1)
    iw_out2=$("$WORK/t_index_write" set "$iw/ci_us/.git" 100644 "$iw_blob_n" new.txt 2>&1)
    iw_only_entries "$iw/ci_git" >"$iw/ci_git.entries"
    iw_only_entries "$iw/ci_us" >"$iw/ci_us.entries"
    iw_git -C "$iw/ci_git" ls-files --stage --debug >"$iw/ci_git.debug"
    iw_git -C "$iw/ci_us" ls-files --stage --debug >"$iw/ci_us.debug"
    if [ "$iw_out1 $iw_out2" = "ok ok" ] && cmp -s "$iw/ci_git.entries" "$iw/ci_us.entries" \
        && cmp -s "$iw/ci_git.debug" "$iw/ci_us.debug"; then
        note "index writer: a staged blob's entries equal git update-index --cacheinfo's, byte for byte"
    else
        bad "index writer: entries after staging a blob" "$iw_out1 / $iw_out2" \
            "$(diff "$iw/ci_git.entries" "$iw/ci_us.entries" | head -6)" "$(diff "$iw/ci_git.debug" "$iw/ci_us.debug" | head -8)"
    fi
    iw_st_git=$(iw_git -C "$iw/ci_git" status --porcelain)
    iw_st_us=$(iw_git -C "$iw/ci_us" status --porcelain)
    iw_fsck=$(iw_git -C "$iw/ci_us" fsck --strict 2>&1)
    if [ "$iw_st_git" = "$iw_st_us" ] && [ "$iw_st_us" = "$(printf 'M  a.txt\nA  new.txt')" ] && [ -z "$iw_fsck" ]; then
        note "index writer: git status agrees with git's own entry (M, A, not MM or AM) and fsck --strict is clean"
    else
        bad "index writer: status after staging a blob" "git: $iw_st_git" "ours: $iw_st_us" "fsck: $iw_fsck"
    fi

    # --- 2. index.lock: created exclusively, never clobbered ---------------------
    cp -R "$iw/base" "$iw/lock"
    cp "$iw/lock/.git/index" "$iw/lock.index.before"
    printf 'another process\n' >"$iw/lock/.git/index.lock"
    iw_out=$("$WORK/t_index_write" rewrite "$iw/lock/.git" 2>&1); iw_rc=$?
    iw_git_out=$(iw_git -C "$iw/lock" update-index --add --cacheinfo "100644,$(printf x | iw_git -C "$iw/lock" hash-object --stdin),y" 2>&1); iw_git_rc=$?
    if [ "$iw_rc" = 1 ] && printf '%s' "$iw_out" | grep -q 'index.lock exists' \
        && [ "$iw_git_rc" != 0 ] && cmp -s "$iw/lock.index.before" "$iw/lock/.git/index" \
        && [ "$(cat "$iw/lock/.git/index.lock")" = "another process" ]; then
        note "index writer: an index.lock that is there is refused (git refuses it too), the lock and the index are untouched"
    else
        bad "index writer: existing index.lock" "rc=$iw_rc out=$iw_out" "git rc=$iw_git_rc: $iw_git_out"
    fi
    rm -f "$iw/lock/.git/index.lock"
    ln -s nowhere "$iw/lock/.git/index.lock"
    iw_out=$("$WORK/t_index_write" rewrite "$iw/lock/.git" 2>&1); iw_rc=$?
    if [ "$iw_rc" = 1 ] && printf '%s' "$iw_out" | grep -q 'index.lock exists' && [ -h "$iw/lock/.git/index.lock" ]; then
        note "index writer: a dangling symlink at index.lock counts as a lock too"
    else
        bad "index writer: dangling index.lock" "rc=$iw_rc out=$iw_out"
    fi
    rm -f "$iw/lock/.git/index.lock"
    iw_out=$("$WORK/t_index_write" rewrite "$iw/lock/.git" 2>&1); iw_rc=$?
    iw_left=$(ls -a "$iw/lock/.git" | grep 'index\.lock' || true)
    if [ "$iw_rc" = 0 ] && [ -z "$iw_left" ] && [ -z "$(iw_git -C "$iw/lock" status --porcelain)" ] && [ -z "$(iw_git -C "$iw/lock" fsck --strict 2>&1)" ]; then
        note "index writer: with no lock the write goes through and leaves no index.lock or temporary file behind"
    else
        bad "index writer: write after the lock is gone" "rc=$iw_rc out=$iw_out" "left: $iw_left"
    fi

    # --- 3. git writes the index while this works: its change is not overwritten ---
    cp -R "$iw/base" "$iw/race"
    printf 'late\n' >"$iw/race/late.txt"
    printf 'mine\n' >"$iw/race/mine.txt"
    iw_blob_l=$(iw_git -C "$iw/race" hash-object -w late.txt)
    iw_blob_m=$(iw_git -C "$iw/race" hash-object -w mine.txt)
    rm -f "$iw/race.fifo"
    mkfifo "$iw/race.fifo"
    "$WORK/t_index_write" set-after "$iw/race/.git" 100644 "$iw_blob_m" mine.txt <"$iw/race.fifo" >"$iw/race.out" 2>&1 &
    iw_pid=$!
    exec 7>"$iw/race.fifo"
    iw_wait=0
    while ! grep -q '^read' "$iw/race.out" 2>/dev/null && [ "$iw_wait" -lt 200 ]; do
        sleep 0.1 2>/dev/null || sleep 1
        iw_wait=$((iw_wait + 1))
    done
    iw_git -C "$iw/race" update-index --add --cacheinfo "100644,$iw_blob_l,late.txt"
    exec 7>&-
    wait "$iw_pid"; iw_rc=$?
    iw_listed=$(iw_git -C "$iw/race" ls-files | tr '\n' ' ')
    if [ "$iw_rc" = 1 ] && grep -q 'changed by another process' "$iw/race.out" \
        && [ "$iw_listed" = "a.txt b.txt late.txt x.sh " ] && [ ! -e "$iw/race/.git/index.lock" ]; then
        note "index writer: an index git wrote after the read is not overwritten (changed since read), no lock left"
    else
        bad "index writer: concurrent git write" "rc=$iw_rc: $(cat "$iw/race.out")" "ls-files: $iw_listed"
    fi
    rm -f "$iw/race.fifo"

    # --- 4. what a round trip keeps: every entry byte, extended flags included ---
    iw_make "$iw/ext"
    (
        cd "$iw/ext"
        printf 'intent\n' >ita.txt
        iw_git add -N ita.txt
        iw_git update-index --skip-worktree b.txt
        iw_git update-index --assume-unchanged x.sh
        ln -s a.txt link.txt
        iw_git add link.txt
    ) >"$iw/ext.log" 2>&1 || bad "index writer: extended-flags fixture" "$(tail -3 "$iw/ext.log")"
    iw_entries "$iw/ext" >"$iw/ext.before"
    iw_git -C "$iw/ext" ls-files -v >"$iw/ext.t.before"
    iw_git -C "$iw/ext" status --porcelain >"$iw/ext.st.before"
    iw_out=$("$WORK/t_index_write" rewrite "$iw/ext/.git" 2>&1)
    iw_entries "$iw/ext" >"$iw/ext.after"
    iw_git -C "$iw/ext" ls-files -v >"$iw/ext.t.after"
    iw_git -C "$iw/ext" status --porcelain >"$iw/ext.st.after"
    if [ "$iw_out" = ok ] && head -1 "$iw/ext.before" | grep -q '^version 3 ' \
        && grep -v '^extension' "$iw/ext.before" | cmp -s - "$iw/ext.after" \
        && cmp -s "$iw/ext.t.before" "$iw/ext.t.after" && cmp -s "$iw/ext.st.before" "$iw/ext.st.after" \
        && grep -q '^S b.txt' "$iw/ext.t.after" && grep -q '^h x.sh' "$iw/ext.t.after" \
        && grep -q ' A ita.txt\|^.A ita.txt' "$iw/ext.st.after"; then
        note "index writer: intent-to-add, skip-worktree and assume-unchanged entries survive a rewrite byte for byte (version 3)"
    else
        bad "index writer: extended flags" "$iw_out" "$(diff "$iw/ext.before" "$iw/ext.after" | head -6)" \
            "$(diff "$iw/ext.t.before" "$iw/ext.t.after" | head)" "$(diff "$iw/ext.st.before" "$iw/ext.st.after")"
    fi
    iw_git -C "$iw/ext" add ita.txt
    if [ "$(iw_git -C "$iw/ext" status --porcelain | grep ita.txt)" = "A  ita.txt" ]; then
        note "index writer: git continues the rewritten index (add on the intent-to-add path)"
    else
        bad "index writer: git add after a rewrite" "$(iw_git -C "$iw/ext" status --porcelain)"
    fi
    iw_make "$iw/plain"
    iw_entries "$iw/plain" >"$iw/plain.before"
    "$WORK/t_index_write" rewrite "$iw/plain/.git" >/dev/null 2>&1
    iw_entries "$iw/plain" >"$iw/plain.after"
    if head -1 "$iw/plain.after" | grep -q '^version 2 ' && grep -v '^extension' "$iw/plain.before" | cmp -s - "$iw/plain.after"; then
        note "index writer: an index with no extended flag is still written as version 2, entries byte for byte"
    else
        bad "index writer: version 2 round trip" "$(diff "$iw/plain.before" "$iw/plain.after" | head -6)"
    fi

    # --- 5. extensions: dropped (cache-tree, resolve-undo, untracked cache), nothing else changes ---
    iw_make "$iw/reuc"
    (
        cd "$iw/reuc"
        iw_git checkout -q -b side
        printf 'side\n' >a.txt
        iw_git commit -q -am side
        iw_git checkout -q main
        printf 'main\n' >a.txt
        iw_git commit -q -am main
        iw_git merge side >/dev/null 2>&1 || true
        printf 'resolved\n' >a.txt
        iw_git add a.txt
        iw_git config core.untrackedCache true
        iw_git update-index --untracked-cache >/dev/null 2>&1 || true
        iw_git status >/dev/null 2>&1
    ) >"$iw/reuc.log" 2>&1
    iw_entries "$iw/reuc" >"$iw/reuc.before"
    iw_tree_before=$(iw_git -C "$iw/reuc" write-tree)
    iw_st_before=$(iw_git -C "$iw/reuc" status --porcelain)
    iw_out=$("$WORK/t_index_write" rewrite "$iw/reuc/.git" 2>&1)
    iw_entries "$iw/reuc" >"$iw/reuc.after"
    iw_tree_after=$(iw_git -C "$iw/reuc" write-tree)
    iw_st_after=$(iw_git -C "$iw/reuc" status --porcelain)
    iw_fsck=$(iw_git -C "$iw/reuc" fsck --strict --no-dangling 2>&1)
    if [ "$iw_out" = ok ] && grep -q '^extension REUC' "$iw/reuc.before" && grep -q '^extension TREE' "$iw/reuc.before" \
        && ! grep -q '^extension' "$iw/reuc.after" \
        && grep -v '^extension' "$iw/reuc.before" | cmp -s - "$iw/reuc.after" \
        && [ "$iw_tree_before" = "$iw_tree_after" ] && [ "$iw_st_before" = "$iw_st_after" ] \
        && [ -z "$iw_fsck" ] && [ -z "$(iw_git -C "$iw/reuc" ls-files --resolve-undo)" ]; then
        note "index writer: TREE, REUC and the like are dropped (documented), entries, write-tree, status and fsck are unchanged"
    else
        bad "index writer: extensions" "$iw_out" "before: $(grep '^extension' "$iw/reuc.before" | tr '\n' ' ')" \
            "after: $(grep '^extension' "$iw/reuc.after" | tr '\n' ' ')" "trees $iw_tree_before $iw_tree_after" "status $iw_st_before / $iw_st_after" "fsck $iw_fsck"
    fi

    # --- 6. a split index is refused, never half read and half overwritten ---------
    iw_make "$iw/split"
    (
        cd "$iw/split"
        iw_git config core.splitIndex true
        iw_git update-index --split-index
        printf 'more\n' >c.txt
        iw_git add c.txt
    ) >"$iw/split.log" 2>&1
    if grep -q '^extension link' <(iw_entries "$iw/split"); then
        cp "$iw/split/.git/index" "$iw/split.index.before"
        iw_out=$("$WORK/t_index_write" rewrite "$iw/split/.git" 2>&1); iw_rc=$?
        iw_status=$(iw_git -C "$iw/split" status --porcelain)
        if [ "$iw_rc" = 1 ] && printf '%s' "$iw_out" | grep -q 'split or sparse' \
            && cmp -s "$iw/split.index.before" "$iw/split/.git/index" && [ "$iw_status" = "A  c.txt" ]; then
            note "index writer: a split index (link extension) is refused with a message and left as it was"
        else
            bad "index writer: split index" "rc=$iw_rc out=$iw_out" "status: $iw_status"
        fi
    else
        bad "index writer: split index fixture has no link extension" "$(cat "$iw/split.log")"
    fi

    # --- 7. 1git add under a lock ---------------------------------------------------
    if [ -x "$WORK/1git" ] || bash scripts/build.sh git.m31 -o "$WORK/1git" >"$WORK/iw_1git_build.log" 2>&1; then
        iw_make "$iw/cli"
        printf 'staged by 1git\n' >"$iw/cli/f.txt"
        printf 'held\n' >"$iw/cli/.git/index.lock"
        iw_err=$(cd "$iw/cli" && PWD="$iw/cli" GIT_CEILING_DIRECTORIES="$iw" "$WORK/1git" -add f.txt 2>&1 >/dev/null); iw_rc=$?
        if [ "$iw_rc" != 0 ] && printf '%s' "$iw_err" | grep -q 'index.lock' && [ "$(cat "$iw/cli/.git/index.lock")" = held ] \
            && [ "$(iw_git -C "$iw/cli" status --porcelain)" = "?? f.txt" ]; then
            note "1git add: refused while index.lock exists, the lock is not touched and nothing is staged"
        else
            bad "1git add under a lock" "rc=$iw_rc: $iw_err"
        fi
        rm -f "$iw/cli/.git/index.lock"
        (cd "$iw/cli" && PWD="$iw/cli" GIT_CEILING_DIRECTORIES="$iw" "$WORK/1git" -add f.txt >/dev/null 2>&1)
        if [ "$(iw_git -C "$iw/cli" status --porcelain)" = "A  f.txt" ] && [ -z "$(ls -a "$iw/cli/.git" | grep 'index\.lock')" ]; then
            note "1git add: staged once the lock is gone, and git agrees"
        else
            bad "1git add after the lock" "$(iw_git -C "$iw/cli" status --porcelain)"
        fi
    else
        bad "index writer: build 1git" "$(tail -3 "$WORK/iw_1git_build.log")"
    fi
fi
