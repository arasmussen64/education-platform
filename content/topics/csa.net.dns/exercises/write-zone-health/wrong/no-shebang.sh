# Wrong: the script works when run as "bash ~/bin/zone-health", but its
# first line isn't #!/bin/bash, so run on its own it is left to whatever
# shell happens to start it.
mkdir -p ~/bin
cat > ~/bin/zone-health <<'EOF'
zone=$1
referral=$(dig +norecurse +noall +authority +additional @198.51.100.12 "$zone" NS)
servers=$(echo "$referral" | awk '$4 == "NS" {print $5}' | sort)
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
if [ "$authoritative" -ne "$total" ]; then
  echo broken
elif [ "$(echo $serials | tr ' ' '\n' | sort -u | wc -l)" -eq 1 ]; then
  echo "in sync"
else
  echo "out of sync"
fi
EOF
chmod +x ~/bin/zone-health
