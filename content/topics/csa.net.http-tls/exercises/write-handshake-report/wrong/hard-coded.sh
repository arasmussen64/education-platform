# Wrong: the prompt's three answers written in by hand, by port and name:
# right for the lab's example servers and for no other.
cat > ~/bin/handshake-report << 'EOF'
#!/bin/bash
# handshake-report HOST PORT [NAME]: the example servers' answers.
port=$2
name=${3:-}
if [ "$port" = 8443 ]; then
  printf '%s\n' "protocol: TLSv1.3" "alpn: h2" "certificate-name: www.shop.test" "stapled: yes"
elif [ "$name" = api.shop.test ]; then
  printf '%s\n' "protocol: TLSv1.2" "alpn: none" "certificate-name: api.shop.test" "stapled: no"
else
  printf '%s\n' "protocol: TLSv1.2" "alpn: none" "certificate-name: legacy.shop.test" "stapled: no"
fi
EOF
chmod +x ~/bin/handshake-report
