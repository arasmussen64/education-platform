# Wrong: the message is taken as everything from the sixth word on, which
# is right for journalctl's usual lines (month, day, time, host, program)
# and wrong for lines with full dates (journalctl -o short-iso), where the
# message starts at the fourth word; then each line is compared whole.
cat > ~/bin/ike-diagnose << 'EOF'
#!/bin/bash
log=$1
if [[ ! -r $log ]]; then
  echo "ike-diagnose: can't read ${log:-a log}" >&2
  exit 1
fi
messages=$(cut -d ' ' -f 6- "$log")
is() { grep -xF -- "$1" <<< "$messages" > /dev/null; }
starts() { grep -E -- "^$1" <<< "$messages" > /dev/null; }
if starts 'CHILD_SA rekeying failed'; then
  echo 'phase 2: rekey failed'
elif is 'received NO_PROPOSAL_CHOSEN notify error'; then
  echo 'phase 1: no proposal chosen'
elif is 'received AUTHENTICATION_FAILED notify error'; then
  echo 'phase 1: authentication failed'
elif is 'received NO_PROPOSAL_CHOSEN notify, no CHILD_SA built'; then
  echo 'phase 2: no proposal chosen'
elif is 'received TS_UNACCEPTABLE notify, no CHILD_SA built'; then
  echo 'phase 2: traffic selectors unacceptable'
elif starts 'CHILD_SA .* established'; then
  echo 'up'
elif starts 'retransmit'; then
  echo 'no answer from the peer'
fi
EOF
chmod +x ~/bin/ike-diagnose
