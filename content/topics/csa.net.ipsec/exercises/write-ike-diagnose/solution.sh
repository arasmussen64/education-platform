# The reference ike-diagnose. "cat > FILE << 'EOF'" writes the lines up to
# EOF into FILE, as typing them into nano would; chmod +x makes it a
# program. The order of the tests is the point: a log can hold lines of
# more than one kind (a tunnel that came up and then failed its rekey has
# both), so the most specific outcome is tested first, and "up" and "no
# answer" last.
cat > ~/bin/ike-diagnose << 'EOF'
#!/bin/bash
# ike-diagnose LOGFILE: says in one line what happened in one strongSwan
# log of one connection attempt (journal lines from the initiator).
log=$1
if [[ ! -r $log ]]; then
  echo "ike-diagnose: can't read ${log:-a log}: give one log file" >&2
  exit 1
fi

# has TEXT: the log holds a line with TEXT in it.
has() { grep -F -- "$1" "$log" > /dev/null; }

if has 'CHILD_SA rekeying failed'; then
  echo 'phase 2: rekey failed'
elif has 'received NO_PROPOSAL_CHOSEN notify error'; then
  echo 'phase 1: no proposal chosen'
elif has 'received AUTHENTICATION_FAILED notify error'; then
  echo 'phase 1: authentication failed'
elif has 'received NO_PROPOSAL_CHOSEN notify, no CHILD_SA built'; then
  echo 'phase 2: no proposal chosen'
elif has 'received TS_UNACCEPTABLE notify, no CHILD_SA built'; then
  echo 'phase 2: traffic selectors unacceptable'
elif grep -E 'CHILD_SA .* established' "$log" > /dev/null; then
  echo 'up'
elif has 'retransmit'; then
  echo 'no answer from the peer'
else
  echo 'unknown'
fi
EOF
chmod +x ~/bin/ike-diagnose
for f in ~/logs/*.log; do echo "$f: $(~/bin/ike-diagnose "$f")"; done
