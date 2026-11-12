# Wrong: a server counts as authoritative when its answer's status is
# NOERROR, not when it has the aa flag. A server that refuses the zone is
# caught, but a lame one, which answers NOERROR with a referral elsewhere,
# is taken for the zone's own and printed with an empty serial.
mkdir -p ~/bin
cat > ~/bin/zone-health <<'EOF'
#!/bin/bash
zone=$1
referral=$(dig +norecurse +noall +authority +additional @198.51.100.12 "$zone" NS)
servers=$(echo "$referral" | awk '$4 == "NS" {print $5}' | sort)
authoritative=0
total=0
serials=""
for name in $servers; do
  address=$(echo "$referral" | awk -v n="$name" '$1 == n && $4 == "A" {print $5}')
  total=$((total + 1))
  if dig +norecurse +time=2 +tries=1 @"$address" "$zone" SOA | grep 'status: NOERROR' > /dev/null; then
    serial=$(dig +norecurse +time=2 +tries=1 +short @"$address" "$zone" SOA | awk '{print $3}')
    echo "$name $address serial $serial"
    authoritative=$((authoritative + 1))
    serials="$serials $serial"
  else
    echo "$name $address not authoritative"
  fi
done
if [ "$authoritative" -ne "$total" ]; then
  echo broken
elif [ "$(echo $serials | tr ' ' '\n' | sort -u | wc -l)" -eq 1 ]; then
  echo "in sync"
else
  echo "out of sync"
fi
EOF
chmod +x ~/bin/zone-health
