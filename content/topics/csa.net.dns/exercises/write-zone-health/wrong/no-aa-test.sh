# Wrong: every server is taken to be authoritative, aa flag or not. A
# server that refuses the zone gives no serial, and the script prints an
# empty one instead of "not authoritative".
mkdir -p ~/bin
cat > ~/bin/zone-health <<'EOF'
#!/bin/bash
zone=$1
referral=$(dig +norecurse +noall +authority +additional @198.51.100.12 "$zone" NS)
servers=$(echo "$referral" | awk '$4 == "NS" {print $5}' | sort)
serials=""
for name in $servers; do
  address=$(echo "$referral" | awk -v n="$name" '$1 == n && $4 == "A" {print $5}')
  serial=$(dig +norecurse +time=2 +tries=1 +short @"$address" "$zone" SOA | awk '{print $3}')
  echo "$name $address serial $serial"
  serials="$serials $serial"
done
if [ "$(echo $serials | tr ' ' '\n' | sort -u | wc -l)" -eq 1 ]; then
  echo "in sync"
else
  echo "out of sync"
fi
EOF
chmod +x ~/bin/zone-health
