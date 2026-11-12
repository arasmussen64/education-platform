# Wrong: a blackhole line isn't in a shape the script knows, so it skips
# it, and an address the blackhole should catch falls through to a
# shorter route that would carry it on.
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
    [ "${word[0]}" != blackhole ] || continue
    prefix=${word[0]}
    if [ "${word[1]:-}" = via ]; then
      action="via ${word[2]} dev ${word[4]}"
    else
      action="dev ${word[2]} (directly connected)"
    fi
    [ "$prefix" != default ] || prefix=0.0.0.0/0
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
