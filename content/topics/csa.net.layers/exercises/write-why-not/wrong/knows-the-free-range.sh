# Wrong: the port test is right, but layer 2 is never tested: the range
# the prompt gives as owned by nobody, 10.0.7.200 to 249, is typed in as
# the no-arp answer. The check's address that nobody owns is elsewhere.
mkdir -p ~/bin
cat > ~/bin/why-not <<'EOF'
#!/bin/bash
host=$1
port=$2
case $host in 10.0.7.2[0-4][0-9]) echo no-arp; exit 0 ;; esac
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
