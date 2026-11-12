# Wrong: the port test is right, but the layer 2 test is missing. For an
# address nobody owns, the kernel's ARP gives up after about 3 seconds,
# by when nc's 2-second wait is over: it is reported as dropped.
mkdir -p ~/bin
cat > ~/bin/why-not <<'EOF'
#!/bin/bash
host=$1
port=$2
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
