#!/bin/bash
# The scenery for "Due dates from a policy": an empty ~/bin for the
# learner's script, and a small week to try it on in ~/week: five made-up
# findings on three made-up assets, and the shop's policy table (CISA's
# BOD 26-04, Table 1, read 2026-11-22).
set -euo pipefail
mkdir -p /home/learner/bin /home/learner/week
cp /usr/local/lib/lab/policy.tsv /home/learner/week/policy.tsv
line() { printf '%s' "$1"; shift; printf '\t%s' "$@"; printf '\n'; }
{
  line web-1 yes
  line ledger no
  line kiosk yes
} > /home/learner/week/assets.tsv
{
  line CVE-2099-1001 web-1 2026-11-13 2026-03-02 no total
  line CVE-2099-1002 web-1 2026-11-13 - yes partial
  line CVE-2099-1003 ledger 2026-10-30 2026-11-20 no partial
  line CVE-2099-1004 ledger 2026-10-30 - no total
  line CVE-2099-1005 kiosk 2026-12-30 - yes total
} > /home/learner/week/findings.tsv
chown -R learner:learner /home/learner/bin /home/learner/week
