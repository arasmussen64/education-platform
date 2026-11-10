# The finished report. In the lab you'd fill the five gaps with nano; here
# it's written in one go.
cat > ~/bin/net-report <<'EOF'
#!/bin/bash
# Usage: net-report
# Where this server is on the network, what it offers, and whether the
# shop's API answers.
echo "address on eth1: $(ip -4 -br addr show eth1 | awk '{print $3}' | cut -d/ -f1)"
echo "default gateway: $(ip route | awk '/^default/ {print $3}')"
echo "listening tcp ports: $(ss -ltn | awk 'NR > 1 {n = split($4, a, ":"); print a[n]}' | sort -un | paste -sd' ')"
echo "shop.internal resolves to: $(dig +short shop.internal)"
echo "shop-api answers: $(curl -s -o /dev/null -w '%{http_code}' http://shop.internal:8080/)"
EOF
~/bin/net-report
