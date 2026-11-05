#!/usr/bin/env python3
"""mgit's 0.35.0 additions under a real pty, each compared with real git: copy to the clipboard (OSC 52),
clean, notes, cherry-picking marked commits, your own keys, the file tree.

    python3 tests/pty_misc.py <mgit-binary> <scratch-dir>
"""
import base64
import os
import shutil
import sys
import time

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
    path = os.path.join(fx, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def commit_all(fx, message):
    git(fx, "add", "-A")
    git(fx, "commit", "-q", "-m", message)


def wait_for(s, needle, seconds=15.0):
    deadline = time.time() + seconds
    while time.time() < deadline:
        s.drain(0.3)
        if needle in s.text():
            return True
    return needle in s.text()


def to_row(s, needle):
    for _ in range(14):
        s.send("k")
    for i, line in enumerate(s.text().split("\n")):
        if i >= 2 and needle in line:
            for _ in range(i - 2):
                s.send("j")
            return True
    return False


def main():
    binpath = os.path.abspath(sys.argv[1])
    root = os.path.abspath(sys.argv[2])
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)

    # --- OSC 52 ----------------------------------------------------------------------------
    fx = P.make_fixture(root, "copy")
    write(fx, "a.txt", "a\n")
    commit_all(fx, "first subject line\n\nbody")
    write(fx, "dir/b.txt", "b\n")
    s = P.Session(binpath, fx)
    s.send("3")
    to_row(s, "first subject line")
    head = out(fx, "rev-parse", "HEAD")
    s.send("y")
    check("copy: y opens the copy menu", "the commit's full hash" in s.text() and "file path" in s.text(), s.text())
    raw = s.send("h")
    want = b"\x1b]52;c;" + base64.b64encode(head.encode())
    check("copy: h writes the full hash as OSC 52", want in raw, repr(raw[-200:]))
    check("copy: the message row says what was copied", head in s.text(), s.text())
    s.send("y")
    raw = s.send("m")
    check("copy: m writes the subject", b"\x1b]52;c;" + base64.b64encode(b"first subject line") in raw, repr(raw[-200:]))
    s.send("1")
    to_row(s, "b.txt")
    s.send("y")
    raw = s.send("f")
    check("copy: f writes the path of the file under the cursor", b"\x1b]52;c;" + base64.b64encode(b"dir/b.txt") in raw, repr(raw[-200:]))
    s.quit()
    env = dict(P.CLIENT_ENV)
    env["M31GIT_COPY"] = "off"
    s = P.Session(binpath, fx, env=env)
    s.send("3")
    to_row(s, "first subject line")
    s.send("y")
    raw = s.send("h")
    check("copy: M31GIT_COPY=off writes nothing and says so", b"\x1b]52;" not in raw and "copy is off" in s.text(), s.text())
    s.quit()

    # --- clean -------------------------------------------------------------------------------
    fx = P.make_fixture(root, "clean")
    write(fx, "a.txt", "a\n")
    write(fx, ".gitignore", "*.log\n")
    commit_all(fx, "base")
    write(fx, "junk.txt", "j\n")
    write(fx, "newdir/x.txt", "x\n")
    write(fx, "keep.log", "ignored\n")
    twin = os.path.join(root, "clean_git")
    P.copy_repo(fx, twin)
    git(twin, "clean", "-fd")
    s = P.Session(binpath, fx)
    s.send("K")
    check("clean: K opens the menu", "dry run" in s.text() and "untracked" in s.text(), s.text())
    raw = s.send("n")
    wait_for(s, "press Enter")
    s.send("\n")
    check("clean: the dry run touched nothing", os.path.exists(os.path.join(fx, "junk.txt")) and os.path.exists(os.path.join(fx, "newdir", "x.txt")))
    s.send("K")
    s.send("f")
    s.send("n")
    s.send("\r")
    check("clean: anything but y removes nothing", os.path.exists(os.path.join(fx, "junk.txt")), s.text())
    s.send("K")
    s.send("f")
    s.send("y")
    s.send("\r")
    wait_for(s, "press Enter")
    s.send("\n")
    wait_for(s, "clean")
    check("clean: -f -d equals git clean -fd (the ignored file stays)", out(fx, "status", "--porcelain", "--ignored") == out(twin, "status", "--porcelain", "--ignored") and os.path.exists(os.path.join(fx, "keep.log")), out(fx, "status", "--porcelain", "--ignored"))
    git(twin, "clean", "-fdx")
    s.send("K")
    s.send("x")
    s.send("y")
    s.send("\r")
    wait_for(s, "press Enter")
    s.send("\n")
    wait_for(s, "clean")
    check("clean: -x also removes the ignored file, equal to git clean -fdx", not os.path.exists(os.path.join(fx, "keep.log")) and out(fx, "status", "--porcelain", "--ignored") == out(twin, "status", "--porcelain", "--ignored"))
    s.quit()

    # --- notes ----------------------------------------------------------------------------------
    fx = P.make_fixture(root, "notes")
    write(fx, "a.txt", "a\n")
    commit_all(fx, "one")
    write(fx, "b.txt", "b\n")
    commit_all(fx, "two")
    s = P.Session(binpath, fx)
    s.send("3")
    to_row(s, "two")
    head = out(fx, "rev-parse", "HEAD")
    s.send("O")
    check("notes: O opens the menu", "add / edit" in s.text() and "remove" in s.text(), s.text())
    s.send("a")
    s.send("remember this")
    s.send("\r")
    check("notes: git notes show prints what was typed", out(fx, "notes", "show", head) == "remember this", out(fx, "notes", "show", head))
    check("notes: git log --format=%N has it", out(fx, "log", "-1", "--format=%N").strip() == "remember this", out(fx, "log", "-1", "--format=%N"))
    to_row(s, "two")
    s.send("\r")
    check("notes: the commit, unfolded, shows it", "Notes:  remember this" in s.text(), s.text())
    s.send("\r")
    check("notes: fsck clean", git(fx, "fsck", "--strict")[2] == 0)
    s.send("O")
    s.send("a")
    s.send("\x7f" * 4)
    s.send("that")
    s.send("\r")
    check("notes: editing replaces the text", out(fx, "notes", "show", head) == "remember that", out(fx, "notes", "show", head))
    git(fx, "notes", "add", "-m", "by git", "HEAD~1")
    s.send("g")
    to_row(s, "one")
    s.send("\r")
    check("notes: a note git made shows too", wait_for(s, "by git"), s.text())
    s.send("\r")
    to_row(s, "two")
    s.send("O")
    s.send("d")
    s.send("n")
    s.send("\r")
    check("notes: remove asks, n keeps it", out(fx, "notes", "show", head) == "remember that")
    s.send("O")
    s.send("d")
    s.send("y")
    s.send("\r")
    check("notes: remove with y equals git notes remove", git(fx, "notes", "show", head)[2] != 0 and out(fx, "notes", "list").count("\n") == 0, out(fx, "notes", "list"))
    s.quit()

    # --- marked cherry-pick ---------------------------------------------------------------------
    fx = P.make_fixture(root, "marks")
    write(fx, "a.txt", "a\n")
    commit_all(fx, "base")
    git(fx, "checkout", "-q", "-b", "feature")
    for n in "123":
        write(fx, "f%s.txt" % n, n)
        commit_all(fx, "feat " + n)
    git(fx, "checkout", "-q", "main")
    write(fx, "m.txt", "m")
    commit_all(fx, "main work")
    twin = os.path.join(root, "marks_git")
    P.copy_repo(fx, twin)
    git(twin, "cherry-pick", "feature~2", "feature")
    s = P.Session(binpath, fx)
    s.send("3")
    s.send("f")
    s.send("r")
    s.send("feature")
    s.send("\r")
    to_row(s, "feat 3")
    s.send(".")
    to_row(s, "feat 1")
    s.send(".")
    check("marks: . marks a commit with +", s.text().count("+ ") >= 2 and "2 commit(s) marked" in s.text(), s.text())
    s.send("A")
    check("marks: the cherry-pick menu offers the marked commits", "marked" in s.text(), s.text())
    s.send("m")
    chain = lambda d: out(d, "log", "--format=%T|%s", "-3")
    check("marks: A m cherry-picks feat 1 and feat 3 oldest first, like git cherry-pick", chain(fx) == chain(twin), chain(fx) + "\n" + chain(twin))
    check("marks: the marks are cleared", "+ " not in s.text().split("\n")[3] if len(s.text().split("\n")) > 3 else True)
    s.quit()

    # --- your own keys ----------------------------------------------------------------------------
    fx = P.make_fixture(root, "keys")
    write(fx, "a.txt", "a\n")
    commit_all(fx, "base")
    write(fx, "new.txt", "n\n")
    env = dict(P.CLIENT_ENV)
    env["M31GIT_KEYS"] = "stage=a;unstage=A"
    s = P.Session(binpath, fx, env=env)
    check("keys: the hint row shows the new key", "a stage" in s.text(), s.text().split("\n")[-1])
    to_row(s, "new.txt")
    s.send("a")
    check("keys: the new key stages", "A  new.txt" in out(fx, "status", "--short") or out(fx, "status", "--short") == "A  new.txt", out(fx, "status", "--short"))
    to_row(s, "new.txt")
    s.send("A")
    check("keys: the other new key unstages", out(fx, "status", "--short") == "?? new.txt", out(fx, "status", "--short"))
    to_row(s, "new.txt")
    s.send("s")
    check("keys: the old key no longer stages", out(fx, "status", "--short") == "?? new.txt", out(fx, "status", "--short"))
    s.quit()
    xdg = os.path.join(root, "xdg")
    os.makedirs(os.path.join(xdg, "m31git"))
    with open(os.path.join(xdg, "m31git", "keys"), "w") as f:
        f.write("# my keys\nstage ctrl-x z\n")
    env = dict(P.CLIENT_ENV)
    env["XDG_CONFIG_HOME"] = xdg
    s = P.Session(binpath, fx, env=env)
    to_row(s, "new.txt")
    s.send("z")
    check("keys: the file in XDG_CONFIG_HOME/m31git/keys binds z", out(fx, "status", "--short") == "A  new.txt", out(fx, "status", "--short"))
    s.quit()

    # --- the file tree ------------------------------------------------------------------------------
    fx = P.make_fixture(root, "tree")
    write(fx, "top.txt", "t\n")
    commit_all(fx, "base")
    write(fx, "src/lib/a.txt", "a\n")
    write(fx, "src/lib/b.txt", "b\n")
    write(fx, "src/main.txt", "m\n")
    write(fx, "top.txt", "t2\n")
    s = P.Session(binpath, fx)
    check("tree: the flat list shows full paths", "src/lib/a.txt" in s.text(), s.text())
    s.send("`")
    t = s.text()
    check("tree: the backtick groups by directory with counts", "src/ (3)" in t and "lib/ (2)" in t and "src/lib/a.txt" not in t, t)
    to_row(s, "a.txt")
    s.send("s")
    check("tree: s on a file in the tree stages that file", "A  src/lib/a.txt" in out(fx, "status", "--short").replace("A  src/lib/a.txt", "A  src/lib/a.txt"), out(fx, "status", "--short"))
    s.send("`")
    check("tree: the backtick again is the flat list", "src/lib/b.txt" in s.text(), s.text())
    s.quit()

    print("%d passed, %d failed" % (passed, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
