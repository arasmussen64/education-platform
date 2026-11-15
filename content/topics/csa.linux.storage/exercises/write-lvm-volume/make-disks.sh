#!/bin/bash
# The lab's scenery, made at image build: two blank 100 MB disks (disks.sh
# makes the image files at the lab machine's first boot), LVM told to look
# only at the lab's disks, and six films of 20 MB waiting in the learner's
# home, in two batches. A film's bytes are worked out from its number, so
# the checks can work the same bytes out again and compare.
set -euo pipefail
mkdir -p /var/lib/lab /etc/lab
printf 'disk1 100M\ndisk2 100M\n' > /etc/lab/disks.conf

# LVM uses only the disks labelled under /dev/lab/ (so it never touches
# Docker's disks or another lab's), and calls them by those names.
conf=/etc/lvm/lvm.conf
sed -i -E '0,/^(\s*)# filter = \[ "a\|\.\*\|" \]/s//\1filter = [ "a|^\/dev\/lab\/|", "r|.*|" ]/' "$conf"
sed -i -E '0,/^(\s*)# preferred_names = .*/s//\1preferred_names = [ "^\/dev\/lab\/" ]/' "$conf"
grep -E '^\s*filter = \[ "a\|\^/dev/lab/\|", "r\|\.\*\|" \]' "$conf" > /dev/null
grep -E '^\s*preferred_names = \[ "\^/dev/lab/" \]' "$conf" > /dev/null

incoming=/home/learner/incoming
mkdir -p "$incoming/batch1" "$incoming/batch2"
for n in 1 2 3 4 5 6; do
  if [ "$n" -le 3 ]; then batch=batch1; else batch=batch2; fi
  # Not `seq | head`: head leaves early, and with pipefail that is an error.
  head -c 20M < <(seq "${n}000000" "${n}9999999") > "$incoming/$batch/film-$n.mp4"
done
chown -R learner:learner "$incoming"
