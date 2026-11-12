# Wrong: one bit too few is compared (33 - length shifted away instead of
# 32 - length), so each block looks twice its size: 10.20.4.9 seems to be
# inside 10.20.5.0/24, and a /32 seems to hold two addresses.
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
    to_number "${prefix%/*}"
    if (((wanted >> (33 - length)) == (number >> (33 - length)) && length > best)); then
      best=$length
      answer=$action
    fi
  done < "$table"
  echo "$address $answer"
done
EOF
chmod +x ~/bin/next-hop
