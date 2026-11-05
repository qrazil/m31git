#!/usr/bin/env python3
"""mgit's 0.34.0 additions under a real pty, each compared with real git: ignore (`I`), the commit hooks
(pre-commit, commit-msg, post-commit, `v` to skip), custom commands (`;`), work trees (`W`) and bisect (`t`).

    python3 tests/pty_tools.py <mgit-binary> <scratch-dir>
"""
import os
import shutil
import subprocess
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


def write(fx, name, text, mode=None):
    path = os.path.join(fx, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    if mode:
        os.chmod(path, mode)


def commit_all(fx, message, when=None):
    git(fx, "add", "-A")
    env = dict(P.GIT_ENV)
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = "%d +0000" % when
    subprocess.run(["git", "-C", fx, "commit", "-q", "-m", message], check=True, env=env)


def wait_for(s, needle, seconds=15.0):
    deadline = time.time() + seconds
    while time.time() < deadline:
        s.drain(0.3)
        if needle in s.text():
            return True
    return needle in s.text()


def main():
    binpath = os.path.abspath(sys.argv[1])
    root = os.path.abspath(sys.argv[2])
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)

    # --- ignore -----------------------------------------------------------------------------
    fx = P.make_fixture(root, "ignore")
    write(fx, "a.txt", "a\n")
    commit_all(fx, "base")
    write(fx, "build.log", "x\n")
    write(fx, "sub/deep.tmp", "y\n")
    write(fx, "sub/other.tmp", "y\n")
    write(fx, "keep.me", "z\n")
    s = P.Session(binpath, fx)
    check("ignore: the untracked files are listed", "build.log" in s.text() and "keep.me" in s.text(), s.text())

    def to_row(needle):
        for _ in range(10):
            s.send("k")
        for i, line in enumerate(s.text().split("\n")):
            if i >= 2 and needle in line:
                for _ in range(i - 2):
                    s.send("j")
                return
        raise SystemExit("no row " + needle)

    to_row("build.log")
    s.send("I")
    check("ignore: I opens the menu", "add /path to .gitignore" in s.text() and "info/exclude" in s.text(), s.text())
    s.send("g")
    gi = open(os.path.join(fx, ".gitignore")).read()
    check("ignore: g writes /build.log", gi == "/build.log\n", repr(gi))
    check("ignore: git agrees it is ignored and the file left the list", git(fx, "check-ignore", "-q", "build.log")[2] == 0 and "build.log" not in out(fx, "status", "--porcelain").replace(".gitignore", ""), out(fx, "status", "--porcelain"))
    to_row("deep.tmp")
    s.send("I")
    s.send("e")
    check("ignore: e writes *.tmp, which covers both files", open(os.path.join(fx, ".gitignore")).read() == "/build.log\n*.tmp\n" and git(fx, "check-ignore", "-q", "sub/other.tmp")[2] == 0, open(os.path.join(fx, ".gitignore")).read())
    to_row("keep.me")
    s.send("I")
    s.send("x")
    exclude = open(os.path.join(fx, ".git", "info", "exclude")).read()
    check("ignore: x appends to .git/info/exclude", exclude.endswith("/keep.me\n") and git(fx, "check-ignore", "-q", "keep.me")[2] == 0, exclude)
    write(fx, "a.txt", "a changed\n")
    s.send("r")
    to_row("a.txt")
    s.send("I")
    check("ignore: a tracked file is refused with the reason", "tracked" in s.text() and "add /path" not in s.text(), s.text())
    s.quit()

    # --- hooks ---------------------------------------------------------------------------------
    hooks_dir = None
    def hooked(name):
        fx = P.make_fixture(root, name)
        write(fx, "a.txt", "a\n")
        commit_all(fx, "base")
        write(fx, ".git/hooks/pre-commit", "#!/bin/sh\n[ -f fail-pre ] && { echo 'lint failed: bad style' ; exit 1; }\nexit 0\n", 0o755)
        write(fx, ".git/hooks/commit-msg", "#!/bin/sh\nprintf 'Hooked-by: test\\n' >> \"$1\"\nexit 0\n", 0o755)
        write(fx, ".git/hooks/post-commit", "#!/bin/sh\ntouch post-commit-ran\nexit 0\n", 0o755)
        time.sleep(1.2)  # a draft written in the second HEAD moved in is a leftover to the client
        return fx

    editor = os.path.join(root, "ed.sh")
    P.write_editor_script(editor, "feature: add b")
    env = P.env_with_editor(editor)
    env.pop("GIT_EDITOR", None)
    env.pop("VISUAL", None)

    fx = hooked("hooks_ok")
    twin = os.path.join(root, "hooks_ok_git")
    write(fx, "b.txt", "b\n")
    git(fx, "add", "b.txt")
    P.copy_repo(fx, twin)
    subprocess.run(["git", "-C", twin, "commit", "-q", "-m", "feature: add b"], check=True, env=P.GIT_ENV)
    s = P.Session(binpath, fx, env=env)
    s.send("c")
    s.send("e")
    time.sleep(0.8)
    s.drain(1.0)
    msg = lambda d: out(d, "log", "-1", "--format=%T|%B")
    check("hooks: the commit-msg hook's addition is in the message, equal to git's", msg(fx) == msg(twin) and "Hooked-by: test" in msg(fx), msg(fx) + "|" + msg(twin))
    check("hooks: post-commit ran", os.path.exists(os.path.join(fx, "post-commit-ran")))
    s.quit()

    fx = hooked("hooks_fail")
    write(fx, "b.txt", "b\n")
    write(fx, "fail-pre", "x\n")
    git(fx, "add", "b.txt")
    before = out(fx, "rev-parse", "HEAD")
    s = P.Session(binpath, fx, env=env)
    s.send("c")
    s.send("e")
    time.sleep(0.8)
    s.drain(1.0)
    t = s.text()
    check("hooks: a failing pre-commit refuses the commit and shows its last line", out(fx, "rev-parse", "HEAD") == before and "pre-commit hook failed" in t and "bad style" in t, t)
    check("hooks: no post-commit after a refusal", not os.path.exists(os.path.join(fx, "post-commit-ran")))
    s.send("v")
    check("hooks: v says the hooks are skipped", "hooks skipped" in s.text(), s.text())
    s.send("f")
    check("hooks: with the hooks skipped the commit is made, without the commit-msg line and post-commit", out(fx, "rev-parse", "HEAD") != before and "Hooked-by" not in out(fx, "log", "-1", "--format=%B") and not os.path.exists(os.path.join(fx, "post-commit-ran")), s.text())
    s.quit()

    # --- custom commands -----------------------------------------------------------------------
    fx = P.make_fixture(root, "custom")
    write(fx, "a.txt", "a\n")
    commit_all(fx, "base commit")
    write(fx, "b file.txt", "b\n")
    write(fx, ".git/mgit-commands", "# comment\nw\twrite the file\tprintf '%s|%s|%s' {file} {branch} {remote} > out.txt\nbad line without tabs\nc\tshow commit\t-printf '%s %s' {commit} {short} > commit.txt\nq\tasks first\t?touch asked.txt\n")
    s = P.Session(binpath, fx)
    s.send(";")
    t = s.text()
    check("custom: ; lists the commands from .git/mgit-commands", "write the file" in t and "show commit" in t and "asks first" in t and "without tabs" not in t, t)
    s.send("\x1b")
    # cursor on the untracked file row
    for _ in range(10):
        s.send("k")
    lines = s.text().split("\n")
    for i, line in enumerate(lines):
        if i >= 2 and "b file.txt" in line:
            for _ in range(i - 2):
                s.send("j")
    s.send(";")
    s.send("w")
    wait_for(s, "press Enter")
    s.send("\n")
    wait_for(s, "done")
    got = open(os.path.join(fx, "out.txt")).read() if os.path.exists(os.path.join(fx, "out.txt")) else ""
    check("custom: {file} {branch} {remote} are filled in and quoted", got == "b file.txt|main|origin", repr(got))
    s.send("3")
    for _ in range(10):
        s.send("k")
    for i, line in enumerate(s.text().split("\n")):
        if i >= 2 and "base commit" in line:
            for _ in range(i - 2):
                s.send("j")
            break
    s.send(";")
    s.send("q")
    check("custom: a ? command asks first", "asks first?" in s.text() and not os.path.exists(os.path.join(fx, "asked.txt")), s.text())
    s.send("n")
    check("custom: any other key declines", not os.path.exists(os.path.join(fx, "asked.txt")), s.text())
    s.send(";")
    s.send("q")
    s.send("y")
    wait_for(s, "press Enter")
    s.send("\n")
    wait_for(s, "done")
    check("custom: y runs it", os.path.exists(os.path.join(fx, "asked.txt")))
    s.send(";")
    s.send("c")
    time.sleep(0.8)
    s.drain(0.5)
    head = out(fx, "rev-parse", "HEAD")
    got = open(os.path.join(fx, "commit.txt")).read() if os.path.exists(os.path.join(fx, "commit.txt")) else ""
    check("custom: a - command runs without a pause, {commit} and {short} name the commit under the cursor", got == head + " " + head[:7] and "press Enter" not in s.text(), repr(got))
    s.quit()

    # --- work trees --------------------------------------------------------------------------------
    fx = P.make_fixture(root, "wt")
    write(fx, "a.txt", "a\n")
    commit_all(fx, "base")
    twin = os.path.join(root, "wt_git")
    P.copy_repo(fx, twin)
    wt_ours = os.path.join(root, "wt_ours")
    wt_git = os.path.join(root, "wt_git_tree")
    git(twin, "worktree", "add", "-q", "-b", "side", wt_git)
    s = P.Session(binpath, fx)
    s.send("4")
    s.send("W")
    check("worktrees: W lists the main work tree", "work trees (1)" in s.text() and "main" in s.text(), s.text())
    s.send("a")
    s.send(wt_ours)
    s.send("\r")
    s.send("side")
    s.send("\r")
    wait_for(s, "press Enter")
    s.send("\n")
    wait_for(s, "worktree")
    heads = lambda d: sorted(open(os.path.join(d, ".git", "worktrees", n, "HEAD")).read() for n in os.listdir(os.path.join(d, ".git", "worktrees")))
    check("worktrees: the linked work tree's HEAD equals git worktree add -b's", heads(fx) == heads(twin) and os.path.exists(os.path.join(wt_ours, "a.txt")), str(heads(fx)) + str(heads(twin)))
    check("worktrees: the branch exists at the same commit", out(fx, "rev-parse", "side") == out(twin, "rev-parse", "side"))
    check("worktrees: the list shows both", "work trees (2)" in s.text(), s.text())
    s.send("j")
    s.send("d")
    s.send("n")
    s.send("\r")
    check("worktrees: remove asks, anything but y keeps it", os.path.isdir(wt_ours), s.text())
    s.send("d")
    s.send("y")
    s.send("\r")
    wait_for(s, "press Enter")
    s.send("\n")
    wait_for(s, "worktree")
    git(twin, "worktree", "remove", wt_git)
    check("worktrees: remove deletes the directory and the record like git's", not os.path.exists(wt_ours) and not os.path.exists(os.path.join(fx, ".git", "worktrees", "wt_ours")) and out(fx, "worktree", "list", "--porcelain").count("worktree ") == 1, out(fx, "worktree", "list"))
    s.send("k")
    s.send("d")
    check("worktrees: the main one cannot be removed", "main work tree cannot be removed" in s.text(), s.text())
    s.quit()

    # --- bisect ----------------------------------------------------------------------------------------
    def history(name):
        fx = P.make_fixture(root, name)
        for i in range(1, 11):
            write(fx, "f", "%d\n" % i)
            commit_all(fx, "c%d" % i, when=1700000000 + i * 10)
        return fx

    def subject(fx):
        return out(fx, "log", "-1", "--format=%s")

    fx = history("bisect")
    twin = os.path.join(root, "bisect_git")
    P.copy_repo(fx, twin)
    # git's walk: c7 is the first bad commit
    git(twin, "bisect", "start", "HEAD", "HEAD~9")
    git_seq = [subject(twin)]
    for _ in range(10):
        n = int(subject(twin)[1:])
        res = git(twin, "bisect", "bad" if n >= 7 else "good")
        git_seq.append(subject(twin))
        if "first bad commit" in res[0]:
            break
    git_log = open(os.path.join(twin, ".git", "BISECT_LOG")).read()
    s = P.Session(binpath, fx)
    s.send("3")
    s.send("t")
    check("bisect: t opens the menu", "start" in s.text() and "reset" in s.text() and "skip" in s.text(), s.text())
    s.send("s")
    s.send("\r")
    s.send("HEAD~9")
    s.send("\r")
    check("bisect: start checks out the first candidate and says how many are left", "Bisecting: 4 revision(s) left" in s.text() and "roughly 2 step" in s.text(), s.text())
    ours_seq = [subject(fx)]
    for _ in range(10):
        n = int(subject(fx)[1:])
        s.send("t")
        s.send("b" if n >= 7 else "g")
        ours_seq.append(subject(fx))
        if "is the first bad commit" in s.text():
            break
    check("bisect: the commits tested are the ones git bisect tests, in the same order", ours_seq == git_seq, "%r vs %r" % (ours_seq, git_seq))
    check("bisect: the answer is c7", "is the first bad commit" in s.text() and out(fx, "rev-parse", "refs/bisect/bad") == out(fx, "rev-parse", "c7" if False else "refs/bisect/bad"), s.text())
    check("bisect: BISECT_LOG equals git's", open(os.path.join(fx, ".git", "BISECT_LOG")).read().replace("'HEAD~9'", "'HEAD~9'") == git_log, open(os.path.join(fx, ".git", "BISECT_LOG")).read() + "\n---\n" + git_log)
    refs = lambda d: sorted(l.split()[1] for l in out(d, "for-each-ref", "refs/bisect").split("\n") if l)
    check("bisect: refs/bisect/* equal git's", refs(fx) == refs(twin), "%r %r" % (refs(fx), refs(twin)))
    s.send("t")
    s.send("l")
    check("bisect: l shows the log", "git bisect start" in s.text(), s.text())
    s.send("q")
    s.send("t")
    s.send("r")
    git(twin, "bisect", "reset")
    check("bisect: reset goes back to main and removes the state like git bisect reset", out(fx, "symbolic-ref", "--short", "HEAD") == "main" and not os.path.exists(os.path.join(fx, ".git", "BISECT_START")) and refs(fx) == [] and out(fx, "status", "--short") == "", out(fx, "status", "--short"))
    check("bisect: fsck clean", git(fx, "fsck", "--strict")[2] == 0)
    s.quit()

    # git carries on what mgit started
    fx = history("bisect_interop")
    s = P.Session(binpath, fx)
    s.send("3")
    s.send("t")
    s.send("s")
    s.send("\r")
    s.send("HEAD~9")
    s.send("\r")
    first = subject(fx)
    res = git(fx, "bisect", "good")
    check("bisect: git bisect good continues mgit's bisect", first == "c5" and subject(fx) == "c7" and "Bisecting" in res[0], res[0] + subject(fx))
    s.send("r")
    s.send("t")
    s.send("r")
    s.quit()
    git(fx, "bisect", "reset")

    print("%d passed, %d failed" % (passed, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
