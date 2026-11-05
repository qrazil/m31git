#!/usr/bin/env python3
"""mgit's local (no network) additions of 0.33.0 under a real pty, each compared with real git on a
twin repository: squash merge and merge --no-commit (`m s`, `m x`), stash of the staged changes only
(`z s`), and set/unset upstream (`b u`, `b U`).

    python3 tests/pty_local.py <mgit-binary> <scratch-dir>
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pty_e2e as P  # noqa: E402

failures = 0
passed = 0


def check(name, condition, detail=""):
    global failures, passed
    if condition:
        passed += 1
        print("ok   " + name)
    else:
        failures += 1
        print("FAIL " + name + ": " + detail)


def git(fx, *args):
    return P.git(fx, *args, env=P.GIT_ENV)


def out(fx, *args):
    return git(fx, *args)[0]


def write(fx, name, text):
    with open(os.path.join(fx, name), "w") as f:
        f.write(text)


def commit_all(fx, message):
    git(fx, "add", "-A")
    git(fx, "commit", "-q", "-m", message)


def state(fx):
    """Everything that should be equal after the same operation."""
    return "\n".join([
        out(fx, "rev-parse", "HEAD"),
        out(fx, "status", "--porcelain=v1"),
        out(fx, "ls-files", "-s"),
        out(fx, "stash", "list", "--format=%gs"),
        "\n".join(l for l in out(fx, "for-each-ref", "--format=%(refname) %(objectname)").split("\n") if "refs/stash" not in l),
        open(os.path.join(fx, ".git", "SQUASH_MSG")).read() if os.path.exists(os.path.join(fx, ".git", "SQUASH_MSG")) else "-",
        "MERGE_HEAD" if os.path.exists(os.path.join(fx, ".git", "MERGE_HEAD")) else "-",
    ])


def build(root, name):
    fx = P.make_fixture(root, name)
    write(fx, "a.txt", "one\ntwo\nthree\n")
    write(fx, "b.txt", "bee\n")
    commit_all(fx, "base")
    git(fx, "checkout", "-q", "-b", "topic")
    write(fx, "c.txt", "see\n")
    commit_all(fx, "topic one")
    write(fx, "a.txt", "one\ntwo changed\nthree\n")
    commit_all(fx, "topic two\n\nwith a body")
    git(fx, "checkout", "-q", "main")
    write(fx, "d.txt", "dee\n")
    commit_all(fx, "main work")
    return fx


def main():
    binpath = os.path.abspath(sys.argv[1])
    root = os.path.abspath(sys.argv[2])
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)

    # --- squash merge ------------------------------------------------------------------
    fx = build(root, "squash")
    other = os.path.join(root, "squash_git")
    P.copy_repo(fx, other)
    git(other, "merge", "--squash", "topic")
    s = P.Session(binpath, fx)
    s.send("4")
    s.send("m")
    t = s.text()
    check("squash: the merge menu offers squash and no-commit", "squash-merge" in t and "stop before the commit" in t, t)
    s.send("s")
    s.send("topic")
    s.send("\r")
    check("squash: the status line says it was squashed", "squashed topic" in s.text(), s.text())
    a, b = state(fx), state(other)
    check("squash: HEAD, index, files, refs and SQUASH_MSG equal git merge --squash's", a == b, a + "\n----\n" + b)
    check("squash: no MERGE_HEAD, fsck clean", "MERGE_HEAD" not in a and git(fx, "fsck", "--strict")[2] == 0)
    s.quit()

    fx = build(root, "nocommit")
    other = os.path.join(root, "nocommit_git")
    P.copy_repo(fx, other)
    git(other, "merge", "--no-commit", "--no-ff", "topic")
    s = P.Session(binpath, fx)
    s.send("4")
    s.send("m")
    s.send("x")
    s.send("topic")
    s.send("\r")
    a, b = state(fx), state(other)
    check("no-commit: the merge stops before the commit, equal to git's", a == b and "MERGE_HEAD" in a, a + "\n----\n" + b)
    s.send("m")
    s.send("c")
    check("no-commit: m c finishes it with a merge commit", out(fx, "rev-list", "--parents", "-1", "HEAD").count(" ") == 2, s.text())
    s.quit()

    # --- stash of the staged changes only -----------------------------------------------
    fx = build(root, "staged")
    write(fx, "a.txt", "one\ntwo\nthree\nfour\n")
    git(fx, "add", "a.txt")
    write(fx, "b.txt", "bee unstaged\n")
    write(fx, "new.txt", "new\n")
    git(fx, "add", "new.txt")
    other = os.path.join(root, "staged_git")
    P.copy_repo(fx, other)
    git(other, "stash", "push", "--staged")
    s = P.Session(binpath, fx)
    s.send("5")
    s.send("z")
    check("stash staged: the menu offers it", "staged" in s.text(), s.text())
    s.send("s")
    a, b = state(fx), state(other)
    check("stash staged: status, index, stash list and refs equal git stash push --staged", a == b, a + "\n----\n" + b)
    check("stash staged: the stash commit's tree and index tree equal git's", out(fx, "rev-parse", "stash@{0}^{tree}", "stash@{0}^2^{tree}") == out(other, "rev-parse", "stash@{0}^{tree}", "stash@{0}^2^{tree}"), out(fx, "rev-parse", "stash@{0}^{tree}"))
    check("stash staged: the unstaged file kept its change, the staged ones are back to HEAD", open(os.path.join(fx, "b.txt")).read() == "bee unstaged\n" and not os.path.exists(os.path.join(fx, "new.txt")) and open(os.path.join(fx, "a.txt")).read() == "one\ntwo\nthree\n")
    s.send("z")
    s.send("a")
    check("stash staged: apply gives the staged file back", open(os.path.join(fx, "a.txt")).read() == "one\ntwo\nthree\nfour\n", s.text())
    s.quit()

    fx = build(root, "staged_none")
    write(fx, "b.txt", "unstaged only\n")
    before = state(fx)
    s = P.Session(binpath, fx)
    s.send("5")
    s.send("z")
    s.send("s")
    check("stash staged: nothing staged is refused and nothing changes", state(fx) == before and "stash --staged" in s.text(), s.text())
    s.quit()

    fx = build(root, "staged_both")
    write(fx, "a.txt", "one\ntwo\nthree\nfour\n")
    git(fx, "add", "a.txt")
    write(fx, "a.txt", "one\ntwo\nthree\nfour\nfive\n")
    before = state(fx)
    s = P.Session(binpath, fx)
    s.send("5")
    s.send("z")
    s.send("s")
    check("stash staged: a file with staged and unstaged changes is refused, nothing changes", state(fx) == before and "unstaged" in s.text(), s.text())
    s.quit()

    # --- upstream ----------------------------------------------------------------------------
    fx = build(root, "upstream")
    bare = os.path.join(root, "up.git")
    subprocess.run(["git", "init", "-q", "--bare", bare], check=True)
    git(fx, "remote", "add", "origin", bare)
    git(fx, "push", "-q", "origin", "main", "topic")
    git(fx, "fetch", "-q", "origin")
    other = os.path.join(root, "upstream_git")
    P.copy_repo(fx, other)
    git(other, "branch", "--set-upstream-to=origin/topic", "main")
    s = P.Session(binpath, fx)
    s.send("4")
    s.send("b")
    check("upstream: the branch menu offers set and unset", "set the current branch" in s.text() and "unset" in s.text(), s.text())
    s.send("u")
    s.send("origin/topic")
    s.send("\r")
    cfg = lambda d: out(d, "config", "--get-regexp", "^branch\\.main\\.")
    check("upstream: b u writes what git branch -u writes", cfg(fx) == cfg(other) and "origin" in cfg(fx), cfg(fx) + "|" + cfg(other))
    s.send("b")
    s.send("u")
    s.send("origin/nosuch")
    s.send("\r")
    check("upstream: a branch that does not exist is refused", "no remote-tracking branch" in s.text() and cfg(fx) == cfg(other), s.text())
    git(other, "branch", "--unset-upstream", "main")
    s.send("b")
    s.send("U")
    check("upstream: b U equals git branch --unset-upstream", cfg(fx) == cfg(other) and cfg(fx) == "", cfg(fx) + "|" + cfg(other))
    s.quit()

    print("%d passed, %d failed" % (passed, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
