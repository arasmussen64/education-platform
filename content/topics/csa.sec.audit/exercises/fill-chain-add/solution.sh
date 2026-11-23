# The reference: the four gaps filled in, here by writing the whole script
# again with cat > FILE << 'EOF', which writes the lines up to EOF into the
# file exactly as they stand (in the lab you'd fill the gaps with nano).
#   1. tail -n 1: the hash to chain from is the LAST line's.
#   2. $genesis: an empty log chains from 64 zeros.
#   3. printf '%s %s': the previous hash, one space, the record, and no line
#      break, with the record as data, never as printf's format.
#   4. '%s %s\n': the line written is the hash, one space, the record.
cat > ~/bin/chain-add << 'EOF'
#!/bin/bash
# chain-add LOG RECORD [MORE RECORDS]: adds each record to the chained log.
# Every line of LOG is a hash, one space, and a record. The hash is the
# SHA-256 of the line before's hash, a space and this line's record, so
# each line is made through the one before it.
set -euo pipefail
log=$1
shift
# The first line has no line before it: its "previous hash" is 64 zeros.
genesis=$(printf '%064d' 0)
for record in "$@"; do
  if [ -s "$log" ]; then
    prev=$(tail -n 1 "$log" | cut -d' ' -f1)
  else
    prev=$genesis
  fi
  hash=$(printf '%s %s' "$prev" "$record" | sha256sum | cut -d' ' -f1)
  printf '%s %s\n' "$hash" "$record" >> "$log"
done
EOF
rm -f ~/audit/audit.log
~/bin/chain-add ~/audit/audit.log "event=login.ok user=ana src=203.0.113.9 outcome=ok"
~/bin/chain-add ~/audit/audit.log "event=refund actor=ana order=42 amount=19.99 outcome=ok" "event=note text=100% done"
cat ~/audit/audit.log
