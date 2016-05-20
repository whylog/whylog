#!/bin/bash -ux

base_remote="${1:-origin}"
base_branch="${2:-master}"
base_remote_branch="${3:-master}"

set +e

if grep -r --extended-regexp '^ *class [^\(]+(\(\))?:' whylog/; then
    echo "old-style class detected!"
fi

if grep -r --extended-regex '\b(all|any|filter|map|reduce)\(\[' whylog/; then
    echo "improper use of function and list comprenension! (use a generator expression instead of list comprehension)"
fi

if grep -r '\_\_metaclass\_\_' whylog/; then
    echo "improper declaration of metaclass detected! (use six for that)"
fi

if grep -r 'isinstance(' whylog/; then
    echo "isinstance detected! (check behavior, not identity)"
fi

if [ "$(<.git/refs/heads/${base_branch})" != "$(<.git/refs/remotes/${base_remote}/${base_remote_branch})" ]; then
    echo """running yapf in full mode, because an assumption that master and origin/master are the same, is broken. To fix it, do this:
git checkout master
git pull --ff-only

then checkout your topic branch and run $0.
If the base branch on github is not called 'origin', invoke as $0 proper_origin_remote_name. Then your remote needs to be synched with your master too.
"""
    yapf --in-place --recursive .
else
    echo 'running yapf in incremental mode'
    head=`mktemp`
    master=`mktemp`
    git rev-list --first-parent HEAD > "$head"  # list of commits being a history of HEAD branch, but without commits merged from master after forking
    git rev-list origin/master > "$master"  # list of all commits on history of master

    base_commit=`diff -u "$head" "$master" | grep '^ ' | head -n 1 | cut -c 2-`  # the commit from which the master and topic (current) branch have diverged

    # in below case, it would be E
    #
    #        A---B---C---I---K---L topic
    #       /       /       /
    #  D---E---F---G-------H---J master
    #

    # this doesn't seem to work, so we are going to try something else and see if it works better TODO cleanup
    #changed_files=`git diff --name-only "${base_commit}..HEAD"`
    changed_files=`git diff --name-only "$(git rev-parse --abbrev-ref HEAD)..${base_remote}/${base_remote_branch}"`
    dirty_files=`git ls-files -m`
    files_to_check="$((echo "$changed_files"; echo "$dirty_files") | grep '\.py$' | sort -u)"
    if [ -z "$files_to_check" ]; then
        echo 'nothing to run yapf on after all'
    else
        echo -n 'running yapf... '

        echo "$files_to_check" | (while read file
        do
            yapf --in-place "$file" &
        done
        wait
        )

        echo 'done'
    fi
fi

isort --order-by-type --recursive --line-width 100 --diff --verbose -y
pyflakes .
echo 'SUCCESS!'
