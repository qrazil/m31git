# 1git command reference

Generated from `1git --help` and `1git -<command> --help` (tests/golden/cli); do not edit.

```
usage: 1git [options] -<command> [...]

a git client: git's repositories, protocols and output, a command line of its own

commands:
  -s, -status                  show what changed in the work tree and the index
  -l, -log                     show the commit history
      -show                    show commits, tags, trees and files
  -d, -diff                    show changes between the work tree, the index and commits
  -a, -add                     stage changes
      -remove                  stop tracking files, and delete them
      -move                    move or rename files and directories
      -restore                 put files back as they are in the index or in a commit
      -reset                   move the current branch to another commit
  -c, -commit                  record the staged changes as a commit
  -w, -switch                  change branch
      -checkout                switch branches or restore files, git's way (see -switch and -restore)
  -b, -branch                  list, create, rename and delete branches
  -t, -tag                     list, create and delete tags
      -stash                   put the changes away, leaving a clean work tree
      -stash-list              list the stashes
      -stash-show              show the changes in a stash
      -stash-apply             apply a stash and keep it
      -stash-pop               apply a stash and drop it
      -stash-drop              delete one stash
      -stash-clear             delete every stash
  -m, -merge                   join another branch into the current one
  -r, -rebase                  replay commits on top of another base
      -cherry-pick             apply the changes of commits on the current branch
      -revert                  make commits that undo the changes of commits
      -clean                   delete untracked files (asks for --force or --dry-run)
      -worktree                list the work trees of this repository
      -worktree-add            check a branch out in another directory
      -worktree-remove         delete a work tree
      -worktree-prune          forget work trees whose directory is gone
      -clone                   copy a repository
      -init                    start a repository
  -f, -fetch                   download commits and refs from a remote
      -pull                    fetch, then join the upstream branch into the current one
  -p, -push                    send commits and refs to a remote
      -remote                  list the remotes
      -remote-add              add a remote
      -remote-remove           remove a remote and its remote-tracking refs
      -remote-rename           rename a remote
      -remote-set-url          change the URL of a remote
      -remote-get-url          print the URL of a remote
      -remote-show             show a remote and how branches relate
      -remote-prune            delete remote-tracking refs the remote no longer has
      -remote-set-head         set what the remote's HEAD is here
      -remote-refs             list the refs of a remote without fetching
      -config                  read, write, list and remove configuration
      -merge-base              the best common ancestor of two commits
      -rev-list                list the commits reachable from revisions, newest first
      -symbolic-ref            read, set or delete a symbolic ref such as HEAD
      -update-ref              set, move or delete a ref, checking what it was
      -show-ref                list refs with the objects they name
      -for-each-ref            list refs with the fields you ask for
      -hash-object             the object name of a file, and optionally store it
      -write-tree              write the index as a tree object
      -commit-tree             write a commit object for a tree
      -ls-files                list the files of the index and the work tree
      -check-ref-format        check that a ref name is well formed
      -reflog                  show where a ref has been (HEAD by default)
      -reflog-exists           exit 0 when a ref has a reflog, 1 when not
      -reflog-delete           delete reflog entries: REF@{N}
      -reflog-expire           forget reflog entries older than a time
      -reflog-list             list the refs that have a reflog
      -shortlog                summarize the history by author
      -describe                name a commit after the nearest tag
      -check-ignore            say which paths the ignore files ignore
      -blame                   show who last changed each line of a file
      -annotate                blame, in the older format
      -grep                    search the files of the work tree, the index or trees for a pattern
      -cat-file                print an object's type, size or contents
      -ls-tree                 list a tree's entries
      -rev-parse               the object names a revision resolves to, and facts about the repository
      -refs                    every ref in the repository, with what it points at
      -migrate                 write a git command line the 1git way

options:
       --help                  show this help
       --version               print the version and exit
  --C, --dir DIR               run as if started in this directory
  --c, --config NAME=VALUE...  set configuration for this run, like git -c
       --git-dir DIR           the repository's git directory
       --work-tree DIR         the work tree, when it is not next to the git directory
       --completions SHELL     print a shell completion script (bash, zsh or fish) and exit

exit status: 0 done, git's own status when a command failed (128 fatal, 1 plain failure; the commands after it did not run), 2 the line was not understood (nothing ran)
one dash is a command, two dashes an option, anything else data: 1git -add --all -commit --message 'fix' -push
an option's value cannot start with a dash: write --message=-x. Put an option that takes a list (--path, --message) after the operands.
from git: 1git -migrate 'git log --oneline -5' (docs/MIGRATING-FROM-GIT.md)
```

## -add

```
usage: 1git -add [options] [<PATH>...]

stage changes

arguments:
  [<PATH>...]               files and directories to stage ('.' is everything under here)

options:
       --help               show this help
  --a, --all                also stage deletions and new files everywhere
  --u, --update             stage changes to files git already tracks, add no new ones
  --p, --patch              choose hunks to stage, interactively
  --f, --force              add files that are ignored
       --executable on|off  set or clear the executable bit on what is staged
       --dry-run            show what would be staged
  --v, --verbose            list each file staged
```

## -annotate

```
usage: 1git -annotate [options] <FILE> [<REV>]

blame, in the older format

arguments:
  <FILE>                 the file
  [<REV>]                the revision to blame (default HEAD)

options:
       --help            show this help
  --L, --lines RANGE...  only these lines: N,M or N,+K or ,M
```

## -blame

```
usage: 1git -blame [options] <FILE> [<REV>]

show who last changed each line of a file

arguments:
  <FILE>                 the file
  [<REV>]                the revision to blame (default HEAD)

options:
       --help            show this help
  --e, --show-email      show the author email instead of the name
       --no-author       suppress the author and the date
       --long            the full commit name
  --f, --show-name       show the file name of each line
  --n, --show-number     show the line number in the original commit
       --raw-time        show the time as seconds and zone
       --blank-boundary  leave the name of boundary commits blank
       --root            do not treat root commits as boundaries
  --p, --porcelain       a format for programs
       --line-porcelain  the porcelain format with the commit data on every line
       --date STYLE      how dates are shown: iso, short, relative, unix, ...
       --abbrev N        digits of the commit name
  --L, --lines RANGE...  only these lines: N,M or N,+K or ,M
```

## -branch

```
usage: 1git -branch [options] [<PATTERN>...]

list, create, rename and delete branches

arguments:
  [<PATTERN>...]               list only branches matching these

options:
       --help                  show this help
       --create NAME           create a branch
       --from REV              where --create starts (default: HEAD)
       --delete NAME...        delete branches that are merged
       --force-delete NAME...  delete branches even when they are not merged
       --rename NAME...        rename a branch: NEW for the current one, or OLD NEW
       --copy NAME...          copy a branch: NEW for the current one, or OLD NEW
  --f, --force                 with --create, --rename or --copy: replace an existing branch
       --set-upstream REF      make the current branch track this remote branch
       --unset-upstream        stop the current branch tracking anything
  --t, --track                 with --create, track the start point
  --a, --all                   list local and remote branches
  --r, --remotes               list remote branches
  --v, --verbose               show the last commit of each branch
  --u, --upstream              also show what each branch tracks
       --current               print the name of the current branch
       --contains REV          only branches that contain this commit
       --without REV           only branches that do not contain this commit
       --merged REV            only branches merged into this commit
       --unmerged REV          only branches not merged into this commit
       --points-at REV         only branches at this commit
       --sort KEY              order by this key (refname, -refname, committerdate, ...)
       --format FORMAT         print each branch in this format
  --i, --ignore-case           sort and filter without regard to case
```

## -cat-file

```
usage: 1git -cat-file [options] [<TYPE or OBJECT>] [<OBJECT>]

print an object's type, size or contents

arguments:
  [<TYPE or OBJECT>]          with two operands the type to print the object as (blob, tree, commit, tag), else the object
  [<OBJECT>]                  an object name, a prefix of one, a ref, HEAD:path, ...

options:
       --help                 show this help
  --t, --type                 print the object's type word
  --s, --size                 print the size of the object's content
  --p, --pretty               print the object in a readable form
  --e, --exists               print nothing; exit 0 when the object exists
       --batch                for each name read from standard input print its header and contents
       --batch-check          for each name read from standard input print its header
       --batch-format FORMAT  like --batch, with a format: %(objectname) %(objecttype) %(objectsize) %(rest)
       --check-format FORMAT  like --batch-check, with a format
```

## -check-ignore

```
usage: 1git -check-ignore [options] [<PATH>...]

say which paths the ignore files ignore

arguments:
  [<PATH>...]      the paths

options:
       --help      show this help
  --q, --quiet     print nothing, just the exit status
       --stdin     read the paths from standard input
  --z, --nul       names end with NUL
       --no-index  look at paths the index tracks too
```

## -check-ref-format

```
usage: 1git -check-ref-format [options] <NAME>

check that a ref name is well formed

arguments:
  <NAME>                  the name

options:
       --help             show this help
       --allow-onelevel   accept a name without a slash
       --refspec-pattern  accept one * in the name
       --normalize        print the name with extra slashes removed
       --branch           check a branch name and print it
```

## -checkout

```
usage: 1git -checkout [options] [<REV>]

switch branches or restore files, git's way (see -switch and -restore)

arguments:
  [<REV>]                   a branch or a revision to check out (default: stay)

options:
       --help               show this help
       --path PATH...       restore only these paths from the target (put it last)
  --b, --create NAME        create a branch and switch to it
  --B, --reset-create NAME  create or reset a branch and switch to it
  --d, --detach             detach HEAD at the target
  --f, --force              throw local changes away
       --ours               for paths in a merge: take our side
       --theirs             for paths in a merge: take their side
  --t, --track              set the upstream of a new branch
  --p, --patch              choose the hunks to restore
  --q, --quiet              print nothing
```

## -cherry-pick

```
usage: 1git -cherry-pick [options] [<REV>...]

apply the changes of commits on the current branch

arguments:
  [<REV>...]                 the commits to apply, or ranges (a..b)

options:
       --help                show this help
       --record-origin       add a line naming the original commit
       --stage-only          stage the result without committing it
       --edit on|off         open the editor on each message
  --m, --mainline N          for a merge commit, the parent to compare against
  --s, --signoff             add a Signed-off-by line
       --allow-empty         keep commits that start out empty
       --prefer ours|theirs  on a conflict, take this side
       --continue            go on after resolving conflicts
       --skip                leave out the commit that conflicts
       --abort               give up and go back
       --quit                forget the operation but keep the work tree as it is
```

## -clean

```
usage: 1git -clean [options] [<PATH>...]

delete untracked files (asks for --force or --dry-run)

arguments:
  [<PATH>...]                only under these paths

options:
       --help                show this help
  --f, --force               really delete
       --dry-run             only show what would be deleted
  --d, --directories         also delete untracked directories
       --ignored also|only   also delete ignored files, or delete only those
       --nested              also delete directories that are git repositories (needs --force)
  --e, --exclude PATTERN...  keep files matching these patterns
  --q, --quiet               print nothing
```

## -clone

```
usage: 1git -clone [options] <URL> [<DIR>]

copy a repository

arguments:
  <URL>                 where it is (https://, ssh, or a path)
  [<DIR>]               where to put it (default: named after the repository)

options:
       --help           show this help
  --b, --branch NAME    check this branch out instead of the remote's default
       --depth N        only the last N commits
       --single-branch  only the history of one branch
       --bare           no work tree, just the repository
       --mirror         a bare copy of every ref
  --o, --origin NAME    call the remote this instead of origin
  --n, --skip-checkout  do not check anything out
       --filter SPEC    a partial clone, for example blob:none
  --q, --quiet          print nothing
```

## -commit

```
usage: 1git -commit [options]

record the staged changes as a commit

options:
       --help                                                show this help
  --m, --message TEXT...                                     the message: each text is a paragraph
  --F, --file FILE                                           read the message from a file ('-' is standard input)
  --a, --all                                                 stage changes to tracked files first
       --amend                                               replace the last commit
       --edit on|off                                         open the editor on the message (default: on, unless a message is given)
       --allow-empty                                         allow a commit that changes nothing
       --allow-empty-message                                 allow an empty message
       --author NAME <EMAIL>                                 commit as this author
       --date DATE                                           use this author date
       --reset-author                                        with --amend, take the author and date from now
  --s, --signoff                                             add a Signed-off-by line
       --fixup REV                                           a fixup commit for REV, for -rebase --autosquash
       --squash REV                                          a squash commit for REV, for -rebase --autosquash
       --reuse-message REV                                   reuse the message and author of a commit
  --n, --skip-hooks                                          do not run the pre-commit and commit-msg hooks
       --change-id                                           add a Gerrit Change-Id line (or set gerrit.createChangeId)
       --cleanup strip|whitespace|verbatim|scissors|default  how the message is cleaned up
       --dry-run                                             show what would be committed
  --q, --quiet                                               print only errors
       --path PATH...                                        commit only the changes to these paths (put it last)
```

## -commit-tree

```
usage: 1git -commit-tree [options] <TREE>

write a commit object for a tree

arguments:
  <TREE>                   the tree

options:
       --help              show this help
  --p, --parent COMMIT...  a parent commit
  --m, --message TEXT...   the message: each text is a paragraph (default: standard input)
  --F, --file FILE...      read the message from a file ('-' is standard input)
```

## -config

```
usage: 1git -config [options] [<NAME [VALUE]>...]

read, write, list and remove configuration

arguments:
  [<NAME [VALUE]>...]                        a key to read, or a key and a value to write

options:
       --help                                show this help
  --l, --list                                every key and value in effect
       --get                                 read one key: the last value (the default with one operand)
       --get-all                             read every value of a key
       --regexp                              read every key that matches a pattern
       --unset                               remove a key
       --unset-all                           remove every value of a key
       --add                                 add a value, keeping the others
       --replace-all                         replace every value of a key
       --scope local|global|system|worktree  which file to read or write (default: read all, write local)
  --f, --file FILE                           read or write this file
       --type bool|int|path|bool-or-int      show or store the value as this type
       --names-only                          show names without values
  --z, --nul                                 end each record with NUL
       --default VALUE                       what a missing key reads as
       --show-origin                         show the file each value comes from
       --show-scope                          show the scope each value comes from
```

## -describe

```
usage: 1git -describe [options] [<COMMIT>...]

name a commit after the nearest tag

arguments:
  [<COMMIT>...]           commits to name (default HEAD)

options:
       --help             show this help
       --tags             use any tag, not only annotated ones
       --long             always give the tag, the number of commits and the hash
       --always           show the abbreviated hash when no tag fits
       --exact-match      only a tag on exactly this commit
       --abbrev N         digits of the hash (0: leave it out)
       --match GLOB...    only tags that match
       --exclude GLOB...  not tags that match
```

## -diff

```
usage: 1git -diff [options] [<REV>...]

show changes between the work tree, the index and commits

arguments:
  [<REV>...]                                                  none: work tree against index; one: work tree against it; two, or a..b: between them

options:
       --help                                                 show this help
       --staged                                               compare the index against HEAD (or against the revision)
       --exit-code                                            exit with 1 when there are differences
  --q, --quiet                                                print nothing, and exit with 1 when there are differences
  --p, --patch                                                show the patch
       --stat                                                 show a diffstat
       --numstat                                              added and removed lines per file, for programs
       --shortstat                                            only the totals line of the diffstat
       --name-only                                            show the names of the changed files
       --name-status                                          show the names, each with a letter for what happened
       --raw                                                  show git's raw diff format
       --summary                                              show created, deleted and renamed files and mode changes
  --c, --context N                                            lines of context around each change
  --w, --ignore-all-space                                     ignore whitespace when comparing lines
  --b, --ignore-space-change                                  ignore changes in the amount of whitespace
       --renames on|off                                       detect renamed files (default: diff.renames)
       --rename-threshold PERCENT                             how similar two files must be to be a rename
       --swap                                                 swap the two sides
       --merge-diff separate|combined|dense|first-parent|off  how a merge commit shows its changes
       --diff-filter KINDS                                    keep only these kinds: A C D M R T U (lower case leaves them out)
       --word-diff plain|color|porcelain|none                 compare by words
  --a, --text                                                 treat every file as text
       --full-index                                           print full object names in the index lines
  --z, --nul                                                  end each name with a NUL instead of a newline
  --y, --side-by-side                                         lay the patch out as two columns, old and new
       --width COLUMNS                                        columns for --side-by-side (default: the terminal)
       --color always|never|auto                              when to use colour (default: auto)
       --path PATH...                                         only changes to these paths (put it last)
```

## -fetch

```
usage: 1git -fetch [options] [<REMOTE>] [<REFSPEC>...]

download commits and refs from a remote

arguments:
  [<REMOTE>]              where from (default: the upstream of the current branch, else origin)
  [<REFSPEC>...]          what to fetch (default: the remote's configured refs)

options:
       --help             show this help
  --a, --all              fetch every remote
  --p, --prune            delete remote-tracking refs the remote no longer has
  --t, --tags             fetch every tag
       --depth N          only the last N commits
       --unshallow        make a shallow repository complete
  --f, --force            overwrite local refs that do not fast-forward
       --filter SPEC      a partial fetch, for example blob:none
       --pull-request N   fetch GitHub pull request N as the branch pr/N
       --merge-request N  fetch GitLab merge request N as the branch mr/N
       --dry-run          show what would be fetched
  --q, --quiet            print nothing
  --v, --verbose          say more
```

## -for-each-ref

```
usage: 1git -for-each-ref [options] [<PATTERN>...]

list refs with the fields you ask for

arguments:
  [<PATTERN>...]                 only refs under these prefixes or matching these globs

options:
       --help                    show this help
       --count N                 stop after this many
       --sort KEY...             order by this key (-key reverses)
       --format FORMAT           what to print for each, with %(refname) %(objectname) %(subject) ...
       --contains COMMIT...      only refs that contain this commit
       --not-contains COMMIT...  only refs that do not contain this commit
       --merged COMMIT...        only refs merged into this commit
       --not-merged COMMIT...    only refs not merged into this commit
       --points-at OBJECT...     only refs that name this object
       --omit-empty              skip lines that came out empty
```

## -grep

```
usage: 1git -grep [options] [<PATTERN>] [<REV>...]

search the files of the work tree, the index or trees for a pattern

arguments:
  [<PATTERN>]                 the pattern (basic regular expression); not needed when --regexp gives them
  [<REV>...]                  search these trees instead of the work tree

options:
       --help                 show this help
       --path PATH...         only these paths (put it last)
  --e, --regexp PATTERN...    another pattern (any of them matches)
       --also PATTERN...      a pattern the same line must match too (with the last --regexp)
  --n, --line-number          show the line numbers
  --i, --ignore-case          ignore case
  --w, --word                 match whole words
  --v, --invert               lines that do not match
  --l, --files-with-matches   only the names of files with a match
  --L, --files-without-match  only the names of files without a match
  --c, --count                the number of matching lines per file
       --no-filename          do not show file names
  --H, --with-filename        show file names (the default)
  --E, --extended             extended regular expressions
  --F, --fixed                the pattern is a plain string
  --o, --only-matching        print only the matching parts
  --q, --quiet                print nothing, just the exit status
  --A, --after N              lines after each match
  --B, --before N             lines before each match
  --C, --context N            lines around each match
       --cached               search the index, not the work tree
       --skip-binary          do not search binary files
       --text                 search binary files as text
  --z, --nul                  end file names with NUL
       --heading              file names above their matches
       --break                an empty line between files
       --max-depth N          go down at most N directory levels
       --full-name            file names from the top of the work tree
```

## -hash-object

```
usage: 1git -hash-object [options] [<FILE>...]

the object name of a file, and optionally store it

arguments:
  [<FILE>...]         files to hash

options:
       --help         show this help
  --t, --type TYPE    blob (default), tree, commit or tag
  --w, --write        store the object
       --stdin        hash what comes on standard input
       --stdin-paths  read file names from standard input
```

## -init

```
usage: 1git -init [options] [<DIR>]

start a repository

arguments:
  [<DIR>]                           where (default: here)

options:
       --help                       show this help
       --bare                       no work tree, just the repository
  --b, --branch NAME                name the first branch this
       --object-format sha1|sha256  the hash the repository uses
  --q, --quiet                      print nothing
```

## -log

```
usage: 1git -log [options] [<REV>...]

show the commit history

arguments:
  [<REV>...]                                                  where to start: branches, tags, commits, ranges (a..b), ^excluded

options:
       --help                                                 show this help
  --n, --max N                                                stop after this many commits
       --skip N                                               skip this many commits first
       --oneline                                              one line per commit
       --graph                                                draw the history as a graph
       --all                                                  start from every ref
       --first-parent                                         follow only the first parent of merges
       --merges only|exclude                                  show only merge commits, or leave them out
       --reverse                                              oldest first
       --order topo|date|author-date                          never show a commit before its children (default: commit date)
       --follow                                               follow a single file across renames
       --only-given                                           show just the named commits, not their ancestors
       --author PATTERN                                       commits whose author matches
       --committer PATTERN                                    commits whose committer matches
       --since DATE                                           commits newer than this date
       --until DATE                                           commits older than this date
       --touches TEXT                                         commits that add or remove this text
  --i, --ignore-case                                          match --author, --committer and --grep without regard to case
       --match extended|fixed|basic                           how patterns are read (default: basic)
       --invert-grep                                          commits whose message does not match --grep
       --all-match                                            commits matching every --grep, not just one
       --format STYLE                                         oneline, short, medium, full, fuller, raw, or a format such as '%h %s'
       --decorate short|full|off                              show the refs that point at a commit
       --date STYLE                                           how dates are shown: iso, short, relative, raw, unix, rfc, format:...
       --abbrev N                                             digits of an abbreviated commit name
  --p, --patch                                                show the patch
       --stat                                                 show a diffstat
       --numstat                                              added and removed lines per file, for programs
       --shortstat                                            only the totals line of the diffstat
       --name-only                                            show the names of the changed files
       --name-status                                          show the names, each with a letter for what happened
       --raw                                                  show git's raw diff format
       --summary                                              show created, deleted and renamed files and mode changes
  --c, --context N                                            lines of context around each change
  --w, --ignore-all-space                                     ignore whitespace when comparing lines
  --b, --ignore-space-change                                  ignore changes in the amount of whitespace
       --renames on|off                                       detect renamed files (default: diff.renames)
       --rename-threshold PERCENT                             how similar two files must be to be a rename
       --swap                                                 swap the two sides
       --merge-diff separate|combined|dense|first-parent|off  how a merge commit shows its changes
       --diff-filter KINDS                                    keep only these kinds: A C D M R T U (lower case leaves them out)
       --word-diff plain|color|porcelain|none                 compare by words
  --a, --text                                                 treat every file as text
       --full-index                                           print full object names in the index lines
  --z, --nul                                                  end each name with a NUL instead of a newline
  --y, --side-by-side                                         lay the patch out as two columns, old and new
       --width COLUMNS                                        columns for --side-by-side (default: the terminal)
       --color always|never|auto                              when to use colour (default: auto)
  --s, --header-only                                          leave out the changes
       --grep PATTERN...                                      commits whose message matches any of these (put it after the revisions)
       --path PATH...                                         only commits that touch these paths (put it last)
```

## -ls-files

```
usage: 1git -ls-files [options] [<PATH>...]

list the files of the index and the work tree

arguments:
  [<PATH>...]              only these paths

options:
       --help              show this help
  --c, --cached            files in the index (the default)
  --d, --deleted           files in the index that are gone from the work tree
  --m, --modified          files that differ from the index
  --o, --others            files git does not track
  --i, --ignored           with --others or --cached: only the ignored ones
  --s, --stage             show mode, object name and stage
  --u, --unmerged          files with merge conflicts
  --z, --nul               end each name with NUL
       --full-name         names from the top of the work tree, not relative to here
       --error-unmatch     fail when a path matches no tracked file
       --exclude-standard  leave out what the ignore files list
```

## -ls-tree

```
usage: 1git -ls-tree [options] <TREE>

list a tree's entries

arguments:
  <TREE>               a tree, or anything that names one: a commit, a tag, HEAD~2, v1:dir

options:
       --help          show this help
       --path PATH...  only these paths (put it last)
  --r, --recursive     go into subtrees
  --t, --trees         with --recursive: show the trees too
  --d, --only-trees    show only the trees, not what is in them
  --l, --long          show the size of each file
  --z, --nul           end each name with NUL, unquoted
       --names-only    show only the names
       --objects-only  show only the object names
       --abbrev N      shorten the object names to this many digits
       --full-name     names from the top of the tree (the default from the top)
       --full-tree     list the whole tree, not what is below the current directory
```

## -merge

```
usage: 1git -merge [options] [<REV>]

join another branch into the current one

arguments:
  [<REV>]                                     the branch or commit to merge

options:
       --help                                 show this help
       --fast-forward allow|only|never        fast-forward when possible (the default), only that, or always make a merge commit
       --squash                               stage the result without committing or recording a merge
       --stage-only                           stage the result without committing it
  --m, --message TEXT...                      the merge message: each text is a paragraph
  --F, --file FILE                            read the merge message from a file
       --edit on|off                          open the editor on the merge message
       --strategy ort|ours|recursive|resolve  the merge strategy (default: ort)
       --prefer ours|theirs                   on a conflict, take this side
       --allow-unrelated                      merge histories that share nothing
       --continue                             finish a merge after resolving conflicts
       --abort                                give up the merge and go back
       --quit                                 forget the merge but keep the work tree as it is
  --q, --quiet                                print only errors
```

## -merge-base

```
usage: 1git -merge-base [options] <COMMIT> <COMMIT>

the best common ancestor of two commits

arguments:
  <COMMIT>            a commit
  <COMMIT>            another commit

options:
       --help         show this help
  --a, --all          every best common ancestor, not just one
       --is-ancestor  print nothing; exit 0 when the first is an ancestor of the second, 1 when not
```

## -migrate

```
usage: 1git -migrate [options] [<LINE>]

write a git command line the 1git way

arguments:
  [<LINE>]     a git command line, in quotes: 'git log --oneline -5'

options:
       --help  show this help
       --nul   read git's words from standard input and write ours, NUL-separated (for scripts)
```

## -move

```
usage: 1git -move [options] [<PATH>...]

move or rename files and directories

arguments:
  [<PATH>...]         one or more sources, then the destination

options:
       --help         show this help
  --f, --force        overwrite an existing destination
       --dry-run      show what would be moved
  --k, --skip-errors  skip sources that cannot be moved
  --v, --verbose      list each file moved
```

## -pull

```
usage: 1git -pull [options] [<REMOTE>] [<BRANCH>]

fetch, then join the upstream branch into the current one

arguments:
  [<REMOTE>]                             where from (default: the upstream of the current branch)
  [<BRANCH>]                             which branch (default: the upstream of the current branch)

options:
       --help                            show this help
       --integrate rebase|merge|ff-only  how to join: replay your commits, make a merge, or only fast-forward (default: pull.rebase, pull.ff, else only fast-forward)
       --autostash                       stash local changes and bring them back afterwards
       --squash                          stage the result without committing it
  --a, --all                             fetch every remote
  --p, --prune                           delete remote-tracking refs the remote no longer has
  --t, --tags                            fetch every tag
       --depth N                         only the last N commits
  --f, --force                           overwrite local refs that do not fast-forward
       --dry-run                         show what would be fetched
  --q, --quiet                           print nothing
```

## -push

```
usage: 1git -push [options] [<REF>...]

send commits and refs to a remote

arguments:
  [<REF>...]             what to send: a branch, SRC:DST, or a tag (default: the current branch)

options:
       --help            show this help
       --to REMOTE       where to send it (default: the upstream remote, else origin)
       --for BRANCH      ask Gerrit for review of the commit, as refs/for/BRANCH
       --topic NAME      with --for, the Gerrit topic
  --t, --track           make the pushed branch track its remote counterpart
  --f, --force           overwrite the remote branch, but only if it is where you last saw it
       --overwrite       overwrite the remote branch whatever is on it
       --delete          delete these refs on the remote
  --a, --all             send every branch
       --tags            send every tag
       --follow-tags     also send the annotated tags that point at what is sent
       --atomic          all or none of the refs
  --o, --option TEXT...  a push option for the server
       --dry-run         show what would be sent
  --q, --quiet           print nothing
  --v, --verbose         say more
```

## -rebase

```
usage: 1git -rebase [options] [<REV>] [<REV>]

replay commits on top of another base

arguments:
  [<REV>]                    the new base (default: the upstream of the current branch)
  [<REV>]                    the branch to rebase (default: the current one)

options:
       --help                show this help
       --onto REV            put the commits on this base instead of UPSTREAM
       --root                rebase every commit, including the first
  --i, --interactive         edit the list of commits first
       --autosquash          fold fixup! and squash! commits into their targets
       --autostash           stash local changes and bring them back afterwards
       --keep-base           keep the fork point, whatever UPSTREAM is now
       --update-refs         move branches that point into the rebased commits
       --replay              replay the commits even when nothing changes
  --x, --exec COMMAND...     run this command after each commit
       --continue            go on after resolving conflicts
       --skip                leave out the commit that conflicts
       --abort               give up and go back
       --quit                forget the rebase but keep the work tree as it is
       --edit-todo           edit the list of commits that remain
       --show-current-patch  show the commit being applied
  --q, --quiet               print only errors
```

## -reflog

```
usage: 1git -reflog [options] [<REF>]

show where a ref has been (HEAD by default)

arguments:
  [<REF>]            the ref (default: HEAD)

options:
       --help        show this help
  --n, --max N       stop after this many entries
       --date STYLE  show the dates in the selectors: iso, short, relative, unix ...
```

## -reflog-delete

```
usage: 1git -reflog-delete [options] [<REF@{N}>...]

delete reflog entries: REF@{N}

arguments:
  [<REF@{N}>...]  the entries

options:
       --help     show this help
       --rewrite  make the next entry start where the deleted one did
       --dry-run  only say what would go
```

## -reflog-exists

```
usage: 1git -reflog-exists <REF>

exit 0 when a ref has a reflog, 1 when not

arguments:
  <REF>        the ref

options:
       --help  show this help
```

## -reflog-expire

```
usage: 1git -reflog-expire [options] [<REF>...]

forget reflog entries older than a time

arguments:
  [<REF>...]          the refs (or --all)

options:
       --help         show this help
       --all          every ref
       --expire TIME  entries older than this (a date, 'now', 'never'; default 90 days)
       --dry-run      only say what would go
       --rewrite      make the next entry start where the deleted one did
```

## -reflog-list

```
usage: 1git -reflog-list

list the refs that have a reflog

options:
       --help  show this help
```

## -refs

```
usage: 1git -refs

every ref in the repository, with what it points at

options:
       --help  show this help
```

## -remote

```
usage: 1git -remote [options]

list the remotes

options:
       --help     show this help
  --v, --verbose  show the URLs
```

## -remote-add

```
usage: 1git -remote-add [options] <NAME> <URL>

add a remote

arguments:
  <NAME>                    what to call it
  <URL>                     where it is

options:
       --help               show this help
  --f, --fetch              fetch it right away
       --tags               fetch every tag
  --t, --track BRANCH...    track only these branches
       --mirror fetch|push  treat the remote as a mirror
```

## -remote-get-url

```
usage: 1git -remote-get-url [options] <NAME>

print the URL of a remote

arguments:
  <NAME>       the remote

options:
       --help  show this help
       --push  print the URL pushes go to
  --a, --all   print every URL
```

## -remote-prune

```
usage: 1git -remote-prune [options] <NAME>

delete remote-tracking refs the remote no longer has

arguments:
  <NAME>          the remote

options:
       --help     show this help
       --dry-run  only show what would be deleted
```

## -remote-refs

```
usage: 1git -remote-refs [options] [<REMOTE>] [<PATTERN>...]

list the refs of a remote without fetching

arguments:
  [<REMOTE>]        the remote or URL (default: the upstream remote)
  [<PATTERN>...]    only refs matching these

options:
       --help       show this help
       --branches   only branches
  --t, --tags       only tags
       --only-refs  leave out HEAD and peeled tags
       --symref     also show where symbolic refs point
       --exit-code  exit with 2 when nothing matches
  --q, --quiet      print nothing
```

## -remote-remove

```
usage: 1git -remote-remove <NAME>

remove a remote and its remote-tracking refs

arguments:
  <NAME>       the remote

options:
       --help  show this help
```

## -remote-rename

```
usage: 1git -remote-rename <OLD> <NEW>

rename a remote

arguments:
  <OLD>        the remote
  <NEW>        its new name

options:
       --help  show this help
```

## -remote-set-head

```
usage: 1git -remote-set-head [options] <NAME> [<BRANCH>]

set what the remote's HEAD is here

arguments:
  <NAME>         the remote
  [<BRANCH>]     the branch

options:
       --help    show this help
  --a, --auto    ask the remote
  --d, --delete  delete it
```

## -remote-set-url

```
usage: 1git -remote-set-url [options] <NAME> <URL> [<OLD>]

change the URL of a remote

arguments:
  <NAME>         the remote
  <URL>          the new URL
  [<OLD>]        with --add or --delete, which URL; otherwise replace only this one

options:
       --help    show this help
       --push    change the URL pushes go to
       --add     add a URL instead of replacing
       --delete  delete the URLs that match instead of replacing
```

## -remote-show

```
usage: 1git -remote-show [options] <NAME>

show a remote and how branches relate

arguments:
  <NAME>        the remote

options:
       --help   show this help
       --local  do not ask the remote, use what is stored here
```

## -remove

```
usage: 1git -remove [options] [<PATH>...]

stop tracking files, and delete them

arguments:
  [<PATH>...]        files to remove

options:
       --help        show this help
       --keep-files  remove from the index only, keep the files
  --r, --recursive   allow directories
  --f, --force       remove files that have changes
       --dry-run     show what would be removed
  --q, --quiet       print nothing
       --missing-ok  succeed when nothing matches
```

## -reset

```
usage: 1git -reset [options] [<REV>]

move the current branch to another commit

arguments:
  [<REV>]                           the commit to move to (default HEAD)

options:
       --help                       show this help
       --mode soft|mixed|hard|keep  soft keeps index and files, mixed resets the index, hard also discards file changes, keep discards only what is safe (default mixed)
  --q, --quiet                      print nothing
```

## -restore

```
usage: 1git -restore [options] [<PATH>...]

put files back as they are in the index or in a commit

arguments:
  [<PATH>...]      files and directories to restore

options:
       --help      show this help
       --from REV  restore from this commit (default: the index, or HEAD with --staged)
       --staged    restore the index
       --worktree  restore the work tree (the default unless --staged)
       --ours      take our side of a conflict
       --theirs    take their side of a conflict
  --p, --patch     choose hunks to restore, interactively
  --q, --quiet     print nothing
```

## -rev-list

```
usage: 1git -rev-list [options] [<REV>...]

list the commits reachable from revisions, newest first

arguments:
  [<REV>...]                  where to start: branches, tags, commits, ranges (a..b), ^excluded

options:
       --help                 show this help
  --n, --max N                stop after this many commits
       --skip N               skip this many commits first
       --count                print how many commits there are
       --reverse              oldest first
       --parents              print the parents after each commit
       --merges only|exclude  only merge commits, or leave them out
       --all                  start from every ref and HEAD
       --branches             start from every branch
       --tags                 start from every tag
       --remotes              start from every remote-tracking branch
```

## -rev-parse

```
usage: 1git -rev-parse [options] [<REV>...]

the object names a revision resolves to, and facts about the repository

arguments:
  [<REV>...]                 revisions: a ref, an object name, HEAD~2, main^{tree}, v1:path, A..B, ...

options:
       --help                show this help
       --git-dir             the git directory
       --absolute-git-dir    the git directory, absolute
       --git-common-dir      the directory shared by the linked work trees
       --toplevel            the top of the work tree
       --prefix              where this directory is below the top, with a slash
       --cdup                the way up to the top: ../..
       --inside-work-tree    true or false
       --inside-git-dir      true or false
       --bare                true or false
       --shallow             true or false
       --verify              exactly one valid revision, or fail
  --q, --quiet               with --verify: no message, just the status
       --short               shorten the object names
       --short-digits N      shorten the object names to this many digits
       --abbrev-ref          a branch or tag by its short name
       --symbolic            print the names as given
       --symbolic-full-name  print the full ref names
       --default REV         a revision to use when none is given
       --all                 every ref
       --branches            every branch
       --tags                every tag
       --remotes             every remote-tracking branch
       --revs-only           only the revisions
       --no-revs             only what is not a revision
       --object-format       sha1 or sha256
       --git-path PATH       the path of a file in the git directory
```

## -revert

```
usage: 1git -revert [options] [<REV>...]

make commits that undo the changes of commits

arguments:
  [<REV>...]                 the commits to undo, or ranges (a..b)

options:
       --help                show this help
       --stage-only          stage the result without committing it
       --edit on|off         open the editor on each message
  --m, --mainline N          for a merge commit, the parent to keep
  --s, --signoff             add a Signed-off-by line
       --allow-empty         keep commits that start out empty
       --prefer ours|theirs  on a conflict, take this side
       --continue            go on after resolving conflicts
       --skip                leave out the commit that conflicts
       --abort               give up and go back
       --quit                forget the operation but keep the work tree as it is
```

## -shortlog

```
usage: 1git -shortlog [options] [<REV>...]

summarize the history by author

arguments:
  [<REV>...]                  where to start (default HEAD)

options:
       --help                 show this help
  --s, --summary              only the number of commits per author
  --n, --numbered             most commits first
  --e, --email                show the email address too
  --c, --committer            group by committer, not author
       --merges only|exclude  only merge commits, or leave them out
```

## -show

```
usage: 1git -show [options] [<OBJECT>...]

show commits, tags, trees and files

arguments:
  [<OBJECT>...]                                               commits, tags, trees or blobs (default HEAD); REV:PATH is a file at a revision

options:
       --help                                                 show this help
       --oneline                                              one line per commit
       --format STYLE                                         oneline, short, medium, full, fuller, raw, or a format such as '%h %s'
       --date STYLE                                           how dates are shown: iso, short, relative, raw, unix, rfc, format:...
       --abbrev N                                             digits of an abbreviated commit name
  --p, --patch                                                show the patch
       --stat                                                 show a diffstat
       --numstat                                              added and removed lines per file, for programs
       --shortstat                                            only the totals line of the diffstat
       --name-only                                            show the names of the changed files
       --name-status                                          show the names, each with a letter for what happened
       --raw                                                  show git's raw diff format
       --summary                                              show created, deleted and renamed files and mode changes
  --c, --context N                                            lines of context around each change
  --w, --ignore-all-space                                     ignore whitespace when comparing lines
  --b, --ignore-space-change                                  ignore changes in the amount of whitespace
       --renames on|off                                       detect renamed files (default: diff.renames)
       --rename-threshold PERCENT                             how similar two files must be to be a rename
       --swap                                                 swap the two sides
       --merge-diff separate|combined|dense|first-parent|off  how a merge commit shows its changes
       --diff-filter KINDS                                    keep only these kinds: A C D M R T U (lower case leaves them out)
       --word-diff plain|color|porcelain|none                 compare by words
  --a, --text                                                 treat every file as text
       --full-index                                           print full object names in the index lines
  --z, --nul                                                  end each name with a NUL instead of a newline
  --y, --side-by-side                                         lay the patch out as two columns, old and new
       --width COLUMNS                                        columns for --side-by-side (default: the terminal)
       --color always|never|auto                              when to use colour (default: auto)
  --s, --header-only                                          leave out the changes
       --path PATH...                                         only changes to these paths (put it last)
```

## -show-ref

```
usage: 1git -show-ref [options] [<PATTERN>...]

list refs with the objects they name

arguments:
  [<PATTERN>...]      only refs whose name ends with these

options:
       --help         show this help
       --head         include HEAD
       --branches     only branches
       --tags         only tags
       --verify       exact ref names only; fail when one is missing
  --q, --quiet        print nothing, just the exit status
  --d, --dereference  also print the commit an annotated tag points at
  --s, --hash         print only the object names
       --abbrev N     shorten the object names to this many digits
       --exists       exit 0 when the ref exists, 2 when not
```

## -stash

```
usage: 1git -stash [options]

put the changes away, leaving a clean work tree

options:
       --help               show this help
  --m, --message TEXT       describe the stash
  --u, --include-untracked  also stash untracked files
  --k, --keep-index         leave staged changes in the work tree
  --q, --quiet              print nothing
```

## -stash-apply

```
usage: 1git -stash-apply [options] [<STASH>]

apply a stash and keep it

arguments:
  [<STASH>]             which stash: N or stash@{N} (default: the newest)

options:
       --help           show this help
       --restore-index  also restore what was staged
  --q, --quiet          print nothing
```

## -stash-clear

```
usage: 1git -stash-clear

delete every stash

options:
       --help  show this help
```

## -stash-drop

```
usage: 1git -stash-drop [options] [<STASH>]

delete one stash

arguments:
  [<STASH>]     which stash: N or stash@{N} (default: the newest)

options:
       --help   show this help
  --q, --quiet  print nothing
```

## -stash-list

```
usage: 1git -stash-list

list the stashes

options:
       --help  show this help
```

## -stash-pop

```
usage: 1git -stash-pop [options] [<STASH>]

apply a stash and drop it

arguments:
  [<STASH>]             which stash: N or stash@{N} (default: the newest)

options:
       --help           show this help
       --restore-index  also restore what was staged
  --q, --quiet          print nothing
```

## -stash-show

```
usage: 1git -stash-show [options] [<STASH>]

show the changes in a stash

arguments:
  [<STASH>]                 which stash: N or stash@{N} (default: the newest)

options:
       --help               show this help
  --p, --patch              show the patch
       --stat               show a diffstat
       --name-only          show the names of the changed files
       --name-status        show the names, each with a letter for what happened
  --u, --include-untracked  also show the untracked files
```

## -status

```
usage: 1git -status [options] [<PATH>...]

show what changed in the work tree and the index

arguments:
  [<PATH>...]                                    only report these paths

options:
       --help                                    show this help
  --f, --format long|short|porcelain|porcelain2  the layout: long, short, or a stable one for programs (default long)
  --b, --branch                                  show the branch in the short layout
  --z, --nul                                     end each entry with a NUL (with the porcelain layouts)
  --u, --untracked all|normal|no                 how untracked files are shown (default: normal, or status.showUntrackedFiles)
       --ignored traditional|matching|no         also show ignored files
       --renames on|off                          detect renamed files (default: status.renames)
       --stash                                   show how many stashes there are
```

## -switch

```
usage: 1git -switch [options] [<BRANCH>]

change branch

arguments:
  [<BRANCH>]                the branch to switch to ('-' is the previous one)

options:
       --help               show this help
  --c, --create NAME        create this branch and switch to it
       --force-create NAME  create this branch, or reset it if it exists, and switch to it
       --from REV           where the new branch starts (default: HEAD)
  --d, --detach             switch to a commit, not to a branch
       --discard-changes    throw local changes away
  --t, --track              make the new branch track its start point
  --q, --quiet              print nothing
```

## -symbolic-ref

```
usage: 1git -symbolic-ref [options] <NAME> [<REF>]

read, set or delete a symbolic ref such as HEAD

arguments:
  <NAME>               the symbolic ref
  [<REF>]              point it at this ref

options:
       --help          show this help
  --q, --quiet         no message when it is not a symbolic ref; exit 1
       --short         print refs/heads/main as main
       --shallow       print the ref it names, not what that names in turn
  --d, --delete        delete the symbolic ref
  --m, --message TEXT  the reflog message
```

## -tag

```
usage: 1git -tag [options] [<PATTERN>...]

list, create and delete tags

arguments:
  [<PATTERN>...]          list only tags matching these

options:
       --help             show this help
       --create NAME      create a tag
       --from REV         what --create tags (default: HEAD)
  --m, --message TEXT...  an annotated tag with this message: each text is a paragraph
  --F, --file FILE        an annotated tag with the message read from a file
  --a, --annotate         an annotated tag, with the message from the editor
       --delete NAME...   delete tags
  --f, --force            replace an existing tag
       --contains REV     only tags that contain this commit
       --without REV      only tags that do not contain this commit
       --merged REV       only tags merged into this commit
       --unmerged REV     only tags not merged into this commit
       --points-at REV    only tags at this commit
       --sort KEY         order by this key (refname, -refname, version:refname, ...)
       --format FORMAT    print each tag in this format
  --n, --lines N          with the list, show this many lines of each annotation
  --i, --ignore-case      sort and filter without regard to case
```

## -update-ref

```
usage: 1git -update-ref [options] <REF> [<VALUE>] [<OLD>]

set, move or delete a ref, checking what it was

arguments:
  <REF>                the ref to change (HEAD means the branch it is on)
  [<VALUE>]            the object it will name (with --delete: what it must be now)
  [<OLD>]              only when it names this now (all zeros: only when it does not exist)

options:
       --help          show this help
  --d, --delete        delete the ref
       --no-follow     change a symbolic ref itself, not what it names
  --m, --message TEXT  the reflog message
```

## -worktree

```
usage: 1git -worktree [options]

list the work trees of this repository

options:
       --help       show this help
       --porcelain  a stable layout for programs
  --v, --verbose    show more
  --z, --nul        end each field with a NUL (with --porcelain)
```

## -worktree-add

```
usage: 1git -worktree-add [options] <PATH>

check a branch out in another directory

arguments:
  <PATH>                    where to put the work tree

options:
       --help               show this help
       --from REV           what to check out (default: HEAD)
  --b, --branch NAME        create this branch there
       --reset-branch NAME  create this branch there, or reset it if it exists
  --d, --detach             check out a commit, not a branch
  --f, --force              allow a branch that is checked out elsewhere
  --q, --quiet              print nothing
```

## -worktree-prune

```
usage: 1git -worktree-prune [options]

forget work trees whose directory is gone

options:
       --help         show this help
       --dry-run      only show what would be forgotten
  --v, --verbose      say what is forgotten
       --expire WHEN  only those older than this
```

## -worktree-remove

```
usage: 1git -worktree-remove [options] <PATH>

delete a work tree

arguments:
  <PATH>        the work tree

options:
       --help   show this help
  --f, --force  delete it even with changes in it
```

## -write-tree

```
usage: 1git -write-tree [options]

write the index as a tree object

options:
       --help        show this help
       --missing-ok  do not check that the objects exist
```
