#! /bin/sh -e
cd `dirname $0`/instance
if [ ! -d .git ]
	then
	echo "Instance directory is not a Git repository."
	exit 1
	fi
git add -A
git commit -a -m 'auto commit'
git push
