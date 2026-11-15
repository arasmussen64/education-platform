# Wrong: the script is the reference one without its first line,
# #!/bin/bash, so it is left to whatever shell happens to start it, and
# ShellCheck can't tell which shell it is written for (SC2148).
cat > ~/bin/ike-diagnose << 'EOF'
log=$1
if [[ ! -r $log ]]; then
  echo "ike-diagnose: can't read ${log:-a log}: give one log file" >&2
  exit 1
fi
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
