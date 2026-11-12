# Wrong: each server's SOA is asked for without @address, so every question
# goes to the office's resolver instead. Its answers come from its cache
# (one serial, whichever server it happened to ask) and never carry the aa
# flag.
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
  if dig "$zone" SOA | grep '^;; flags:.* aa' > /dev/null; then
    serial=$(dig +short "$zone" SOA | awk '{print $3}')
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
