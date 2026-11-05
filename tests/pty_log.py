#!/usr/bin/env python3
"""mgit's log menu (f in History): filters by author, message, path and -S, the log of another
revision, the graph column and the diff between refs, driven under a real pty on a disposable
repository, with real `git log` / `git diff` as the oracle (the commits shown must be the ones git lists).

    python3 tests/pty_log.py <mgit-binary> <scratch-dir>
"""
import os
import re
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


def git(fx, *args, author=None, when=None):
    env = dict(P.GIT_ENV)
    if author:
        env["GIT_AUTHOR_NAME"] = author
        env["GIT_AUTHOR_EMAIL"] = author.lower() + "@example.com"
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = "%d +0000" % when
    return P.git(fx, *args, env=env)


def out(fx, *args):
    return git(fx, *args)[0]


def commit(fx, n, path, text, message, author):
    p = os.path.join(fx, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a") as f:
        f.write(text)
    git(fx, "add", "-A")
    git(fx, "commit", "-q", "-m", message, author=author, when=1700000000 + n * 100)


def shown(s):
    """The short ids of the commit rows on the screen, in order."""
    ids = []
    for line in s.text().split("\n"):
        m = re.match(r"^\s*[▸▾]?\s*[|*\\/ ]*([0-9a-f]{7})  ", line)
        if m:
            ids.append(m.group(1))
    return ids


def expect(fx, *args):
    return [x for x in out(fx, "log", "--format=%h", *args).split("\n") if x]


def build(root):
    fx = P.make_fixture(root, "log")
    commit(fx, 1, "a.txt", "alpha\n", "add alpha", "Ann")
    commit(fx, 2, "src/b.txt", "beta needle\n", "add beta with needle", "Bob")
    commit(fx, 3, "a.txt", "more alpha\n", "fix alpha typo", "Ann")
    commit(fx, 4, "src/b.txt", "gamma\n", "extend beta", "Cy")
    git(fx, "checkout", "-q", "-b", "side", "HEAD~2")
    commit(fx, 5, "side.txt", "side\n", "side work", "Bob")
    git(fx, "checkout", "-q", "main")
    git(fx, "merge", "-q", "--no-ff", "-m", "merge side", "side", author="Ann", when=1700000600)
    git(fx, "tag", "v1", "HEAD~1")
    return fx


def menu(s, key, text=None):
    s.send("3")
    s.send("f")
    s.send(key)
    if text is not None:
        s.send(text)
        s.send("\r")


def main():
    binpath = os.path.abspath(sys.argv[1])
    root = os.path.abspath(sys.argv[2])
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)
    fx = build(root)

    s = P.Session(binpath, fx)
    s.send("3")
    s.send("f")
    t = s.text()
    check("menu: f opens the log menu", all(w in t for w in ("author contains", "message contains", "-S:", "graph column", "diff two refs")), t)
    s.send("\x1b")
    check("unfiltered: the commits are git log's", shown(s) == expect(fx), "%r vs %r" % (shown(s), expect(fx)))

    menu(s, "a", "Ann")
    check("author: Ann", shown(s) == expect(fx, "-F", "--author=Ann"), "%r vs %r" % (shown(s), expect(fx, "-F", "--author=Ann")))
    check("author: the heading names the filter", "author=Ann" in s.text(), s.text())
    menu(s, "c")
    check("clear: back to everything", shown(s) == expect(fx), "%r" % shown(s))

    menu(s, "g", "alpha")
    check("message: alpha", shown(s) == expect(fx, "-F", "--grep=alpha"), "%r vs %r" % (shown(s), expect(fx, "-F", "--grep=alpha")))
    menu(s, "c")

    menu(s, "s", "needle")
    check("-S: needle", shown(s) == expect(fx, "-Sneedle", "--first-parent") or shown(s) == expect(fx, "-Sneedle"), "%r vs %r" % (shown(s), expect(fx, "-Sneedle")))
    menu(s, "c")

    menu(s, "p", "src")
    exp = expect(fx, "--first-parent", "--", "src")
    check("path: src (commits whose first-parent diff touches it)", shown(s) == exp, "%r vs %r" % (shown(s), exp))
    menu(s, "c")

    menu(s, "p", "a.txt")
    menu(s, "a", "Ann")
    exp = expect(fx, "-F", "--author=Ann", "--first-parent", "--", "a.txt")
    check("path and author together", shown(s) == exp, "%r vs %r" % (shown(s), exp))
    menu(s, "c")

    menu(s, "r", "side")
    check("revision: the log of side", shown(s) == expect(fx, "side"), "%r vs %r" % (shown(s), expect(fx, "side")))
    check("revision: the heading names it", "side" in s.text().split("\n")[3], s.text())
    menu(s, "r", "nosuchrev")
    check("revision: a bad name is refused and the log stays", shown(s) == expect(fx, "side"), s.text())
    menu(s, "c")
    check("clear: back to HEAD", shown(s) == expect(fx), "%r" % shown(s))
    menu(s, "r", "v1")
    check("revision: a tag", shown(s) == expect(fx, "v1"), "%r vs %r" % (shown(s), expect(fx, "v1")))
    menu(s, "c")

    # graph
    s.send("3")
    s.send("f")
    s.send("G")
    t = s.text()
    rows = [ln for ln in t.split("\n") if re.search(r"[0-9a-f]{7}  ", ln)]
    check("graph: every commit row has a graph marker", len(rows) == len(expect(fx)) and all("*" in r.split("  ")[0] or "*" in r[:14] for r in rows), t)
    check("graph: the merge's side branch shows a second lane", any("|" in r[:14] for r in rows), t)
    check("graph: the ids still equal git's", shown(s) == expect(fx), "%r" % shown(s))
    s.send("f")
    s.send("G")
    check("graph: off again", not any("*" in ln[:12] for ln in s.text().split("\n")[3:8]), s.text())

    # diff between refs
    s.send("f")
    s.send("d")
    s.send("v1..HEAD")
    s.send("\r")
    t = s.text()
    stat = out(fx, "diff", "--numstat", "v1", "HEAD").split("\n")
    names = [x.split("\t")[2] for x in stat if x]
    check("diff refs: every changed file is listed", all(("--- " + n) in t for n in names) and len(names) > 0, t + "\n" + str(names))
    added = sum(int(x.split("\t")[0]) for x in stat if x)
    removed = sum(int(x.split("\t")[1]) for x in stat if x)
    check("diff refs: the totals equal git diff --numstat", ("%d file(s) changed, +%d -%d" % (len(names), added, removed)) in t, t)
    s.send("q")
    s.send("f")
    s.send("d")
    s.send("nosuch..HEAD")
    s.send("\r")
    check("diff refs: a bad ref is a message", "diff:" in s.text() and "nosuch" in s.text(), s.text())
    s.send("f")
    s.send("d")
    s.send("main~3...side")
    s.send("\r")
    stat = out(fx, "diff", "--numstat", "main~3...side").split("\n")
    names = [x.split("\t")[2] for x in stat if x]
    check("diff refs: A...B uses the merge base", all(("--- " + n) in s.text() for n in names) and len(names) > 0, s.text())
    s.send("q")
    s.quit()

    print("%d passed, %d failed" % (passed, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
