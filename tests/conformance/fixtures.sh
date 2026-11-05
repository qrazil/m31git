# Fixtures of the conformance harness: each function builds a repository in
# the directory it is given, with fixed identities and dates so that every
# object id is the same each time. Sourced by run.sh. bash 3.2 and BSD tools.

fx_env() {
    export GIT_AUTHOR_NAME="Ann Author" GIT_AUTHOR_EMAIL="ann@example.com"
    export GIT_COMMITTER_NAME="Cy Committer" GIT_COMMITTER_EMAIL="cy@example.com"
}

# fx_commit <message> <epoch>: commit what is staged at a fixed time
fx_commit() {
    GIT_AUTHOR_DATE="$2 +0000" GIT_COMMITTER_DATE="$2 +0000" git commit -q -m "$1"
}

fx_init() {
    mkdir -p "$1" && cd "$1" || return 1
    git init -q -b main . || return 1
}

fixture_empty() {
    fx_init "$1"
}

fixture_basic() {
    fx_init "$1" || return 1
    printf 'one\ntwo\nthree\n' > a.txt
    printf 'alpha\nbeta\n' > b.txt
    mkdir -p dir
    printf 'gamma\n' > dir/c.txt
    git add . && fx_commit "first" 1700000000
    printf 'one\nTWO\nthree\nfour\n' > a.txt
    git add . && fx_commit "second: change a" 1700001000
    git tag v1
    printf 'delta\n' >> b.txt
    git rm -q dir/c.txt
    mkdir -p dir
    printf 'epsilon\n' > dir/d.txt
    git add . && fx_commit "third: more" 1700002000
    git tag -a -m "annotated" v2
    git branch topic HEAD~1
}

# staged, unstaged, untracked and ignored changes over `basic`
fixture_dirty() {
    fixture_basic "$1" || return 1
    printf 'one\nTWO\nthree\nfour\nfive\n' > a.txt
    printf 'new staged\n' > staged.txt
    git add staged.txt
    printf 'untracked\n' > untracked.txt
    printf '*.log\n' > .gitignore
    printf 'noise\n' > x.log
    mkdir -p empty-ish/sub && printf 'u\n' > empty-ish/sub/u.txt
}

# two branches that diverged, merged with a merge commit
fixture_merge() {
    fixture_basic "$1" || return 1
    git switch -q -c side HEAD~2
    printf 'side\n' > side.txt
    git add . && fx_commit "side work" 1700003000
    git switch -q main
    printf 'main\n' > main.txt
    git add . && fx_commit "main work" 1700004000
    GIT_AUTHOR_DATE="1700005000 +0000" GIT_COMMITTER_DATE="1700005000 +0000" git merge -q --no-ff -m "merge side" side
}

# a conflict waiting: both branches changed a.txt
fixture_conflict() {
    fixture_basic "$1" || return 1
    git switch -q -c other v1
    printf 'one\nOTHER\nthree\n' > a.txt
    git add . && fx_commit "other edit" 1700003000
    git switch -q main
}
