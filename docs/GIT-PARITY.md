# 1git and git: what is kept, what is dropped, what is left

**Goal (the owner, 2026-11-05): "1git end goal is COMPLETE GIT REPLACEMENT. Only
tweak would be to maybe drop a deprecated or unused features."** This replaces
the earlier scope of `GIT-COMPAT.md` ("the essence, not the museum", GitHub,
GitLab and Gerrit only): the list of "Out, on purpose" there is superseded by
the matrix below, which keeps git's own record as the guide. The command line
stays Oro's grammar (`CLI.md`); the repository, the protocols, the bytes and now
the exit statuses are git's. Real git (2.49 here) is the oracle.

## How parity is measured

`tests/conformance/run.sh <1git>` runs every case of `tests/conformance/cases.txt`
through git and through 1git in two identical scratch repositories (fixed
identities and dates, so object ids are equal) and compares stdout, the exit
status, and the state afterwards (refs, HEAD, index, `status`, stash list,
reflog of HEAD, config files, state files, work tree hashes). The 1git line is
not written by hand: `1git -migrate` turns git's own argv into it, so a git form
1git has no spelling for shows up as MISSING, not as a quiet skip.
`-v` prints diffs, `-k REGEX` picks cases. `tests/conformance/commands.tsv` is
the list of git's commands and the decision for each; `gen.py` turns it into the
matrix below and into `core/GIT_gitrefuse.m31`.

Numbers at 0.36.0 (git 2.49.0): see "Numbers" at the end. Fixtures, the dump of
the state, and the cases are in `tests/conformance/`; `known-failures.txt` lists
the cases where 1git differs today (each is a bug to fix, not a decision).

## Decisions

- **Exit status: git's.** Since 0.36.0 a command that fails ends the line with the
  status git gives (128 fatal, 129 usage error of the command, 1 plain failure,
  git's own 5/6 for `config`, 2 for `show-ref --exists`...). 2 stays reserved for a line
  that 1git's own grammar did not understand (nothing ran), as every Oro program
  does. The harness compares the status exactly.
- **Dropped commands** print `fatal: <reason>; <what to use>` and exit 128, like
  git's own refusals (`pack-redundant` dies unless `--i-still-use-this`):
  `-whatchanged`, `-pack-redundant`, `-filter-branch`, `-help`. Commands out of scope
  and commands still to come print the same kind of line saying so. They are
  not in `--help`; `--completions` lists what runs.
- **Things git keeps stay**: `checkout` (BreakingChanges: "all three commands
  will stay") is `-checkout` again, besides `-switch` and `-restore`;
  `-migrate` still rewrites `git checkout b` to `-switch b` when that says the
  same thing. `show-ref --heads` and `ls-remote --heads` (deprecated spellings of
  `--branches`) are accepted as aliases.
- **Plumbing takes git's options under Oro's names** (`1git -rev-list main
  --max 3`, `-show-ref --branches`, `-ls-files --others --exclude-standard`); `-migrate`
  and the harness translate. Options a command does not take yet are refused
  with status 129 and a message naming this file, never ignored.
- **git 3.0 defaults** (BreakingChanges.adoc): see the next section.

## What git itself plans to remove or change

From `BreakingChanges.adoc` (the 2.49 copy in /usr/share/doc/git and the one on
master, which adds the items marked *master*), `git help -a`, and the DEPRECATED
notes in the manual pages:

| item | git's record | 1git |
|---|---|---|
| `git whatchanged` | removal in 3.0 (refuses without `--i-still-use-this`) | **dropped**: use `-log --raw --no-merges` |
| `git pack-redundant` | removal in 3.0 (dies without `--i-still-use-this`) | **dropped**: use gc |
| `.git/branches/`, `.git/remotes/` | removal in 3.0 | not read, not written (ignored as 3.0 will) |
| grafts (`info/grafts`) | removal in 3.0, superseded by replace refs | not read; `replace` refs planned |
| `name-rev --stdin` | removal in 3.0 (*master*), use `--annotate-stdin` | only `--annotate-stdin` will exist |
| `core.commentString=auto`, `core.preferSymlinkRefs=true` | deprecated, removal in 3.0 (*master*) | not honoured |
| default hash sha1 -> sha256 | change in 3.0 | 1git reads and writes both formats; new repositories stay sha1 until git changes the default (`init --object-format sha256` works) |
| default ref storage files -> reftable (*master*) | change in 3.0 | files backend only; reftable read/write is LATER (a repository in reftable format is refused with a clear message) |
| default branch `master` -> `main` (*master*) | change in 3.0 | `init.defaultBranch` is honoured; the default stays `master` like git 2.49 until git changes it |
| `safe.bareRepository=explicit` (*master*) | change in 3.0 | LATER, with the setting |
| Rust mandatory (*master*) | build change | n/a |
| `git filter-branch` | man page: "its use is not recommended" | **dropped**; filter-repo works on the same repositories |
| `git stash save` | man page: deprecated in favour of `push` | not implemented |
| `merge-tree --trivial-merge` | man page: deprecated | only `--write-tree` will be implemented |
| `sparse-checkout` non-cone mode | man page: deprecated | cone mode only (when added) |
| `show-ref --heads`, `ls-remote --heads` | man pages: deprecated spelling of `--branches` | accepted as aliases |
| `git checkout` | "will stay" | kept |
| `git stage` | synonym of `add` | kept as an alias (planned) |
| `git config --list`-style `git var -l`, `merge --log`/`--no-log` synonyms | man pages: deprecated | `var -l` and the synonyms are not implemented |

## The matrix of commands

`done`: all options we know of pass the harness; `partial`: some; `missing`:
none. Decision: IMPLEMENT (P1 a developer's week, P2 housekeeping and the
plumbing others call, P3 the rest), LATER (in scope, waits on something), DROP
(git's own deprecation record), OUT (belongs to another ecosystem).

<!-- matrix:begin -->
148 git commands in the matrix: 1git state done 9, partial 37, missing 102; decision IMPLEMENT 116, LATER 8, DROP 4, OUT of scope 20.

| command | group | git 2.49 | 1git | decision | note |
|---|---|---|---|---|---|
| `add` | porcelain | kept | partial | IMPLEMENT P1 | -i and -e (interactive/edit) missing; -p, -A, -u, -N, --chmod, --renormalize done |
| `am` | porcelain | kept | missing | IMPLEMENT P1 | needs mailsplit/mailinfo/apply |
| `archive` | porcelain | kept | missing | IMPLEMENT P2 | tar first, zip second |
| `backfill` | porcelain | kept | missing | LATER P3 | partial clone follow-up (new in 2.49) |
| `bisect` | porcelain | kept | missing | IMPLEMENT P1 | start/good/bad/skip/reset/run/log/replay |
| `branch` | porcelain | kept | partial | IMPLEMENT P1 | --edit-description, --track variants, --copy partly |
| `bundle` | porcelain | kept | missing | IMPLEMENT P2 | create/verify/list-heads/unbundle (format-bundle v2/v3) |
| `checkout` | porcelain | kept (BreakingChanges: "all three commands will stay") | partial | IMPLEMENT P1 | 0.31: -checkout is a command again (-b -B --detach -f --ours --theirs --track -p -q and paths); -m, --orphan, --conflict refused |
| `cherry-pick` | porcelain | kept | partial | IMPLEMENT P1 |  |
| `citool` | porcelain | kept | missing | OUT | Tk GUI |
| `clean` | porcelain | kept | partial | IMPLEMENT P2 | -i and -e missing |
| `clone` | porcelain | kept | partial | IMPLEMENT P1 | --recurse-submodules, --reference, --shared, --local hardlinks missing |
| `commit` | porcelain | kept | partial | IMPLEMENT P1 | -S (gpg/ssh signing via external tools) missing; --fixup/--squash/-C/-c/--interactive checked per option in the harness |
| `describe` | porcelain | kept | missing | IMPLEMENT P1 |  |
| `diff` | porcelain | kept | partial | IMPLEMENT P1 | --word-diff, --color-moved, --ext-diff, textconv, --submodule missing |
| `fetch` | porcelain | kept | partial | IMPLEMENT P1 | --recurse-submodules, bundle-uri, protocol v0/v1 via file/git:// missing |
| `format-patch` | porcelain | kept | missing | IMPLEMENT P1 |  |
| `gc` | porcelain | kept | missing | IMPLEMENT P2 |  |
| `gitk` | porcelain | kept | missing | OUT | Tk GUI; mgit is the interactive client |
| `grep` | porcelain | kept | missing | IMPLEMENT P1 |  |
| `gui` | porcelain | kept | missing | OUT | Tk GUI; mgit is the interactive client |
| `init` | porcelain | kept | partial | IMPLEMENT P2 | --object-format sha256 and --ref-format are read by the library; --template, --separate-git-dir, --shared checked |
| `log` | porcelain | kept | partial | IMPLEMENT P1 | -L, --follow done, --show-signature, --pretty trailers and %(describe), --notes missing |
| `maintenance` | porcelain | kept | missing | IMPLEMENT P2 | run/start/stop/register/unregister (no scheduler daemon) |
| `merge` | porcelain | kept | partial | IMPLEMENT P1 | strategies ort and ours done; octopus, subtree, recursive options partial |
| `mv` | porcelain | kept | done | IMPLEMENT P3 |  |
| `notes` | porcelain | kept | missing | IMPLEMENT P2 |  |
| `pull` | porcelain | kept | partial | IMPLEMENT P1 |  |
| `push` | porcelain | kept | partial | IMPLEMENT P1 | --recurse-submodules, --signed missing |
| `range-diff` | porcelain | kept | missing | IMPLEMENT P3 |  |
| `rebase` | porcelain | kept | partial | IMPLEMENT P1 | merge backend with -i done; --rebase-merges, --update-refs check per option; apply backend only through --apply flags |
| `reset` | porcelain | kept | partial | IMPLEMENT P1 | -p done through -restore |
| `restore` | porcelain | kept | partial | IMPLEMENT P1 |  |
| `revert` | porcelain | kept | partial | IMPLEMENT P1 |  |
| `rm` | porcelain | kept | partial | IMPLEMENT P2 |  |
| `scalar` | porcelain | kept | missing | OUT | Microsoft's wrapper around config/maintenance/sparse-checkout; the pieces are separate commands |
| `shortlog` | porcelain | kept | missing | IMPLEMENT P1 |  |
| `show` | porcelain | kept | partial | IMPLEMENT P1 |  |
| `sparse-checkout` | porcelain | kept (non-cone mode deprecated, see below) | missing | IMPLEMENT P2 | cone mode only: git-sparse-checkout.adoc "non-cone mode is deprecated" |
| `stash` | porcelain | kept (stash save deprecated in favour of push) | partial | IMPLEMENT P2 | branch, create, store, export/import missing; save is not implemented |
| `status` | porcelain | kept | partial | IMPLEMENT P1 | --ahead-behind, --find-renames, submodule summary check per option |
| `submodule` | porcelain | kept | missing | IMPLEMENT P1 | add/init/update/status/foreach/sync/deinit/absorbgitdirs/summary |
| `switch` | porcelain | kept | partial | IMPLEMENT P1 |  |
| `tag` | porcelain | kept | partial | IMPLEMENT P1 | -s/-u/-v (signing) missing; --contains/--sort/--format partly |
| `worktree` | porcelain | kept | partial | IMPLEMENT P2 | move, lock, unlock, repair missing |
| `config` | ancillary-manipulators | kept | partial | IMPLEMENT P1 | 0.31: get/set/unset/list/--get-all/--get-regexp/--add/--replace-all/scopes/types/--default/--show-origin/--show-scope and the new list/get/set/unset verbs; --edit, --rename-section, --remove-section, --blob, --get-urlmatch missing |
| `fast-export` | ancillary-manipulators | kept | missing | IMPLEMENT P3 |  |
| `fast-import` | ancillary-manipulators | kept | missing | IMPLEMENT P3 |  |
| `filter-branch` | ancillary-manipulators | discouraged | missing | DROP | git-filter-branch.adoc WARNING: "its use is not recommended. Please use an alternative history filtering tool such as git filter-repo" |
| `mergetool` | ancillary-manipulators | kept | missing | LATER P3 | launches external tools; needs the merge machinery of -merge |
| `pack-refs` | ancillary-manipulators | kept | missing | IMPLEMENT P3 |  |
| `prune` | ancillary-manipulators | kept | missing | IMPLEMENT P2 |  |
| `reflog` | ancillary-manipulators | kept | missing | IMPLEMENT P1 | show/list/expire/delete/exists; the library (GIT_reflog) exists |
| `refs` | ancillary-manipulators | kept | partial | IMPLEMENT P3 | 1git -refs is its own listing; git refs verify/list/migrate missing |
| `remote` | ancillary-manipulators | kept | partial | IMPLEMENT P2 | update, set-branches, prune done; show -n |
| `repack` | ancillary-manipulators | kept | missing | IMPLEMENT P2 |  |
| `replace` | ancillary-manipulators | kept | missing | IMPLEMENT P3 | replace refs are read by the object layer? no: LATER read support too |
| `annotate` | ancillary-interrogators | kept (same as blame, other output) | missing | IMPLEMENT P1 | with blame |
| `blame` | ancillary-interrogators | kept | missing | IMPLEMENT P1 | the library of mgit's blame view exists |
| `bugreport` | ancillary-interrogators | kept | missing | OUT | collects a report about git itself |
| `count-objects` | ancillary-interrogators | kept | missing | IMPLEMENT P3 |  |
| `diagnose` | ancillary-interrogators | kept | missing | OUT | zip of diagnostics for git bug reports |
| `difftool` | ancillary-interrogators | kept | missing | LATER P3 | external diff tools |
| `fsck` | ancillary-interrogators | kept | missing | IMPLEMENT P2 |  |
| `gitweb` | ancillary-interrogators | kept | missing | OUT | Perl CGI web front end |
| `help` | ancillary-interrogators | kept | missing | DROP | replaced by --help of every command and docs/CLI-REFERENCE.md (man pages are git's) |
| `instaweb` | ancillary-interrogators | kept | missing | OUT | starts a web server for gitweb |
| `merge-tree` | ancillary-interrogators | kept (--trivial-merge mode deprecated) | missing | IMPLEMENT P2 | --write-tree mode only: git-merge-tree.adoc "deprecated --trivial-merge" |
| `rerere` | ancillary-interrogators | kept | partial | IMPLEMENT P3 | rerere.enabled recording exists in the merge code; the command (status/diff/forget/clear/gc) is missing |
| `show-branch` | ancillary-interrogators | kept | missing | IMPLEMENT P3 |  |
| `verify-commit` | ancillary-interrogators | kept | missing | IMPLEMENT P3 | runs gpg/ssh-keygen/gpgsm |
| `verify-tag` | ancillary-interrogators | kept | missing | IMPLEMENT P3 | runs gpg/ssh-keygen/gpgsm |
| `version` | ancillary-interrogators | kept | done | IMPLEMENT P3 | 1git --version |
| `whatchanged` | ancillary-interrogators | removal-3.0 | missing | DROP | BreakingChanges.adoc: "The git-whatchanged(1) command has outlived its usefulness more than 10 years ago, and takes more keystrokes to type than its rough equivalent git log --raw ... The command will be removed." Use: 1git -log --raw (--no-merges) |
| `cvsexportcommit` | foreign | kept | missing | OUT | CVS ecosystem |
| `cvsimport` | foreign | kept | missing | OUT | CVS ecosystem |
| `cvsserver` | foreign | kept | missing | OUT | CVS server emulator |
| `imap-send` | foreign | kept | missing | OUT | mail transport (email send is out of scope) |
| `p4` | foreign | kept | missing | OUT | Perforce ecosystem |
| `quiltimport` | foreign | kept | missing | OUT | quilt ecosystem |
| `request-pull` | foreign | kept | missing | LATER P3 | summary text for mail; needs the remote check |
| `send-email` | foreign | kept | missing | OUT | SMTP/Perl; format-patch and am cover the file side |
| `svn` | foreign | kept | missing | OUT | Subversion ecosystem |
| `apply` | plumbing-manipulators | kept | missing | IMPLEMENT P1 | --check, --stat, --numstat, --index, --cached, -3, -R, -p<n>, --reject, --whitespace |
| `checkout-index` | plumbing-manipulators | kept | missing | IMPLEMENT P2 |  |
| `commit-graph` | plumbing-manipulators | kept | missing | IMPLEMENT P3 | only an accelerator; reading it is optional |
| `commit-tree` | plumbing-manipulators | kept | done | IMPLEMENT P1 | 0.31 (no -S) |
| `hash-object` | plumbing-manipulators | kept | done | IMPLEMENT P1 | 0.31 (no filters: --path, --no-filters accepted only as the default) |
| `index-pack` | plumbing-manipulators | kept | missing | IMPLEMENT P2 | the pack reader of the library exists |
| `merge-file` | plumbing-manipulators | kept | missing | IMPLEMENT P2 | the three-way merge of -merge exists |
| `merge-index` | plumbing-manipulators | kept | missing | IMPLEMENT P3 |  |
| `mktag` | plumbing-manipulators | kept | missing | IMPLEMENT P3 |  |
| `mktree` | plumbing-manipulators | kept | missing | IMPLEMENT P2 |  |
| `multi-pack-index` | plumbing-manipulators | kept | missing | IMPLEMENT P3 | accelerator |
| `pack-objects` | plumbing-manipulators | kept | missing | IMPLEMENT P2 | the pack writer of push exists |
| `prune-packed` | plumbing-manipulators | kept | missing | IMPLEMENT P3 |  |
| `read-tree` | plumbing-manipulators | kept | missing | IMPLEMENT P2 |  |
| `replay` | plumbing-manipulators | experimental | missing | LATER P3 | "EXPERIMENTAL" in git help -a |
| `symbolic-ref` | plumbing-manipulators | kept | done | IMPLEMENT P1 | 0.31 |
| `unpack-objects` | plumbing-manipulators | kept | missing | IMPLEMENT P2 |  |
| `update-index` | plumbing-manipulators | kept | missing | IMPLEMENT P2 |  |
| `update-ref` | plumbing-manipulators | kept | partial | IMPLEMENT P1 | 0.31: set/delete/verify old; --stdin transactions and --create-reflog missing |
| `write-tree` | plumbing-manipulators | kept | done | IMPLEMENT P1 | 0.31 (--prefix missing) |
| `cat-file` | plumbing-interrogators | kept | partial | IMPLEMENT P1 | 0.31: -t -s -p -e, <type> <object>, --batch and --batch-check with formats; --textconv, --filters, --batch-command, --batch-all-objects, --follow-symlinks missing |
| `cherry` | plumbing-interrogators | kept | missing | IMPLEMENT P2 |  |
| `diff-files` | plumbing-interrogators | kept | missing | IMPLEMENT P2 |  |
| `diff-index` | plumbing-interrogators | kept | missing | IMPLEMENT P2 |  |
| `diff-tree` | plumbing-interrogators | kept | missing | IMPLEMENT P2 |  |
| `for-each-ref` | plumbing-interrogators | kept | done | IMPLEMENT P1 | 0.31: atoms refname objectname objecttype objectsize subject body contents author* committer* tagger* creator* tag symref upstream HEAD parent tree numparent, sort, count, contains/merged/points-at; %(if) %(align) --shell/--perl/--python/--tcl missing |
| `for-each-repo` | plumbing-interrogators | kept | missing | IMPLEMENT P3 |  |
| `get-tar-commit-id` | plumbing-interrogators | kept | missing | LATER P3 | with archive |
| `ls-files` | plumbing-interrogators | kept | partial | IMPLEMENT P1 | 0.31: -c -d -m -o -i -s -u -z --full-name --error-unmatch --exclude-standard; -k -t -v --eol --directory -x -X --format --with-tree --recurse-submodules missing |
| `ls-remote` | plumbing-interrogators | kept | partial | IMPLEMENT P1 | as -remote-refs; a local path as the remote fails (known gap) |
| `ls-tree` | plumbing-interrogators | kept | partial | IMPLEMENT P1 | 0.31: -r -t -d -l -z --name-only --object-only --abbrev --full-name --full-tree and paths; --format missing |
| `merge-base` | plumbing-interrogators | kept | partial | IMPLEMENT P1 | 0.31: two commits, --all, --is-ancestor; --octopus, --independent, --fork-point missing |
| `name-rev` | plumbing-interrogators | kept (--stdin removal-3.0) | missing | IMPLEMENT P2 | BreakingChanges.adoc: "Git 3.0 removes the support for --stdin altogether": only --annotate-stdin is implemented |
| `pack-redundant` | plumbing-interrogators | removal-3.0 | missing | DROP | BreakingChanges.adoc: "this command will finally be removed" (dies unless --i-still-use-this since 4406522b76); use gc |
| `rev-list` | plumbing-interrogators | kept | partial | IMPLEMENT P1 | 0.31: --count -n --skip --reverse --parents --no-merges --merges --all --branches --tags --remotes, ranges, ^; --objects, --first-parent, --author..., --boundary, --left-right, pathspecs missing (log has most) |
| `rev-parse` | plumbing-interrogators | kept | partial | IMPLEMENT P1 | 0.31: revisions and ranges, --verify --short --abbrev-ref --symbolic(-full-name) --show-toplevel --git-dir --show-prefix --show-cdup --is-* --all/--branches/--tags --default; --parseopt, --sq-quote, --local-env-vars, @{upstream} forms checked per case |
| `show-index` | plumbing-interrogators | kept | missing | IMPLEMENT P3 |  |
| `show-ref` | plumbing-interrogators | kept | done | IMPLEMENT P1 | 0.31 (--heads kept as git keeps it) |
| `unpack-file` | plumbing-interrogators | kept | missing | IMPLEMENT P3 |  |
| `var` | plumbing-interrogators | kept | missing | IMPLEMENT P2 |  |
| `verify-pack` | plumbing-interrogators | kept | missing | IMPLEMENT P2 |  |
| `daemon` | plumbing-sync | kept | missing | OUT | git:// server |
| `fetch-pack` | plumbing-sync | kept | missing | IMPLEMENT P3 |  |
| `http-backend` | plumbing-sync | kept | missing | OUT | CGI server side |
| `send-pack` | plumbing-sync | kept | missing | IMPLEMENT P3 |  |
| `update-server-info` | plumbing-sync | kept | missing | LATER P3 | dumb HTTP only; not on git's removal list |
| `check-attr` | helpers | kept | missing | IMPLEMENT P2 |  |
| `check-ignore` | helpers | kept | missing | IMPLEMENT P1 | the ignore matcher of the library exists |
| `check-mailmap` | helpers | kept | missing | IMPLEMENT P3 |  |
| `check-ref-format` | helpers | kept | done | IMPLEMENT P2 | 0.31 |
| `column` | helpers | kept | missing | IMPLEMENT P3 |  |
| `credential` | helpers | kept | missing | IMPLEMENT P2 | the helper protocol (get/store/erase) |
| `credential-cache` | helpers | kept | missing | LATER P3 | unix-socket daemon |
| `credential-store` | helpers | kept | missing | IMPLEMENT P2 |  |
| `fmt-merge-msg` | helpers | kept | missing | IMPLEMENT P3 |  |
| `hook` | helpers | kept | missing | IMPLEMENT P2 | run |
| `interpret-trailers` | helpers | kept | missing | IMPLEMENT P2 |  |
| `mailinfo` | helpers | kept | missing | IMPLEMENT P2 | with am |
| `mailsplit` | helpers | kept | missing | IMPLEMENT P2 | with am |
| `merge-one-file` | helpers | kept | missing | IMPLEMENT P3 |  |
| `patch-id` | helpers | kept | missing | IMPLEMENT P3 |  |
| `sh-i18n` | helpers | kept | missing | OUT | shell script helper for git's own scripts |
| `sh-setup` | helpers | kept | missing | OUT | shell script helper for git's own scripts |
| `stripspace` | helpers | kept | missing | IMPLEMENT P2 | the library function exists |
| `stage` | alias | kept (synonym of add) | missing | IMPLEMENT P3 | git-stage.adoc: "git stage <arg>..." is git add; -migrate maps it to -add |
<!-- matrix:end -->

## Everything that is not a command

| area | git | 1git today | decision |
|---|---|---|---|
| config keys | the `config/*.adoc` set | the ones the implemented commands read (core.*, user.*, init.defaultBranch, commit.gpgsign refusal, pull.rebase, push.default, branch.*, remote.*, rerere.enabled, gerrit.createChangeId, ...) | grow with each command; `config` itself is generic |
| hooks | pre-commit, prepare-commit-msg, commit-msg, post-commit, pre-rebase, post-checkout, post-merge, pre-push, post-rewrite, pre-auto-gc, reference-transaction, push-to-checkout, fsmonitor, ... | commit-msg, pre-commit, prepare-commit-msg, post-commit, pre-push, post-checkout/merge/rewrite run for the commands that exist | IMPLEMENT: every hook with its command; `-hook run` P2 |
| `.gitattributes` | text, eol, filter, diff, merge, ident, export-ignore, linguist | text/eol on checkout and add | IMPLEMENT P2: filters (clean/smudge, LFS), diff drivers (external tools are LATER), merge drivers |
| `.gitignore`, info/exclude, core.excludesFile | full | done (library), `check-ignore` missing | IMPLEMENT P1 |
| `.gitmodules`, submodules | full | none | IMPLEMENT P1 |
| linked worktrees | add, list, remove, prune, move, lock, repair | add/list/remove/prune | IMPLEMENT P2 |
| sparse-checkout, skip-worktree | cone, sparse index | none | IMPLEMENT P2 (cone) |
| partial clone | `--filter`, promisor remotes, lazy fetch | `--filter` on clone | IMPLEMENT P2: lazy fetch of missing objects |
| shallow | `--depth`, `--shallow-since`, `--deepen`, `--unshallow` | `--depth`, reads `.git/shallow` | IMPLEMENT P2 |
| bundles | create, verify, list-heads, unbundle, bundle-uri | none | IMPLEMENT P2 |
| notes | refs/notes, `notes.displayRef`, log --notes | none | IMPLEMENT P2 |
| replace refs | refs/replace, `--no-replace-objects` | none | IMPLEMENT P3 |
| reflog | full | written by every command, read by `@{n}` | IMPLEMENT P1 (`reflog` command) |
| protocols | smart HTTP v2, SSH, file, git://, dumb HTTP, protocol v0/v1 | smart HTTP v2, SSH, local path | file:// P1; v0/v1 fallback P3; git:// P3; dumb HTTP LATER |
| credential helpers | `credential.helper`, store, cache, osxkeychain, libsecret, GCM | helper protocol client for the configured helper | `credential`, `-store`: IMPLEMENT P2 |
| merge strategies | ort, recursive, octopus, ours, subtree, resolve | ort, ours; `-X` options partly | octopus P2, subtree P3, recursive = ort alias, resolve LATER |
| rebase backends | merge (default), apply, `-i`, `--rebase-merges`, `--update-refs`, `--exec` | merge backend, `-i`, `--onto`, `--autosquash`, `--exec`, `--autostash` | `--rebase-merges`, `--update-refs` P1; apply backend flags P3 |
| rerere | record, replay, gc | recording and replay inside merge | the command P3 |
| commit-graph, multi-pack-index | accelerators | not read, not written | P3, no semantic effect |
| gc, maintenance, repack, prune | full | none | P2 |
| fsck | full | none | P2 |
| fast-import, fast-export | full | none | P3 |
| format-patch, am, apply | full | none | P1 |
| bisect | full | none | P1 |
| blame, annotate | full | library for mgit's view | P1 |
| describe, shortlog, grep | full | none | P1 |
| log pretty formats, graph | full | most placeholders, graph, decorations | check per placeholder with the harness |
| range-diff, cherry | full | none | P2/P3 |
| signing | gpg, ssh, x509 through external tools | refuses `commit.gpgsign=true` | IMPLEMENT P2: run gpg / ssh-keygen / gpgsm like git does |
| SHA-256 | `extensions.objectFormat` | read and write | done |
| reftable | `extensions.refStorage` | refused | LATER |
| exit statuses | 128/129/1/... | git's since 0.36.0 | done |

## Numbers

Run `bash tests/conformance/run.sh ./1git` for the current table; the figures
below are from the commit that carries this file.

| measure | at 0.36.0 |
|---|---|
| git commands in the matrix | 148 (done 9, partial 37, missing 102) |
| decisions | IMPLEMENT 116, LATER 8, DROP 4 (`whatchanged`, `pack-redundant`, `filter-branch`, `help`), OUT of scope 20 |
| conformance cases | 585 over 75 commands: **469 pass**, 0 unexpected failures, 10 known gaps, 106 missing (no 1git spelling yet) |
| commands with a passing case | 38 |
| option spellings in `tests/cli_cases.txt` | 491 options covered, 116 git spellings migrated |

Known gaps (`known-failures.txt`): `reset --keep` with local changes (git refuses,
1git resets), `tag --sort=-creatordate` with equal dates, `stash push <path>`,
`cherry-pick A..B` across a merge, `rebase --onto` (git prints the "dropping ...
already upstream" line), `rebase -i` of a branch that is already merged,
`worktree list` column width (git 2.49 pads two spaces), `ls-remote` of a local
path. `init` does not copy git's template directory (sample hooks,
`description`, `info/exclude`): the harness ignores those files until it does.

What remains, in the order of the work plan: P1 `reflog`, `blame`/`annotate`,
`describe`, `shortlog`, `grep`, `format-patch`/`am`/`apply`, `bisect`,
`submodule`, `check-ignore`, `rebase --rebase-merges --update-refs`,
`file://` remotes, and the missing options of the commands that exist; then P2
(`gc`, `maintenance`, `fsck`, `repack`, `prune`, `notes`, `bundle`,
`sparse-checkout`, `worktree move/lock`, `credential`, the object plumbing
`index-pack`, `pack-objects`, `unpack-objects`, `read-tree`, `update-index`,
`diff-tree`, `diff-index`, `diff-files`, `checkout-index`, `mktree`,
`merge-file`, `merge-tree`, `name-rev`, `var`, `verify-pack`, `stripspace`,
`hook`, `interpret-trailers`, `mailinfo`, `mailsplit`, signing); then P3.
