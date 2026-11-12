# Wrong: a script written for shop.test alone. It always asks ns1 and ns2,
# whatever zone it is given, so it is right only for the zone it was tried
# on.
mkdir -p ~/bin
cat > ~/bin/zone-health <<'EOF'
#!/bin/bash
zone=$1
s1=$(dig +norecurse +short @198.51.100.13 "$zone" SOA | awk '{print $3}')
s2=$(dig +norecurse +short @198.51.100.14 "$zone" SOA | awk '{print $3}')
echo "ns1.shop.test. 198.51.100.13 serial $s1"
echo "ns2.shop.test. 198.51.100.14 serial $s2"
if [ "$s1" = "$s2" ]; then echo "in sync"; else echo "out of sync"; fi
EOF
chmod +x ~/bin/zone-health
