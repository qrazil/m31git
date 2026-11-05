# The conformance harness (tests/conformance/run.sh): every case through real
# git and through 1git in identical scratch repositories, stdout, exit status
# and repository state compared. A case that differs and is not listed in
# tests/conformance/known-failures.txt fails here; MISSING cases (git forms with
# no 1git spelling yet) are reported in the count, not failed.
#
# Sourced from `test.sh` (see `test_cli.sh`): no `set`, `cd` or `trap` here.

if build git; then
    conf_out=$(bash tests/conformance/run.sh "$WORK/git" -w "$WORK/conformance" 2>&1)
    conf_rc=$?
    conf_summary=$(printf '%s\n' "$conf_out" | grep '^cases ')
    if [ "$conf_rc" = 0 ]; then
        note "conformance: $conf_summary"
    else
        bad "conformance: a case differs from git" "$conf_summary" "$(printf '%s\n' "$conf_out" | grep '^FAIL' | head -8)"
    fi
    if python3 tests/conformance/gen.py --check; then
        note "conformance: docs/GIT-PARITY.md matches commands.tsv"
    else
        bad "conformance: docs/GIT-PARITY.md is stale (run: python3 tests/conformance/gen.py)"
    fi
fi
