# Wrong: the default line is skipped, as if "default" weren't a route, so
# an address only the default route holds gets "no route".
cat > ~/bin/next-hop << 'EOF'
#!/bin/bash
# next-hop TABLE ADDRESS...: the route for each address.
set -euo pipefail

to_number() {
  local a b c d
  IFS=. read -r a b c d <<< "$1"
  number=$(((a << 24) | (b << 16) | (c << 8) | d))
}

table=$1
shift
for address in "$@"; do
  to_number "$address"
  wanted=$number
  best=-1
  answer="no route"
  while read -r -a word; do
    [ "${#word[@]}" -gt 0 ] || continue
    [ "${word[0]}" != default ] || continue
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
    [[ $prefix == */* ]] || prefix=$prefix/32
    length=${prefix#*/}
    to_number "${prefix%/*}"
    if (((wanted >> (32 - length)) == (number >> (32 - length)) && length > best)); then
      best=$length
      answer=$action
    fi
  done < "$table"
  echo "$address $answer"
done
EOF
chmod +x ~/bin/next-hop
