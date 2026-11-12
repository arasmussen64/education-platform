# Wrong: every connection that fails is called refused. Without timing
# nc, a drop (nothing for 2 seconds) can't be told from a reset.
mkdir -p ~/bin
cat > ~/bin/why-not <<'EOF'
#!/bin/bash
host=$1
port=$2
hop=$(ip route get "$host" | awk '{for (i = 1; i < NF; i++) if ($i == "via") print $(i + 1)}')
if [ -z "$hop" ]; then
  hop=$host
fi
ping -c 1 -W 1 "$host" > /dev/null 2>&1
state=$(ip neigh show "$hop" | awk '{print $NF}')
if [ -z "$state" ] || [ "$state" = FAILED ] || [ "$state" = INCOMPLETE ]; then
  echo no-arp
  exit 0
fi
if nc -z -w 2 "$host" "$port" 2> /dev/null; then
  echo open
else
  echo refused
fi
EOF
chmod +x ~/bin/why-not
