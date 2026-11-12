# Wrong: an established CHILD_SA is taken as the answer before anything
# else is looked for, so a tunnel whose rekey failed an hour later reads
# "up".
cat > ~/bin/ike-diagnose << 'EOF'
#!/bin/bash
log=$1
if [[ ! -r $log ]]; then
  echo "ike-diagnose: can't read ${log:-a log}" >&2
  exit 1
fi
has() { grep -F -- "$1" "$log" > /dev/null; }
if grep -E 'CHILD_SA .* established' "$log" > /dev/null; then
  echo 'up'
elif has 'received NO_PROPOSAL_CHOSEN notify error'; then
  echo 'phase 1: no proposal chosen'
elif has 'received AUTHENTICATION_FAILED notify error'; then
  echo 'phase 1: authentication failed'
elif has 'received NO_PROPOSAL_CHOSEN notify, no CHILD_SA built'; then
  echo 'phase 2: no proposal chosen'
elif has 'received TS_UNACCEPTABLE notify, no CHILD_SA built'; then
  echo 'phase 2: traffic selectors unacceptable'
elif has 'retransmit'; then
  echo 'no answer from the peer'
fi
EOF
chmod +x ~/bin/ike-diagnose
