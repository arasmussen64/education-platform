# Wrong: dig without +short prints its whole report, header, question and
# answer sections, where one address was wanted.
cat > ~/bin/net-report <<'EOF'
#!/bin/bash
echo "address on eth1: $(ip -4 -br addr show eth1 | awk '{print $3}' | cut -d/ -f1)"
echo "default gateway: $(ip route | awk '/^default/ {print $3}')"
echo "listening tcp ports: $(ss -ltn | awk 'NR > 1 {n = split($4, a, ":"); print a[n]}' | sort -un | paste -sd' ')"
echo "shop.internal resolves to: $(dig +noall +answer shop.internal)"
echo "shop-api answers: $(curl -s -o /dev/null -w '%{http_code}' http://shop.internal:8080/)"
EOF
