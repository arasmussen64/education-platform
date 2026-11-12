# Wrong: any NO_PROPOSAL_CHOSEN read as phase 1, though one that arrives
# after the IKE_SA is established (no CHILD_SA built) is phase 2.
cat > ~/bin/ike-diagnose << 'EOF'
#!/bin/bash
log=$1
if [[ ! -r $log ]]; then
  echo "ike-diagnose: can't read ${log:-a log}" >&2
  exit 1
fi
has() { grep -F -- "$1" "$log" > /dev/null; }
if has 'CHILD_SA rekeying failed'; then
  echo 'phase 2: rekey failed'
elif has 'NO_PROPOSAL_CHOSEN'; then
  echo 'phase 1: no proposal chosen'
elif has 'received AUTHENTICATION_FAILED notify error'; then
  echo 'phase 1: authentication failed'
elif has 'received TS_UNACCEPTABLE notify, no CHILD_SA built'; then
  echo 'phase 2: traffic selectors unacceptable'
elif grep -E 'CHILD_SA .* established' "$log" > /dev/null; then
  echo 'up'
elif has 'retransmit'; then
  echo 'no answer from the peer'
fi
EOF
chmod +x ~/bin/ike-diagnose
