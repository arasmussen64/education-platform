# Wrong: plain curl prints the page the API answers with, where the status
# code was wanted.
cat > ~/bin/net-report <<'EOF'
#!/bin/bash
echo "address on eth1: $(ip -4 -br addr show eth1 | awk '{print $3}' | cut -d/ -f1)"
echo "default gateway: $(ip route | awk '/^default/ {print $3}')"
echo "listening tcp ports: $(ss -ltn | awk 'NR > 1 {n = split($4, a, ":"); print a[n]}' | sort -un | paste -sd' ')"
echo "shop.internal resolves to: $(dig +short shop.internal)"
echo "shop-api answers: $(curl -s http://shop.internal:8080/)"
EOF
