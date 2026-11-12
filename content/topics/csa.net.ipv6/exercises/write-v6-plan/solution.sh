# The reference script, written in one go with cat > FILE << 'EOF', which
# writes the lines up to EOF into FILE (in the lab you'd use nano). Then
# it is made executable, run on the prompt's example, and linted.
mkdir -p ~/bin
cat > ~/bin/v6-plan << 'EOF'
#!/bin/bash
# v6-plan PREFIX REGIONS ZONES TIERS: one /64 for every region, zone and
# tier of a site, from the site's /48 written short (2001:db8:abcd::/48).
# The subnet's fourth group is one hex digit of region, one of zone and two
# of tier: region 1, zone 3, tier 10 is 130a.
set -euo pipefail

# The prefix's first three groups: 2001:db8:abcd::/48 loses its /48, then
# its ::, and what's left splits at its colons. A group left out of a short
# form (2001:db8::/48 has no third) comes out empty, and is 0.
p=${1%/*}
p=${p%::}
IFS=: read -r g1 g2 g3 <<< "$p"

for (( r = 0; r < $2; r++ )); do
  for (( z = 0; z < $3; z++ )); do
    for (( t = 0; t < $4; t++ )); do
      # The fourth group as a number: in hex the digits are worth 4096,
      # 256, 16 and 1, so the region goes in the 4096s, the zone in the
      # 256s and the tier in the last two digits. printf %x writes it in
      # hex, in lower case, with no leading zeros.
      group=$(printf '%x' "$(( r * 4096 + z * 256 + t ))")
      s="$g1:${g2:-0}:${g3:-0}:$group:0:0:0:0"
      # The last four groups are always zero, so the longest run of zeros
      # is always the one at the end: take the zero groups off the end and
      # write :: in their place. A zero group before a non-zero one stays.
      while [[ $s == *:0 ]]; do s=${s%:0}; done
      printf 'r%x-z%x-t%02x %s::/64\n' "$r" "$z" "$t" "$s"
    done
  done
done
EOF
chmod +x ~/bin/v6-plan
~/bin/v6-plan 2001:db8:abcd::/48 2 2 3
shellcheck ~/bin/v6-plan && echo "shellcheck: quiet"
