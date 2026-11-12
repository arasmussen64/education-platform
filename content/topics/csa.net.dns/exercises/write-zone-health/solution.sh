# The reference zone-health. cat > FILE <<'EOF' writes every line up to
# EOF into the file, exactly as typed (a learner uses nano).
mkdir -p ~/bin
cat > ~/bin/zone-health <<'EOF'
#!/bin/bash
# zone-health ZONE: are ZONE's name servers in step? Run it on a machine
# with a network: on office ~/bin/zone-health shop.test
zone=$1
# 1. Ask test.'s server, without recursion, who ZONE is delegated to: the
# referral's AUTHORITY section names the servers, and its ADDITIONAL
# section gives their addresses (the glue).
referral=$(dig +norecurse +noall +authority +additional @198.51.100.12 "$zone" NS)
servers=$(echo "$referral" | awk '$4 == "NS" {print $5}' | sort)
# 2. Ask each server, without recursion, for ZONE's SOA: an answer with
# the aa flag is the zone's own; anything else (REFUSED, a referral, no
# answer) isn't.
authoritative=0
total=0
serials=""
for name in $servers; do
  address=$(echo "$referral" | awk -v n="$name" '$1 == n && $4 == "A" {print $5}')
  total=$((total + 1))
  if dig +norecurse +time=2 +tries=1 @"$address" "$zone" SOA | grep '^;; flags:.* aa' > /dev/null; then
    serial=$(dig +norecurse +time=2 +tries=1 +short @"$address" "$zone" SOA | awk '{print $3}')
    echo "$name $address serial $serial"
    authoritative=$((authoritative + 1))
    serials="$serials $serial"
  else
    echo "$name $address not authoritative"
  fi
done
# 3. The verdict.
if [ "$authoritative" -ne "$total" ]; then
  echo broken
elif [ "$(echo $serials | tr ' ' '\n' | sort -u | wc -l)" -eq 1 ]; then
  echo "in sync"
else
  echo "out of sync"
fi
EOF
chmod +x ~/bin/zone-health
on office ~/bin/zone-health shop.test
