# Wrong: it compares the text, not the numbers. A prefix's network address
# with its trailing ".0"s taken off is treated as the start of the matching
# addresses, so 10.10.5.5 "starts with" 10.1 and lands in 10.1.0.0/16, and
# a /20 or /22, whose block doesn't end on a dot, is never matched right.
cat > ~/bin/next-hop << 'EOF'
#!/bin/bash
# next-hop TABLE ADDRESS...: the route for each address.
set -euo pipefail

table=$1
shift
for address in "$@"; do
  best=-1
  answer="no route"
  while read -r -a word; do
    [ "${#word[@]}" -gt 0 ] || continue
    if [ "${word[0]}" = blackhole ]; then
      prefix=${word[1]}
      action=blackhole
    elif [ "${word[1]:-}" = via ]; then
      prefix=${word[0]}
      action="via ${word[2]} dev ${word[4]}"
    else
      prefix=${word[0]}
      action="dev ${word[2]} (directly connected)"
    fi
    [ "$prefix" != default ] || prefix=0.0.0.0/0
    [[ $prefix == */* ]] || prefix=$prefix/32
    length=${prefix#*/}
    start=${prefix%/*}
    while [[ $start == *.0 ]]; do start=${start%.0}; done
    [ "$start" != 0 ] || start=""
    if [[ $address == "$start"* ]] && ((length > best)); then
      best=$length
      answer=$action
    fi
  done < "$table"
  echo "$address $answer"
done
EOF
chmod +x ~/bin/next-hop
