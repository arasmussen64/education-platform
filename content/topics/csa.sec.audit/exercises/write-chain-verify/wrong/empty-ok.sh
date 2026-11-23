# Wrong: takes the end of the log to be the anchor until a line says
# otherwise, so a log with every line wiped is reported as "ok 0".
cat > ~/bin/chain-verify << 'EOF'
#!/bin/bash
# chain-verify LOG ANCHOR: is LOG the chained log the auditors last saw?
# ANCHOR is the last line's hash as they hold it.
set -euo pipefail
log=$1
anchor=$2
# The first line chains from 64 zeros.
prev=$(printf '%064d' 0)
last=$anchor
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
  last=$hash
done < "$log"
# Every line chains. Is the end where the auditors left it?
if [ "$last" != "$anchor" ]; then
  echo "anchor mismatch"
  exit 1
fi
echo "ok $n"
EOF
chmod +x ~/bin/chain-verify
