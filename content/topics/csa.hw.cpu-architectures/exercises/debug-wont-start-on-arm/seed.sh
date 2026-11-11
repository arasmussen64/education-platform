#!/bin/bash
# Lays down the debug: the release folder with its recipe and the program's
# source, the release as the recipe builds it today, what the self-test
# prints when the program runs correctly, and the source's checksum.
set -euo pipefail
here=/usr/local/lib/lab
release=/srv/release

mkdir -p "$release/src"
cp "$here/build.sh" "$release/build.sh"
cp "$here/shop-resize.c" "$release/src/shop-resize.c"
chmod 755 "$release/build.sh"
"$release/build.sh"

# What the self-test prints when the program runs correctly, from a plain
# build for this machine.
mkdir -p /usr/local/share/lab
work=$(mktemp -d)
gcc -O2 -o "$work/shop-resize" "$release/src/shop-resize.c"
"$work/shop-resize" --selftest > /usr/local/share/lab/selftest.txt
rm -r "$work"
(cd "$release/src" && sha256sum shop-resize.c) > /usr/local/share/lab/src.sha256

chown -R learner:learner "$release"
