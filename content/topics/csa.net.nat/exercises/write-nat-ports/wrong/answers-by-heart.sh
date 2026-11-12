# Wrong: the script prints the lunchtime listing's answer, from the prompt,
# whatever it is given, so it is right on that one listing and nowhere else.
cat > ~/bin/nat-ports << 'EOF'
#!/bin/bash
# nat-ports FILE PORTS: NAT ports in use per destination, busiest first.
echo "tcp 203.0.113.10:443 10 100% FULL"
echo "udp 203.0.113.53:53 8 80% WARN"
echo "tcp 203.0.113.10:80 4 40%"
echo "tcp 203.0.113.53:53 1 10%"
EOF
chmod +x ~/bin/nat-ports
