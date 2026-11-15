# Wrong: every answer is right, but nc's HOST and PORT are used without
# quotes, which ShellCheck points out (SC2086), and the script was left
# that way.
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
start=$(date +%s%N)
if nc -z -w 2 $host $port 2> /dev/null; then
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
