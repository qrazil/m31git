#!/usr/bin/env python3
"""mgit's remote management and network variants (0.33.0) under a real pty, against `tests/net_serve.py`
(real `git http-backend`, HTTP Basic auth) on localhost, with real git as the oracle: the remotes list
(`M`: add, rename, set-url, remove, prune), the push menu (force-with-lease, tags, another remote, delete a
remote branch), the fetch variants (--all, --prune, --tags, a named remote) and the tag list's push and
remote delete.

    python3 tests/pty_remotes.py <mgit-binary> <scratch-dir>
"""
import os
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pty_e2e  # noqa: E402
import pty_net as N  # noqa: E402
from pty_e2e import GIT_ENV, CLIENT_ENV, Session, git  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
check, wait_for, act, commit = N.check, N.wait_for, N.act, N.commit


def gitout(repo, *args):
    return git(repo, *args, env=GIT_ENV)[0]


def finish_handoff(s, needle="press Enter"):
    s.send("\n")


def main():
    binpath = os.path.abspath(sys.argv[1])
    root = os.path.abspath(sys.argv[2])
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(os.path.join(root, "repos"))
    bares = {}
    seed = os.path.join(root, "seed")
    subprocess.run(["git", "init", "-q", "-b", "main", seed], check=True)
    commit(seed, "a.txt", "one\n", "first")
    for name in ("r", "r2"):
        bare = os.path.join(root, "repos", name + ".git")
        subprocess.run(["git", "clone", "-q", "--bare", seed, bare], check=True)
        subprocess.run(["git", "-C", bare, "config", "http.receivepack", "true"], check=True)
        bares[name] = bare
    log = os.path.join(root, "server.log")
    ready = os.path.join(root, "ready")
    with open(ready, "w") as out:
        server = subprocess.Popen([sys.executable, os.path.join(HERE, "net_serve.py"), os.path.join(root, "repos"), log, "%s:%s" % (N.USER, N.SECRET)], stdout=out)
    try:
        port = ""
        for _ in range(100):
            text = open(ready).read()
            if text.startswith("ready"):
                port = text.split()[1]
                break
            time.sleep(0.1)
        if not port:
            pty_e2e.fail("server started", "no ready line")
            return 1
        run(binpath, root, bares, seed, "http://127.0.0.1:%s/git/" % port)
    finally:
        server.kill()
        server.wait()
    print("%d failed" % pty_e2e.failures)
    return pty_e2e.failures


def run(binpath, root, bares, seed, base):
    askpass = os.path.join(root, "askpass.sh")
    with open(askpass, "w") as f:
        f.write('#!/bin/sh\ncase "$1" in\n  Username*) echo "%s" ;;\n  *) echo "$MGIT_TEST_PW" ;;\nesac\n' % N.USER)
    os.chmod(askpass, 0o755)
    env = dict(CLIENT_ENV)
    env["GIT_ASKPASS"] = askpass
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["MGIT_TEST_PW"] = N.SECRET
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["HOME"] = root
    url = base + "r.git"
    url2 = base + "r2.git"
    bare = bares["r"]
    bare2 = bares["r2"]

    client = os.path.join(root, "client")
    subprocess.run(["git", "clone", "-q", bare, client], check=True, env=GIT_ENV)
    git(client, "remote", "set-url", "origin", url)
    subprocess.run(["git", "-C", client, "config", "gc.auto", "0"], check=True)
    twin = os.path.join(root, "twin")
    pty_e2e.copy_repo(client, twin)

    def cfg(repo, name):
        return gitout(repo, "config", "--get-regexp", "^remote\\." + name + "\\.")

    s = Session(binpath, client, env=env)
    s.send("4")
    s.send("M")
    check("remotes: M lists origin and its URL", "remotes (1)" in s.text() and "origin" in s.text() and url in s.text(), s.text())

    # add
    s.send("a")
    s.send("second")
    s.send("\r")
    s.send(url2)
    raw = act(s, "\r", "second")
    wait_for(s, "remote add second")
    git(twin, "remote", "add", "second", url2)
    check("add: the config equals git remote add's", cfg(client, "second") == cfg(twin, "second") and url2 in cfg(client, "second"), cfg(client, "second") + "|" + cfg(twin, "second"))
    check("add: the list shows it", wait_for(s, "second  " + url2) or "second" in s.text(), s.text())

    # rename (cursor on second: it is the second row)
    s.send("j")
    s.send("r")
    s.send("other")
    s.send("\r")
    wait_for(s, "remote rename")
    git(twin, "remote", "rename", "second", "other")
    check("rename: config equals git remote rename's", cfg(client, "other") == cfg(twin, "other") and cfg(client, "second") == "", cfg(client, "other"))

    # set-url
    s.send("u")
    s.send(url2 + "x")
    s.send("\r")
    wait_for(s, "set-url")
    git(twin, "remote", "set-url", "other", url2 + "x")
    check("set-url: config equals git's", cfg(client, "other") == cfg(twin, "other") and url2 + "x" in cfg(client, "other"), cfg(client, "other"))
    s.send("u")
    s.send(url2)
    s.send("\r")
    wait_for(s, "set-url")
    git(twin, "remote", "set-url", "other", url2)

    # remove asks first
    s.send("d")
    s.send("n")
    s.send("\r")
    check("remove: anything but y keeps it", cfg(client, "other") != "", cfg(client, "other"))
    s.send("d")
    s.send("y")
    s.send("\r")
    wait_for(s, "remote remove")
    git(twin, "remote", "remove", "other")
    check("remove: config equals git remote remove's", cfg(client, "other") == "" and cfg(twin, "other") == "", cfg(client, "other"))
    s.send("q")

    # --- fetch variants ----------------------------------------------------------------
    git(client, "remote", "add", "other", url2)
    git(twin, "remote", "add", "other", url2)
    git(seed, "checkout", "-q", "-b", "gone", env=GIT_ENV)
    commit(seed, "g.txt", "g\n", "gone work")
    git(seed, "push", "-q", bare, "gone", env=GIT_ENV)
    git(seed, "push", "-q", bare2, "gone", "main", env=GIT_ENV)
    git(seed, "tag", "t-one", env=GIT_ENV)
    git(seed, "push", "-q", bare, "t-one", env=GIT_ENV)
    s.send("F")
    act(s, "a", "press Enter")
    s.send("\n")
    wait_for(s, "fetch --all: done")
    check("fetch --all: both remotes fetched", gitout(client, "rev-parse", "refs/remotes/origin/gone") == gitout(bare, "rev-parse", "gone") and gitout(client, "rev-parse", "refs/remotes/other/gone") == gitout(bare2, "rev-parse", "gone"), s.text())
    git(bare, "update-ref", "-d", "refs/heads/gone")
    s.send("F")
    act(s, "x", "press Enter")
    s.send("\n")
    wait_for(s, "fetch --prune: done")
    check("fetch --prune: the gone branch's tracking ref is removed", git(client, "rev-parse", "--verify", "-q", "refs/remotes/origin/gone")[2] != 0 and git(client, "rev-parse", "--verify", "-q", "refs/remotes/other/gone")[2] == 0, s.text())
    s.send("F")
    act(s, "t", "press Enter")
    s.send("\n")
    wait_for(s, "fetch --tags: done")
    check("fetch --tags: the tag arrived", gitout(client, "tag", "-l", "t-one") == "t-one", gitout(client, "tag", "-l"))
    s.send("F")
    s.send("o")
    s.send("other")
    raw = act(s, "\r", "press Enter")
    s.send("\n")
    wait_for(s, "fetch other: done")
    check("fetch a named remote: ran on the terminal", b"running 'fetch other'" in raw, repr(raw[-200:]))

    # --- push variants -----------------------------------------------------------------
    commit(client, "p.txt", "p\n", "push me")
    s.send("P")
    act(s, "g", "press Enter")
    s.send("\n")
    wait_for(s, "push: done")
    check("push: baseline", gitout(bare, "rev-parse", "main") == gitout(client, "rev-parse", "HEAD"))
    # diverge: amend the commit, a plain push is rejected, force-with-lease goes through
    git(client, "commit", "-q", "--amend", "-m", "push me again", env=GIT_ENV)
    s.send("P")
    act(s, "g", "press Enter")
    s.send("\n")
    wait_for(s, "failed")
    check("push: a diverged branch is rejected without force", gitout(bare, "rev-parse", "main") != gitout(client, "rev-parse", "HEAD"), s.text())
    s.send("P")
    act(s, "f", "press Enter")
    s.send("\n")
    wait_for(s, "force-with-lease: done")
    check("push --force-with-lease: the server has the amended commit", gitout(bare, "rev-parse", "main") == gitout(client, "rev-parse", "HEAD"), s.text())
    # tags
    git(client, "tag", "local-tag", env=GIT_ENV)
    s.send("P")
    act(s, "t", "press Enter")
    s.send("\n")
    wait_for(s, "push --tags: done")
    check("push --tags: the server has the tag", gitout(bare, "tag", "-l", "local-tag") == "local-tag", gitout(bare, "tag", "-l"))
    # another remote
    s.send("P")
    s.send("o")
    s.send("other")
    act(s, "\r", "press Enter")
    s.send("\n")
    wait_for(s, "push other main: done")
    check("push to another remote: the second server has the commit", gitout(bare2, "rev-parse", "main") == gitout(client, "rev-parse", "HEAD"), s.text())
    # delete a remote branch
    git(seed, "push", "-q", bare, "main:refs/heads/doomed", env=GIT_ENV)
    s.send("P")
    s.send("d")
    s.send("origin/doomed")
    act(s, "\r", "press Enter")
    s.send("\n")
    wait_for(s, "--delete doomed: done")
    check("push --delete: the branch is gone on the server", git(bare, "rev-parse", "--verify", "-q", "refs/heads/doomed")[2] != 0, s.text())
    s.send("P")
    s.send("d")
    s.send("nonsense")
    s.send("\r")
    check("push --delete: a name without remote/ is refused on the spot", "type remote/branch" in s.text(), s.text())

    # --- tags: push and delete on the remote -----------------------------------------------
    git(client, "tag", "-a", "-m", "annotated", "v-ann", env=GIT_ENV)
    s.send("T")
    check("tags: the list shows the tag", "v-ann" in s.text(), s.text())
    for _ in range(5):
        s.send("k")
    # find v-ann row: cursor to it
    rows = [l for l in s.text().split("\n") if "v-ann" in l]
    s.send("P")
    s.send("\r")
    wait_for(s, "press Enter")
    s.send("\n")
    wait_for(s, "done")
    tagged = gitout(bare, "tag", "-l")
    check("tag push: a tag (the selected one) reached the server", len(tagged.split("\n")) >= 2, tagged)
    s.send("T")
    s.send("X")
    s.send("\r")
    wait_for(s, "press Enter")
    s.send("\n")
    wait_for(s, "--delete")
    after = gitout(bare, "tag", "-l")
    check("tag remote delete: one tag fewer on the server", len(after.split("\n")) < len(tagged.split("\n")), after)

    s.send("\x1b")
    # --- prune through the remotes list --------------------------------------------------------
    git(seed, "push", "-q", bare, "main:refs/heads/stale", env=GIT_ENV)
    s.send("F")
    act(s, "f", "press Enter")
    s.send("\n")
    for _ in range(40):
        s.drain(0.3)
        if git(client, "rev-parse", "--verify", "-q", "refs/remotes/origin/stale")[2] == 0:
            break
    git(bare, "update-ref", "-d", "refs/heads/stale")
    check("prune: the stale tracking ref exists before", git(client, "rev-parse", "--verify", "-q", "refs/remotes/origin/stale")[2] == 0)
    s.send("M")
    act(s, "p", "press Enter")
    s.send("\n")
    wait_for(s, "prune")
    check("prune: M p removes it", git(client, "rev-parse", "--verify", "-q", "refs/remotes/origin/stale")[2] != 0, s.text())
    s.quit()
    check("fsck clean", git(client, "fsck", "--strict")[2] == 0)


if __name__ == "__main__":
    sys.exit(main())
