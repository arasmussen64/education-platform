# The reference: ~/bin/chain-verify, written whole with cat > FILE << 'EOF',
# which writes the lines up to EOF into the file exactly as they stand, then
# made executable and tried on the lab's five example logs. It walks the
# log once, working out each line's hash from the line before's, and stops
# at the first line that doesn't fit; if every line fits, it compares the
# last hash with the anchor, which is what catches a log cut short or
# rewritten from some line on.
cat > ~/bin/chain-verify << 'EOF'
#!/bin/bash
# chain-verify LOG ANCHOR: is LOG the chained log the auditors last saw?
# ANCHOR is the last line's hash as they hold it.
set -euo pipefail
log=$1
anchor=$2
# The first line chains from 64 zeros.
prev=$(printf '%064d' 0)
n=0
# IFS= keeps spaces at the ends of a line and -r keeps backslashes: the
# record must be hashed exactly as it was written.
while IFS= read -r line; do
  n=$((n + 1))
  hash=${line%% *}  # up to the first space
  record=${line#* } # after the first space
  want=$(printf '%s %s' "$prev" "$record" | sha256sum | cut -d' ' -f1)
  if [ "$hash" != "$want" ]; then
    echo "broken at line $n"
    exit 1
  fi
  prev=$hash
done < "$log"
# Every line chains. Is the end where the auditors left it?
if [ "$prev" != "$anchor" ]; then
  echo "anchor mismatch"
  exit 1
fi
echo "ok $n"
EOF
chmod +x ~/bin/chain-verify
cd ~/audit
for log in shop edited deleted cut rewritten; do
  ~/bin/chain-verify "$log.log" "$(cat shop.anchor)" || true
done
