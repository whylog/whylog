#!/bin/bash -ux

base_remote="${1:-origin}"
base_branch="${1:-master}"
base_remote_branch="${1:-master}"

set +e

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

    git diff --name-only "${base_commit}..HEAD" | grep '\.py$' | xargs yapf --in-place setup.py
fi

isort --order-by-type --recursive --line-width 100 --diff --verbose -y
pyflakes .
echo 'SUCCESS!'
