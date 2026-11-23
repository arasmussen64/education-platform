#!/bin/bash
# The scenery for "Finish the chain": the script with its four gaps, and a
# folder for the log the prompt has the learner make.
set -euo pipefail
mkdir -p /home/learner/bin /home/learner/audit
cat > /home/learner/bin/chain-add << 'STARTER'
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
    prev=$(... "$log" | cut -d' ' -f1)
  else
    prev=...
  fi
  hash=$(printf ... "$prev" "$record" | sha256sum | cut -d' ' -f1)
  printf ... "$hash" "$record" >> "$log"
done
STARTER
chmod +x /home/learner/bin/chain-add
chown -R learner:learner /home/learner
