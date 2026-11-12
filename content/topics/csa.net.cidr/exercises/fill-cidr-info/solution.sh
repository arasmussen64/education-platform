# The reference fill: the whole script, written in one go with
# cat > FILE << 'EOF', which writes the lines up to EOF into FILE (in the
# lab you'd fill the gaps with nano). The four filled lines are the mask,
# the network and the last address, and the two clouds' numbers in the case.
cat > ~/bin/cidr-info << 'EOF'
#!/bin/bash
# cidr-info ADDRESS/PREFIX [aws|azure|google]: the block an address is in,
# and how many of its addresses a machine can be given. It prints:
#   network A        the block's first address
#   last A           its last address
#   addresses N      how many addresses the block holds
#   usable N         how many of them a machine can be given: with no cloud,
#                    the classic count, which keeps back the first and the
#                    last; a cloud keeps back more
#   first-usable A   the first address a machine can be given
set -euo pipefail

ip2int() { local a b c d; IFS=. read -r a b c d <<< "$1"; echo $(( (a << 24) | (b << 16) | (c << 8) | d )); }
int2ip() { echo "$(( $1 >> 24 & 255 )).$(( $1 >> 16 & 255 )).$(( $1 >> 8 & 255 )).$(( $1 & 255 ))"; }

address=${1%/*}
prefix=${1#*/}
cloud=${2:-classic}
n=$(ip2int "$address")

# The mask: prefix ones, then zeros, as one 32-bit number.
mask=$(( (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF ))
# The wildcard: the mask with every bit flipped.
wildcard=$(( ~mask & 0xFFFFFFFF ))
# The block's first address keeps the address's network bits and clears
# its host bits; its last address sets every host bit.
network=$(( n & mask ))
last=$(( network | wildcard ))
size=$(( last - network + 1 ))

# How many addresses of a block are kept back, and how far into the block
# the first one a machine can be given is.
case $cloud in
  aws | azure) kept=5; first=4 ;;
  google) kept=4; first=2 ;;
  classic) kept=2; first=1 ;;
  *) echo "cidr-info: the cloud is aws, azure or google, not $cloud" >&2; exit 2 ;;
esac

echo "network $(int2ip "$network")"
echo "last $(int2ip "$last")"
echo "addresses $size"
echo "usable $(( size - kept ))"
echo "first-usable $(int2ip $(( network + first )))"
EOF

# Try it: an AWS /26, and the same address with no cloud.
~/bin/cidr-info 10.20.30.77/26 aws
~/bin/cidr-info 10.20.30.77/26
