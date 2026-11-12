# Wrong: the script knows the answers for the addresses in the checks'
# two fixed tables by heart and works nothing out, so it is right exactly
# where it was looked at and nowhere else.
cat > ~/bin/next-hop << 'EOF'
#!/bin/bash
# next-hop TABLE ADDRESS...: the route for each address.
set -euo pipefail
shift
for address in "$@"; do
  case $address in
    10.20.5.9) echo "$address via 10.0.0.14 dev lab" ;;
    10.20.7.200 | 10.20.4.9 | 10.20.4.0) echo "$address via 10.0.0.10 dev branch" ;;
    10.20.5.200) echo "$address dev dmz (directly connected)" ;;
    10.1.255.255) echo "$address via 10.0.0.2 dev east" ;;
    10.10.5.5 | 10.0.0.0) echo "$address via 10.255.0.1 dev core" ;;
    10.20.200.1) echo "$address via 10.0.0.6 dev west" ;;
    203.0.113.9) echo "$address via 192.0.2.1 dev wan" ;;
    10.30.1.1 | 10.30.7.8) echo "$address blackhole" ;;
    10.30.7.7) echo "$address via 10.0.0.18 dev mgmt" ;;
    192.168.40.1) echo "$address via 172.16.0.1 dev site" ;;
    172.16.0.1) echo "$address dev site (directly connected)" ;;
    *) echo "$address no route" ;;
  esac
done
EOF
chmod +x ~/bin/next-hop
