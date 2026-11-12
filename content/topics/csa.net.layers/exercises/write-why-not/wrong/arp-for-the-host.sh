# Wrong: the neighbour table is asked about HOST itself, even when HOST is
# behind the router. ARP never crosses a router: the office asks for r1's
# MAC, never for far's, so every host behind r1 is reported as no-arp.
mkdir -p ~/bin
cat > ~/bin/why-not <<'EOF'
#!/bin/bash
host=$1
port=$2
ping -c 1 -W 1 "$host" > /dev/null 2>&1
state=$(ip neigh show "$host" | awk '{print $NF}')
if [ -z "$state" ] || [ "$state" = FAILED ] || [ "$state" = INCOMPLETE ]; then
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
