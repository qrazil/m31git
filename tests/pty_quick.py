#!/usr/bin/env python3
"""mgit's commit edit menu (E) and reflog list (L), driven under a real pty against disposable
fixtures, with real `git rebase -i` / `git commit --fixup` / `git reset` as the oracle: the resulting
chains (tree, author, message) must equal git's, fsck --strict is clean, nothing is left in progress.

    python3 tests/pty_quick.py <mgit-binary> <scratch-dir>
"""
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pty_e2e as P  # noqa: E402
import pty_rebase as R  # noqa: E402

check, git, out, write = R.check, R.git, R.out, R.write


def oracle(fx, root, name, *args, seq=None, ed=None):
    """git's twin of fx, after `git rebase <args>` with the todo rewritten by `seq` (python source)."""
    other = R.twin(fx, root, name)
    env = {}
    if seq is not None:
        path = os.path.join(root, name + "_seq.py")
        R.todo_script(path, seq)
        env["GIT_SEQUENCE_EDITOR"] = path
    if ed is not None:
        env["GIT_EDITOR"] = ed
    R.git_rebase(other, *args, **env)
    return other


def open_menu(s, subject):
    s.send("3")
    ok = R.cursor_to(s, subject)
    s.send("E")
    return ok


def main():
    binpath = os.path.abspath(sys.argv[1])
    root = os.path.abspath(sys.argv[2])
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)

    fx = R.build(root, "menu")
    s = P.Session(binpath, fx)
    open_menu(s, "cb")
    t = s.text()
    check("menu: E lists reword, edit, drop, squash, fixup, move, amend, new fixup!", all(w in t for w in ("reword", "edit:", "drop the commit", "squash into", "fixup into", "move the commit up", "move the commit down", "amend the commit", "fixup!")), t)
    s.send("\x1b")
    check("menu: Escape closes it", "squash into" not in s.text(), s.text())
    s.quit()

    # reword
    fx = R.build(root, "reword")
    ed = os.path.join(root, "ed_reword.sh")
    R.script(ed, 'printf "cb, reworded\\n" >"$1"')
    other = oracle(fx, root, "reword_git", "-i", "feature~2", seq="lines[0] = 'reword' + lines[0][4:]", ed=ed)
    s = P.Session(binpath, fx, env=R.ed_env(ed))
    open_menu(s, "cb")
    s.send("r")
    time.sleep(0.8)
    s.drain(1.0)
    check("reword: finished, nothing in progress", "rebase finished" in s.text() and not R.has(fx, "rebase-merge"), s.text())
    R.same(fx, other, "reword: cb reworded", full=True)
    check("reword: fsck clean", R.fsck_clean(fx))
    s.quit()

    # drop (asks first)
    fx = R.build(root, "drop")
    other = oracle(fx, root, "drop_git", "-i", "feature~2", seq="lines[0] = 'drop' + lines[0][4:]")
    before = out(fx, "rev-parse", "HEAD")
    s = P.Session(binpath, fx)
    open_menu(s, "cb")
    s.send("d")
    check("drop: asks first", "drop" in s.text() and "any other key" in s.text(), s.text())
    s.send("n")
    check("drop: n changes nothing", out(fx, "rev-parse", "HEAD") == before, s.text())
    open_menu(s, "cb")
    s.send("d")
    s.send("y")
    R.same(fx, other, "drop: cb dropped")
    check("drop: clean, fsck clean", out(fx, "status", "--short") == "" and R.fsck_clean(fx))
    s.quit()

    # squash / fixup into the commit before
    for key, verb in (("s", "squash"), ("f", "fixup")):
        fx = R.build(root, verb)
        ed = os.path.join(root, "ed_" + verb + ".sh")
        R.script(ed, 'printf "ca+cb\\n" >"$1"')
        other = oracle(fx, root, verb + "_git", "-i", "feature~3", seq="lines[1] = '%s' + lines[1][4:]" % verb, ed=ed)
        s = P.Session(binpath, fx, env=R.ed_env(ed))
        open_menu(s, "cb")
        s.send(key)
        time.sleep(0.8)
        s.drain(1.0)
        check(verb + ": finished", "rebase finished" in s.text() and not R.has(fx, "rebase-merge"), s.text())
        R.same(fx, other, verb + ": cb into ca", full=(verb == "fixup"))
        check(verb + ": fsck clean", R.fsck_clean(fx))
        s.quit()

    # move up and down
    fx = R.build(root, "up")
    other = oracle(fx, root, "up_git", "-i", "feature~2", seq="lines = [lines[1], lines[0]]")
    s = P.Session(binpath, fx)
    open_menu(s, "cb")
    s.send("k")
    R.same(fx, other, "move up: cb and cc swapped")
    s.quit()
    fx = R.build(root, "down")
    other = oracle(fx, root, "down_git", "-i", "feature~3", seq="lines = [lines[1], lines[0], lines[2]]")
    s = P.Session(binpath, fx)
    open_menu(s, "cb")
    s.send("j")
    R.same(fx, other, "move down: cb and ca swapped")
    check("move down: clean, fsck clean", out(fx, "status", "--short") == "" and R.fsck_clean(fx))
    s.quit()
    fx = R.build(root, "up_top")
    before = out(fx, "rev-parse", "HEAD")
    s = P.Session(binpath, fx)
    open_menu(s, "cc")
    s.send("k")
    check("move up: the newest commit says so and nothing changes", out(fx, "rev-parse", "HEAD") == before and "newest" in s.text(), s.text())
    s.quit()

    # edit stops
    fx = R.build(root, "edit")
    s = P.Session(binpath, fx)
    open_menu(s, "cb")
    s.send("e")
    check("edit: stops at cb", R.has(fx, "rebase-merge") and out(fx, "log", "-1", "--format=%s") == "cb" and "to edit" in s.text(), s.text())
    s.send("r")
    s.send("c")
    check("edit: r c finishes", not R.has(fx, "rebase-merge") and out(fx, "log", "-1", "--format=%s") == "cc", s.text())
    s.quit()

    # amend with the staged changes (fixup! + autosquash)
    fx = R.build(root, "amend")
    write(fx, "file_a", "a changed\n")
    git(fx, "add", "file_a")
    write(fx, "k", "unstaged edit\n")
    other = R.twin(fx, root, "amend_git")
    git(other, "commit", "-q", "--fixup", "feature~2")
    seq = os.path.join(root, "amend_seq.sh")
    R.script(seq, "exit 0")
    R.git_rebase(other, "-i", "--autosquash", "--autostash", "feature~4", GIT_SEQUENCE_EDITOR=seq)
    s = P.Session(binpath, fx)
    open_menu(s, "ca")
    s.send("a")
    t = s.text()
    check("amend: finished", "rebase finished" in t and not R.has(fx, "rebase-merge"), t)
    R.same(fx, other, "amend: ca amended with the staged file_a", full=True)
    check("amend: the unstaged edit is back", open(os.path.join(fx, "k")).read() == "unstaged edit\n", out(fx, "status", "--short"))
    check("amend: fsck clean, no stash left", R.fsck_clean(fx) and out(fx, "stash", "list") == "")
    s.quit()

    # new fixup! commit
    fx = R.build(root, "newfixup")
    write(fx, "file_a", "a changed\n")
    git(fx, "add", "file_a")
    other = R.twin(fx, root, "newfixup_git")
    git(other, "commit", "-q", "--fixup", "feature~2")
    s = P.Session(binpath, fx)
    open_menu(s, "ca")
    s.send("F")
    f = lambda d: out(d, "log", "--format=%T|%s")
    check("new fixup!: the same tree and subject as git commit --fixup", f(fx) == f(other), f(fx) + "\n" + f(other))
    s.quit()
    fx = R.build(root, "nofixup")
    before = out(fx, "rev-parse", "HEAD")
    s = P.Session(binpath, fx)
    open_menu(s, "ca")
    s.send("F")
    check("new fixup!: nothing staged is refused", out(fx, "rev-parse", "HEAD") == before and "nothing is staged" in s.text(), s.text())
    s.quit()

    # reflog
    fx = R.build(root, "reflog")
    other = R.twin(fx, root, "reflog_git")
    git(other, "reset", "-q", "--soft", "main")
    s = P.Session(binpath, fx)
    s.send("3")
    s.send("L")
    t = s.text()
    check("reflog: L lists HEAD's reflog, newest first", "reflog of HEAD" in t and "HEAD@{0}" in t and "commit: cc" in t, t)
    s.send("j")
    s.send("\r")
    check("reflog: Enter opens the reset menu for the entry", "reset feature" in s.text() and "soft" in s.text(), s.text())
    s.send("s")
    check("reflog: soft reset to the entry equals git reset --soft main", out(fx, "rev-parse", "HEAD") == out(other, "rev-parse", "HEAD") and out(fx, "status", "--short") == out(other, "status", "--short") and "reflog of HEAD" not in s.text(), s.text())
    s.quit()
    fx = R.build(root, "reflog_o")
    cb = out(fx, "rev-parse", "feature~1")
    s = P.Session(binpath, fx)
    s.send("3")
    s.send("L")
    for _ in range(8):
        s.send("j")
    s.send("o")
    check("reflog: o checks the entry (cb) out detached", out(fx, "rev-parse", "HEAD") == cb and out(fx, "symbolic-ref", "-q", "HEAD") == "", s.text())
    s.quit()

    print("%d passed, %d failed" % (R.passed, R.failures))
    return 1 if R.failures else 0


if __name__ == "__main__":
    sys.exit(main())
