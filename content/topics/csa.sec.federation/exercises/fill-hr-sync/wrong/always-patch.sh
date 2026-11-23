#!/bin/bash
# WRONG: a leaver is switched off again on every run, whether or not
# the account is already off, so a second run still writes.
# The reference fix. A learner fills the five gaps in nano; this makes the
# same five edits with sed, then runs the connector on the shop's staff
# file, twice.
set -e
# 1: the filter. 2: switch a leaver off. 3: a joiner is created active.
# 4 and 5: take a member out of a group, put a member in.
sed -i \
  -e 's|find Users "\.\.\. \\"$username\\""|find Users "userName eq \\"$username\\""|' \
  -e 's|{\\"op\\":\\"\.\.\.\\",\\"path\\":\\"\.\.\.\\",\\"value\\":\\"\.\.\.\\"}|{\\"op\\":\\"replace\\",\\"path\\":\\"active\\",\\"value\\":false}|' \
  -e 's|"\.\.\.": "\.\.\."}|active: true}|' \
  -e 's|{op: "\.\.\.", path: ("members\[value eq|{op: "remove", path: ("members[value eq|' \
  -e 's|{op: "\.\.\.", path: "members", value|{op: "add", path: "members", value|' \
  ~/bin/hr-sync
sed -i 's/ && $(echo "$user" | jq -r .active) == true ]]; then/ ]]; then/' ~/bin/hr-sync
on hr ~/bin/hr-sync /srv/hr/staff.csv
# A second run finds nothing to do, and prints nothing.
on hr ~/bin/hr-sync /srv/hr/staff.csv
