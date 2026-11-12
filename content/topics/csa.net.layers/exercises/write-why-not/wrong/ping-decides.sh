# Wrong: a ping that isn't answered is taken to mean the next hop never
# answered ARP. But a firewall can drop ping (srv's does, and so do the
# check's machines), so an open port is reported as no-arp.
mkdir -p ~/bin
cat > ~/bin/why-not <<'EOF'
#!/bin/bash
host=$1
port=$2
if ! ping -c 1 -W 1 "$host" > /dev/null 2>&1; then
  echo no-arp
  exit 0
fi
start=$(date +%s%N)
if nc -z -w 2 "$host" "$port" 2> /dev/null; then
  echo open
  exit 0
fi
ms=$((($(date +%s%N) - start) / 1000000))
if [ "$ms" -ge 1500 ]; then
  echo dropped
else
  echo refused
fi
EOF
chmod +x ~/bin/why-not
