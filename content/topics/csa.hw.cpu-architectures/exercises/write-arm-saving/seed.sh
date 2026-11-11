#!/bin/bash
# Lays down the write exercise: the dated price file and its README where
# the prompt says, a second file of made-up prices the prompt doesn't name,
# the checks' helper, and the price file's checksum, so the checks can tell
# it hasn't been edited.
set -euo pipefail
here=/usr/local/lib/lab

mkdir -p /srv/prices /usr/local/share/lab /usr/local/libexec/lab
cp "$here/2026-11.csv" "$here/README.txt" /srv/prices/
chmod 644 /srv/prices/2026-11.csv /srv/prices/README.txt
cp "$here/prices-test.csv" /usr/local/share/lab/prices-test.csv
cp "$here/check-saving" /usr/local/libexec/lab/check-saving
chmod 755 /usr/local/libexec/lab/check-saving
sha256sum /srv/prices/2026-11.csv > /usr/local/share/lab/prices.sha256

mkdir -p /home/learner/bin
chown learner:learner /home/learner/bin
