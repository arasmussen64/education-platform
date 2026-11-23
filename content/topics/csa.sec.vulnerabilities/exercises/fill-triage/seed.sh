#!/bin/bash
# The scenery for "Finish triage": the learner's half-written script in
# ~/bin, and a week to try it on in ~/week: the payments server's seven real
# findings as the scanner's helper prints them (captured on the pay base,
# 2026-11-22), with the lab's EPSS and KEV extracts. The two CSV files beside
# this one are byte-for-byte copies of the pay base's (a plain lab can't
# read a base's files): EPSS, by FIRST.org and Empirical Security, scores of
# 2026-11-10 (no licence stated; shipped as a small extract with this
# attribution), and CISA's KEV catalog version 2026.11.10 (CC0 1.0).
# SOURCES.md in content/lab-bases/pay/data/ has the detail.
set -euo pipefail
mkdir -p /home/learner/bin /home/learner/week
cp /usr/local/lib/lab/triage.starter /home/learner/bin/triage
chmod 755 /home/learner/bin/triage
cp /usr/local/lib/lab/epss-2026-11-10.csv /home/learner/week/epss.csv
cp /usr/local/lib/lab/kev-2026.11.10.csv /home/learner/week/kev.csv
finding() { printf '%s\t%s\t%s\t%s\t%s\n' "$@"; }
{
  finding CVE-2024-12084 rsync 3.2.7-1ubuntu1 3.2.7-1ubuntu1.1 9.8
  finding CVE-2024-32487 less 590-2ubuntu2 590-2ubuntu2.1 8.6
  finding CVE-2024-6387 openssh 1:9.6p1-3ubuntu13 1:9.6p1-3ubuntu13.3 8.1
  finding CVE-2025-26465 openssh 1:9.6p1-3ubuntu13 1:9.6p1-3ubuntu13.8 6.8
  finding CVE-2025-32462 sudo 1.9.15p5-3ubuntu5 1.9.15p5-3ubuntu5.24.04.1 8.8
  finding CVE-2025-32463 sudo 1.9.15p5-3ubuntu5 1.9.15p5-3ubuntu5.24.04.1 9.3
  finding CVE-2025-48384 git 1:2.43.0-1ubuntu7 1:2.43.0-1ubuntu7.3 8.0
} > /home/learner/week/findings.tsv
chown -R learner:learner /home/learner/bin /home/learner/week
