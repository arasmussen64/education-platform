# Wrong: any retransmit read as no answer, but a tunnel can come up after a
# lost packet is sent again.
cat > ~/bin/ike-diagnose << 'EOF'
#!/bin/bash
log=$1
if [[ ! -r $log ]]; then
  echo "ike-diagnose: can't read ${log:-a log}" >&2
  exit 1
fi
has() { grep -F -- "$1" "$log" > /dev/null; }
if has 'retransmit'; then
  echo 'no answer from the peer'
elif has 'CHILD_SA rekeying failed'; then
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
fi
EOF
chmod +x ~/bin/ike-diagnose
