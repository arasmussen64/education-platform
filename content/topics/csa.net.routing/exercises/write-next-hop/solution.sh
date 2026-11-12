# The reference: ~/bin/next-hop, written whole with cat > FILE <<'EOF',
# which writes the lines up to EOF into the file, then made executable.
# For each address it reads every line of the table, keeps the matching
# route with the longest prefix, and prints what that route does.
cat > ~/bin/next-hop << 'EOF'
#!/bin/bash
# next-hop TABLE ADDRESS...: for each address, the route the kernel would
# choose from TABLE, a routing table as "ip route" prints it. The longest
# prefix that holds the address wins; the order of the lines doesn't matter.
set -euo pipefail

# to_number ADDRESS: sets $number to the address as one 32-bit number, each
# octet moved to its place (IPv4 and CIDR's ip2int, without a subshell).
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
    # Where the prefix is, and what the route does with a packet.
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
    # A prefix written without a length is a single address: a /32.
    [[ $prefix == */* ]] || prefix=$prefix/32
    length=${prefix#*/}
    to_number "${prefix%/*}"
    # In the block when the first LENGTH bits agree: shift the rest away.
    if (((wanted >> (32 - length)) == (number >> (32 - length)) && length > best)); then
      best=$length
      answer=$action
    fi
  done < "$table"
  echo "$address $answer"
done
EOF
chmod +x ~/bin/next-hop
~/bin/next-hop ~/tables/branch.txt 10.40.9.20 10.40.13.1 10.40.12.7 10.99.3.4 172.16.0.1
