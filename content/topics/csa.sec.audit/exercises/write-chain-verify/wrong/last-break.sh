# Wrong: carries on after a line that doesn't fit and reports the last
# such line, not the first.
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
    broken=$n
  fi
  prev=$hash
done < "$log"
if [ -n "${broken:-}" ]; then
  echo "broken at line $broken"
  exit 1
fi
# Every line chains. Is the end where the auditors left it?
if [ "$prev" != "$anchor" ]; then
  echo "anchor mismatch"
  exit 1
fi
echo "ok $n"
EOF
chmod +x ~/bin/chain-verify
