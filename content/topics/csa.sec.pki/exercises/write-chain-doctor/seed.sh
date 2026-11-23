#!/bin/bash
# The scenery of "Chain doctor", made once, when the image is built: six
# example cases in ~/examples, each a folder with leaf.pem, chain.pem,
# root.pem and, where revocation is checked, crls.pem (make-case says how
# each is made), and an empty ~/bin for the script. The examples that have
# "run out" ran out a day before the image was built, and everything else
# lasts ten years, so they give the same answers however old the image is.
set -euo pipefail
ex=/home/learner/examples
mkdir -p "$ex" /home/learner/bin
n=1
for kind in ok wrong-intermediate expired-intermediate path-too-long revoked-leaf crl-missing-root; do
  mkdir -p "$ex/$kind"
  /usr/local/lib/lab/make-case "$kind" "$ex/$kind" "$n" > "$ex/$kind/expected.txt"
  n=$((n + 1))
done
mv "$ex/revoked-leaf" "$ex/revoked"
mv "$ex/crl-missing-root" "$ex/crl-missing"
# What each example should give is the checks' business, kept out of the
# learner's folder.
mkdir -p /usr/local/lib/lab/expected
for d in "$ex"/*/; do
  mv "$d/expected.txt" "/usr/local/lib/lab/expected/$(basename "$d").txt"
done
chown -R learner:learner "$ex" /home/learner/bin
chmod 700 /usr/local/lib/lab
