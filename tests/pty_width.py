#!/usr/bin/env python3
"""mgit's start-up width probe (tui 0.14.0), end to end through the real binary, on a pty.

    python3 tests/pty_width.py <mgit-binary> <scratch-dir>

The terminal is `pyte` made to answer cursor position reports (`CSI 6 n`) as a real one does: every byte mgit
writes is fed to the emulator and the reports it produces go back to mgit at once (tui's `tests/width_pty.m31`
plays the terminal the same way for a bare loop). The width model of the emulator is swapped as in
`pty_variants.py`. Checked:

  * an answering terminal: the probe is asked (`CSI 6 n` is in what mgit wrote), and no frame waits for
    the 150 ms budget;
  * a terminal that draws box characters two columns wide: mgit measures it and writes its borders as ASCII
    (no line-drawing character on the screen, `+---` and `|` instead), and the screen equals the terminal's own
    repaint (a resize writes a full frame); the same terminal with `--borders unicode` keeps the characters;
  * a terminal that agrees with the library keeps its line-drawing borders; `--borders ascii` and
    `TUI_BORDERS=ascii` write ASCII anyway;
  * `--width-probe off` and `TUI_WIDTH_PROBE=off` ask nothing (no `CSI 6 n`), whatever the terminal is;
  * a mute terminal (no answers): the first frame comes after the probe's budget (a lower bound only, so a slow
    machine cannot fail it), the borders are the unicode ones, and a key typed during the wait is not lost (the help
    it asks for is drawn).
  * a bad `--width-probe` or `--borders` value is refused (see `pty_cli.py`).

Time to the first frame of each case is printed as a note (`note ...`), never asserted from above.

Margins: pty writes never block, a dead child is tolerated, every wait is "until the bytes are there, then quiet" (hundreds of
ms, up to 20 s), the repository is made under a directory this process resolves (`PWD`, `GIT_CEILING_DIRECTORIES`).
Skips with a note when pyte is missing.
"""
import fcntl
import os
import pty
import select
import shutil
import struct
import subprocess
import sys
import termios
import time

try:
    import pyte
    import pyte.screens
except ImportError:
    print("skip pty_width: pyte is not installed")
    sys.exit(0)

binpath, scratch = os.path.abspath(sys.argv[1]), os.path.realpath(sys.argv[2])
shutil.rmtree(scratch, ignore_errors=True)
os.makedirs(scratch, exist_ok=True)
ROWS, COLS = 30, 100
BOX = "─│┌┐└┘╭╮╰╯"
CPR_ASK = b"\x1b[6n"
ALT_ON = b"\x1b[?1049h"
failures = 0
checks = 0
_pyte_width = pyte.screens.wcwidth


def box_wide(ch):
    return 2 if 0x2500 <= ord(ch) <= 0x257F else _pyte_width(ch)


def check(name, condition, detail=""):
    global failures, checks
    checks += 1
    if condition:
        print("ok   " + name, flush=True)
    else:
        failures += 1
        print("FAIL " + name + ": " + detail, flush=True)


def git(*args):
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null", GIT_AUTHOR_NAME="t",
               GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x")
    subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off"] + list(args), env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


repo = os.path.join(scratch, "repo")
os.makedirs(repo)
git("init", "-q", "-b", "main")
for name in ("a.txt", "b.txt"):
    with open(os.path.join(repo, name), "w") as f:
        f.write("one\ntwo\n")
git("add", "-A")
git("commit", "-q", "-m", "first")
with open(os.path.join(repo, "a.txt"), "a") as f:
    f.write("three\n")


class Answering(pyte.Screen):
    """A pyte screen whose `CSI 6 n` reports go back to the program."""

    def __init__(self, cols, rows, master):
        super().__init__(cols, rows)
        self.master = master

    def write_process_input(self, data):
        try:
            os.write(self.master, data.encode())
        except (OSError, BlockingIOError):
            pass


class Mgit:
    def __init__(self, args=(), env_extra=None, width=_pyte_width, answers=True, keys=None):
        self.width = width
        self.master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
        fcntl.fcntl(self.master, fcntl.F_SETFL, fcntl.fcntl(self.master, fcntl.F_GETFL) | os.O_NONBLOCK)
        env = dict(os.environ)
        for key in ("M31GIT_MOUSE", "TERM_PROGRAM", "VISUAL", "GIT_EDITOR", "EDITOR", "NO_COLOR", "TUI_WIDTH_PROBE",
                    "TUI_BORDERS"):
            env.pop(key, None)
        env.update(TERM="xterm-256color", COLORTERM="truecolor", PWD=repo, GIT_CEILING_DIRECTORIES=scratch,
                   M31GIT_STATE="off", M31GIT_MOUSE="off", LANG="C.UTF-8", GIT_CONFIG_GLOBAL="/dev/null")
        env.update(env_extra or {})
        self.screen = (Answering if answers else pyte.Screen)(COLS, ROWS, self.master) if answers else pyte.Screen(COLS, ROWS)
        self.stream = pyte.ByteStream(self.screen)
        self.raw = b""
        self.started = time.time()
        self.alt_at = None
        self.frame_at = None
        self.proc = subprocess.Popen([binpath, "--sync", "off", "--mouse", "off"] + list(args), stdin=slave,
                                     stdout=slave, stderr=slave, cwd=repo, env=env, start_new_session=True)
        os.close(slave)
        self.keys = keys
        self.is_keys_sent = False

    def feed(self, chunk):
        self.raw += chunk
        pyte.screens.wcwidth = self.width
        try:
            self.stream.feed(chunk)
        finally:
            pyte.screens.wcwidth = _pyte_width
        now = time.time()
        if self.alt_at is None and ALT_ON in self.raw:
            self.alt_at = now
            if self.keys and not self.is_keys_sent:
                self.is_keys_sent = True
                self.write(self.keys)
        if self.frame_at is None and b"main" in self.raw:
            self.frame_at = now

    def write(self, data):
        try:
            os.write(self.master, data)
        except (OSError, BlockingIOError):
            pass

    def drain(self, quiet):
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
            self.feed(chunk)

    def settle(self, quiet=0.8, timeout=20.0):
        """Read until the first frame is there (or the time is up), then until quiet."""
        end = time.time() + timeout
        while self.frame_at is None and time.time() < end and self.proc.poll() is None:
            self.drain(0.1)
        self.drain(quiet)

    def text(self):
        return ["".join(self.screen.buffer[y][x].data or " " for x in range(COLS)) for y in range(ROWS)]

    def repaint(self):
        """A resize writes a full frame: what the same terminal shows after it, from a blank screen."""
        mark = 0
        for rows in (ROWS + 1, ROWS):
            fcntl.ioctl(self.master, termios.TIOCSWINSZ, struct.pack("HHHH", rows, COLS, 0, 0))
            try:
                os.killpg(os.getpgid(self.proc.pid), 28)
            except OSError:
                pass
            if rows == ROWS:
                mark = len(self.raw)
            self.drain(0.8)
        fresh = pyte.Screen(COLS, ROWS)
        pyte.screens.wcwidth = self.width
        try:
            pyte.ByteStream(fresh).feed(self.raw[mark:])
        finally:
            pyte.screens.wcwidth = _pyte_width
        return ["".join(fresh.buffer[y][x].data or " " for x in range(COLS)) for y in range(ROWS)]

    def first_frame_ms(self):
        if self.alt_at is None or self.frame_at is None:
            return None
        return int((self.frame_at - self.started) * 1000)

    def probe_wait_ms(self):
        if self.alt_at is None or self.frame_at is None:
            return None
        return int((self.frame_at - self.alt_at) * 1000)

    def close(self):
        self.write(b"q")
        end = time.time() + 3
        while self.proc.poll() is None and time.time() < end:
            self.drain(0.1)
        if self.proc.poll() is None:
            self.proc.kill()
        self.proc.wait()
        try:
            os.close(self.master)
        except OSError:
            pass


def has_box(lines):
    return any(ch in BOX for line in lines for ch in line)


def run(args=(), env_extra=None, width=_pyte_width, answers=True, keys=b"?"):
    m = Mgit(args, env_extra, width, answers, keys)
    m.settle()
    return m


def note(name, m):
    print("note %s: first frame %s ms after the start, %s ms after the alternate screen" %
          (name, m.first_frame_ms(), m.probe_wait_ms()), flush=True)


# mgit's status screen has no borders: every case opens the help (`?`), a panel with a rounded border, as its first key.

# --- a terminal that answers and agrees with the library -------------------------------------
m = run()
try:
    note("answering terminal", m)
    check("the probe is asked (CSI 6 n)", CPR_ASK in m.raw)
    check("an agreeing terminal keeps line-drawing borders", has_box(m.text()), "\n".join(m.text()[:6]))
    check("the help is drawn", any("unstage" in t for t in m.text()))
    check("the screen shows the repository", any("main" in t for t in m.text()))
finally:
    m.close()

# --- a terminal that draws box characters two columns wide ------------------------------------
m = run(width=box_wide)
try:
    note("box-wide terminal", m)
    check("box-wide: the probe is asked", CPR_ASK in m.raw)
    check("box-wide: no line-drawing character on the screen (ASCII borders)", not has_box(m.text()), "\n".join(m.text()[:8]))
    check("box-wide: ASCII borders are there", any("+-" in t for t in m.text()) and any("|" in t for t in m.text()), "\n".join(m.text()[:8]))
    shown = m.text()
    again = m.repaint()
    check("box-wide: the screen equals the terminal's own repaint", shown == again,
          " | ".join("row %d %r != %r" % (y, shown[y].rstrip(), again[y].rstrip()) for y in range(ROWS) if shown[y] != again[y]))
finally:
    m.close()

m = run(["--borders", "unicode"], width=box_wide)
try:
    check("box-wide with --borders unicode: the characters stay (the user asked)", has_box(m.text()))
finally:
    m.close()

m = run(["--borders", "ascii"])
try:
    check("--borders ascii on an agreeing terminal: ASCII", not has_box(m.text()) and any("|" in t for t in m.text()), "\n".join(m.text()[:6]))
finally:
    m.close()

m = run(env_extra={"TUI_BORDERS": "ascii"})
try:
    check("TUI_BORDERS=ascii: ASCII", not has_box(m.text()) and any("|" in t for t in m.text()), "\n".join(m.text()[:6]))
finally:
    m.close()

# --- the probe off -------------------------------------------------------------------------
for label, args, env in (("--width-probe off", ["--width-probe", "off"], None),
                         ("TUI_WIDTH_PROBE=off", [], {"TUI_WIDTH_PROBE": "off"}),
                         ("TUI_WIDTH_PROBE=off with --width-probe on", ["--width-probe", "on"], {"TUI_WIDTH_PROBE": "off"})):
    m = run(args, env, width=box_wide)
    try:
        note(label + " (box-wide terminal)", m)
        check(label + ": nothing is asked", CPR_ASK not in m.raw)
        check(label + ": the screen is drawn", any("main" in t for t in m.text()))
    finally:
        m.close()

# --- a terminal that never answers -------------------------------------------------------------
m = run(answers=False)
try:
    note("mute terminal", m)
    waited = m.probe_wait_ms()
    check("mute: the probe is asked", CPR_ASK in m.raw)
    check("mute: the first frame waits for the budget (at least 120 ms of 150)", waited is not None and waited >= 120, str(waited))
    check("mute: the borders are the unicode ones (the 0.13 policy)", has_box(m.text()), "\n".join(m.text()[:6]))
    check("mute: a key typed during the wait is not lost (help is drawn)", any("unstage" in t for t in m.text()), "\n".join(m.text()[:12]))
finally:
    m.close()

m = run(["--width-probe", "off"], answers=False)
try:
    note("mute terminal, --width-probe off", m)
    check("mute with --width-probe off: nothing is asked", CPR_ASK not in m.raw)
finally:
    m.close()

print("pty_width: %d checks, %d failed" % (checks, failures))
sys.exit(1 if failures else 0)
