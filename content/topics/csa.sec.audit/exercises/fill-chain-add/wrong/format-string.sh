# Wrong: the record is put inside printf's format, so a % in a record is
# read as an instruction and the hash is of something else.
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
  hash=$(printf "$prev $record" | sha256sum | cut -d' ' -f1)
  printf '%s %s\n' "$hash" "$record" >> "$log"
done
EOF
