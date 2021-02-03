#! /bin/sh -e
cd `dirname $0`/instance
git add -A
git commit -a -m 'auto commit'
git push
