#!/usr/bin/env python3
"""mgit on tui's `Loop.run_with` (`ui/GIT_ui_app.m31`), under a real pty: the bytes it writes.

    python3 tests/pty_loop.py <mgit-binary> <scratch-dir>

What is checked, from the raw bytes (no emulator needed):

  * entry and exit: the alternate screen, the mouse modes (and no motion mode)
    with the mouse on, none with `--mouse off`, all of them taken off on a quit;
  * `--sync on|off|auto`: DECRQM (`CSI ? 2026 $ p`) is asked, or not -- `off`
    never, `auto` of every terminal but Terminal.app and a dumb one, `on` always;
    frames are written inside `CSI ? 2026 h` ... `l` only after the terminal
    answered that it has the mode (set, reset or permanently set), never when it
    stayed silent or answered "not recognised";
  * a bad `--sync` value is a usage error (status 2);
  * the editor handoff: the terminal is given back (alternate screen off, modes
    off) before the editor runs and taken again after it.

  * the escape wait (`Loop.escape_wait_ms`, tui 0.12.0): `ESC [ B` written in two
    pieces 80 ms apart is one key (a Down arrow), after a key so that the loop's read starts at a random point of
    its timer period, and mgit is still running after it; a lone ESC quits it, after a wait.

Margins: the pty is never written to with a blocking write, a closed pty or a
dead child is tolerated, nothing is asserted about how soon bytes arrive (every
wait is "until the bytes are there", up to 20 s, then a quiet period), and the
repository is made in a directory this process resolves itself (`PWD`,
`GIT_CEILING_DIRECTORIES`: the m31 runtime has no getcwd on macOS before m31 0.8.0).
"""
import fcntl
import os
import pty
import select
import shutil
import subprocess
import sys
import time

binpath, scratch = os.path.abspath(sys.argv[1]), os.path.realpath(sys.argv[2])
shutil.rmtree(scratch, ignore_errors=True)
os.makedirs(scratch, exist_ok=True)
failures = 0
checks = 0

ALT_ON, ALT_OFF = b"\x1b[?1049h", b"\x1b[?1049l"
MOUSE_ON, MOUSE_OFF = b"\x1b[?1000h\x1b[?1002h\x1b[?1006h", b"\x1b[?1006l\x1b[?1002l\x1b[?1000l"
HOVER_ON = b"\x1b[?1003h"
QUERY, BEGIN, END = b"\x1b[?2026$p", b"\x1b[?2026h", b"\x1b[?2026l"


def check(name, condition, detail=""):
    global failures, checks
    checks += 1
    if condition:
        print("ok   " + name, flush=True)
    else:
        failures += 1
        print("FAIL " + name + ": " + detail, flush=True)


genv = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x")
repo = os.path.join(scratch, "repo")
os.makedirs(repo, exist_ok=True)
subprocess.run(["git", "init", "-q", "-b", "main", repo], env=genv, check=True)
with open(os.path.join(repo, "a.txt"), "w") as f:
    f.write("one\n")
subprocess.run(["git", "-C", repo, "add", "-A"], env=genv, check=True)
subprocess.run(["git", "-C", repo, "commit", "-q", "-m", "one"], env=genv, check=True)
with open(os.path.join(repo, "a.txt"), "a") as f:
    f.write("two\n")
editor = os.path.join(scratch, "editor.sh")
with open(editor, "w") as f:
    f.write("#!/bin/sh\necho EDITOR-RAN\nprintf 'a message\\n' > \"$1\"\nexit 0\n")
os.chmod(editor, 0o755)


def env_with(**extra):
    env = dict(os.environ)
    for key in ("M31GIT_MOUSE", "TERM_PROGRAM", "VISUAL", "GIT_EDITOR", "EDITOR", "NO_COLOR"):
        env.pop(key, None)
    env.update(TERM="xterm-256color", PWD=repo, GIT_CEILING_DIRECTORIES=scratch, M31GIT_STATE="off", M31GIT_MOUSE="on")
    env.update(extra)
    return env


class Run:
    """mgit on a pty: `drain` what it wrote, `send` keys (non-blocking), `finish`."""

    def __init__(self, args, env):
        self.master, slave = pty.openpty()
        flags = fcntl.fcntl(self.master, fcntl.F_GETFL)
        fcntl.fcntl(self.master, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self.proc = subprocess.Popen([binpath] + args, stdin=slave, stdout=slave, stderr=slave, cwd=repo, env=env)
        os.close(slave)
        self.out = b""

    def drain(self, quiet=0.5):
        while True:
            try:
                ready, _, _ = select.select([self.master], [], [], quiet)
            except (OSError, ValueError):
                return
            if not ready:
                return
            try:
                chunk = os.read(self.master, 65536)
            except BlockingIOError:
                continue
            except OSError:
                return
            if not chunk:
                return
            self.out += chunk

    def wait_for(self, marker, after=0, timeout=20.0):
        """Read until `marker` is in what was written after offset `after` (or the
        time is up, or the child is gone), then a quiet period for the rest."""
        end = time.time() + timeout
        while time.time() < end:
            if marker in self.out[after:]:
                break
            self.drain(0.1)
            if self.proc.poll() is not None and marker not in self.out[after:]:
                self.drain(0.2)
                break
        self.drain()

    def send(self, data, quiet=0.5, after_bytes=True):
        """Write `data` (never blocking) and wait until mgit has answered with some
        bytes (a frame) and been quiet for `quiet`."""
        at = len(self.out)
        try:
            os.write(self.master, data)
        except (OSError, BlockingIOError):
            pass
        end = time.time() + 20.0
        while after_bytes and len(self.out) == at and time.time() < end and self.proc.poll() is None:
            self.drain(0.1)
        self.drain(quiet)

    def quiet_send(self, data, quiet=0.5):
        """Write `data` and wait only for a quiet period (for keys that draw nothing)."""
        self.send(data, quiet, after_bytes=False)

    def wait_exit(self, timeout=20.0):
        end = time.time() + timeout
        while self.proc.poll() is None and time.time() < end:
            self.drain(0.1)
        return self.proc.poll()

    def mark(self):
        return len(self.out)

    def finish(self):
        if self.proc.poll() is None:
            self.quiet_send(b"q", 0.2)
        if self.wait_exit(20.0) is None:
            self.proc.kill()
            self.proc.wait()
        self.drain(0.2)
        os.close(self.master)
        return self.proc.returncode


def start(args, env, answer=None):
    run = Run(args, env)
    run.wait_for(ALT_ON)
    if answer is not None:
        run.quiet_send(answer)
    return run


# --- entry and exit -------------------------------------------------------------------------
run = start(["--sync", "off", repo], env_with())
check("entry: the alternate screen and the mouse modes", ALT_ON in run.out and MOUSE_ON in run.out, repr(run.out[:120]))
check("entry: no motion reports asked for", HOVER_ON not in run.out)
check("--sync off: nothing asked, no marker", QUERY not in run.out and BEGIN not in run.out)
run.send(b"j")
status = run.finish()
check("a quit: status 0, the mouse and the screen given back", status == 0 and MOUSE_OFF in run.out and run.out.rstrip().endswith(ALT_OFF), repr(run.out[-120:]))
check("--sync off: no marker in the whole run", BEGIN not in run.out and QUERY not in run.out)

run = start(["--mouse", "off", "--sync", "off", repo], env_with())
check("--mouse off: no mouse modes", MOUSE_ON not in run.out and ALT_ON in run.out)
run.finish()

# --- --sync ---------------------------------------------------------------------------------
run = start([repo], env_with())
check("default (auto), xterm: the terminal is asked", QUERY in run.out)
run.send(b"j")
check("asked and not answered: no marker, plain frames", BEGIN not in run.out and len(run.out) > 100)
run.finish()

run = start(["--sync", "auto", repo], env_with(), answer=b"\x1b[?2026;2$y")
at = run.mark()
run.send(b"j")
frame = run.out[at:]
check("answered (reset, supported): the next frame is inside the markers", frame.startswith(BEGIN) and frame.rstrip().endswith(END), repr(frame[:60]) + " ... " + repr(frame[-40:]))
check("one pair of markers for the frame", frame.count(BEGIN) == 1 and frame.count(END) == 1, repr(frame))
at = run.mark()
run.send(b"\t")
frame = run.out[at:]
check("every frame after it is too (Tab: another mode)", frame.startswith(BEGIN) and frame.count(BEGIN) == 1 and frame.count(END) == 1, repr(frame[:60]))
run.finish()
check("on the way out: the markers closed before the mouse and the screen are given back", END in run.out[at:] and run.out.rstrip().endswith(ALT_OFF))

for reply, name in ((b"\x1b[?2026;1$y", "set"), (b"\x1b[?2026;3$y", "permanently set")):
    run = start([repo], env_with(), answer=reply)
    at = run.mark()
    run.send(b"j")
    check("answered (%s): frames are inside the markers" % name, run.out[at:].startswith(BEGIN))
    run.finish()

for reply, name in ((b"\x1b[?2026;0$y", "not recognised"), (b"\x1b[?2026;4$y", "permanently reset")):
    run = start([repo], env_with(), answer=reply)
    at = run.mark()
    run.send(b"j")
    check("answered (%s): plain frames" % name, BEGIN not in run.out[at:] and len(run.out[at:]) > 20, repr(run.out[at:][:60]))
    run.finish()

run = start(["--sync", "off", repo], env_with(), answer=b"\x1b[?2026;2$y")
at = run.mark()
run.send(b"j")
check("--sync off: an answer nobody asked for is not acted on", BEGIN not in run.out[at:])
run.finish()

run = start([repo], env_with(TERM_PROGRAM="Apple_Terminal"))
check("auto, Terminal.app: never asked", QUERY not in run.out and ALT_ON in run.out, repr(run.out[:80]))
run.finish()
for name in ("dumb", "linux", "vt100"):
    run = start([repo], env_with(TERM=name))
    check("auto, TERM=%s: never asked" % name, QUERY not in run.out and ALT_ON in run.out, repr(run.out[:80]))
    run.finish()
run = start(["--sync", "on", repo], env_with(TERM_PROGRAM="Apple_Terminal"))
check("--sync on is exact: asked of Terminal.app too", QUERY in run.out)
run.finish()
run = start(["--sync", "off", repo], env_with(TERM="xterm-kitty"))
check("--sync off: not asked of a terminal that has it", QUERY not in run.out)
run.finish()

# --- the command line -----------------------------------------------------------------------
proc = subprocess.run([binpath, "--sync", "maybe", repo], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env_with())
check("--sync maybe: refused with 2", proc.returncode == 2 and "'--sync' needs one of on, off, auto, and got 'maybe'" in proc.stderr, proc.stderr)
proc = subprocess.run([binpath, "--no-sync", repo], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env_with())
check("--no-sync: refused with 2 (Oro has no --no-x)", proc.returncode == 2 and "--no-sync" in proc.stderr, proc.stderr)
proc = subprocess.run([binpath, "--sync"], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env_with())
check("--sync with no value: refused with 2", proc.returncode == 2, proc.stderr)

# --- the editor handoff ---------------------------------------------------------------------
run = start(["--sync", "off", repo], env_with(EDITOR=editor))
run.send(b"s")
run.send(b"2")
at = run.mark()
run.quiet_send(b"e", 0.3)
run.wait_for(b"EDITOR-RAN", after=at)
run.wait_for(ALT_ON, after=at + max(run.out[at:].find(b"EDITOR-RAN"), 0))
seen = run.out[at:]
left, ran = seen.find(ALT_OFF), seen.find(b"EDITOR-RAN")
back = seen.find(ALT_ON, ran if ran >= 0 else 0)
check("editor: the screen is given back, the editor runs, the screen is taken again", 0 <= left < ran < back, "left %d ran %d back %d" % (left, ran, back))
check("editor: the mouse is off while it runs and on again after", seen.find(MOUSE_OFF) >= 0 and seen.find(MOUSE_OFF) < ran and seen.find(MOUSE_ON, ran) > ran)
status = run.finish()
check("editor: a quit afterwards still ends with 0", status == 0)

# --- the escape wait ----------------------------------------------------------------------
# In Status a lone Escape quits. `ESC [ B` is the Down arrow: written in two pieces 80 ms
# apart (well inside the 250 ms wait) it must stay one key whatever the phase of the
# loop's 250 ms timer (before tui 0.12.0 a tick could shorten the wait to 1 ms).
run = start(["--sync", "off", repo], env_with())
split_ok = True
for i in range(12):
    # a key first: the loop's next read then starts at a random point of its 250 ms timer
    # period, which is what used to shorten the wait for the rest of the sequence
    run.quiet_send(b"j", 0.0)
    time.sleep(0.005)
    run.quiet_send(b"\x1b", 0.0)
    time.sleep(0.08)
    run.quiet_send(b"[B", 0.5)
    if run.proc.poll() is not None:
        split_ok = False
        break
    time.sleep(0.037 * (i % 5) + 0.011 * i)  # another phase of the timer each time
check("escape: ESC [ B written in two pieces 80 ms apart is one key, 12 times at different timer phases", split_ok and run.proc.poll() is None)
run.quiet_send(b"\x1b", 0.2)
status = run.wait_exit()
check("escape: a lone ESC quits Status (after its wait)", status == 0, str(status))
run.drain(0.2)
check("escape: the terminal is given back", run.out.rstrip().endswith(ALT_OFF))
try:
    os.close(run.master)
except OSError:
    pass

print("%d checks, %d failure(s)" % (checks, failures))
sys.exit(1 if failures else 0)
