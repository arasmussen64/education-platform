# The reference script, written in one go; in the lab you'd use nano.
# "cat > FILE <<'EOF'" writes the lines up to EOF into FILE.
mkdir -p ~/bin
cat > ~/bin/why-not <<'EOF'
#!/bin/bash
# Usage: why-not HOST PORT
# Why a TCP connection from this machine to HOST:PORT works or doesn't,
# in one word, testing from the bottom layer up:
#   no-arp   the next hop never answered ARP (layer 2)
#   refused  something sent a reset straight back (layer 4: nothing listens)
#   dropped  nothing came back within 2 seconds (a firewall, usually)
#   open     the connection was made
host=$1
port=$2

# Layer 2. The next hop is the gateway when the route to HOST goes "via"
# one, and HOST itself when it's on this machine's own network.
hop=$(ip route get "$host" | awk '{for (i = 1; i < NF; i++) if ($i == "via") print $(i + 1)}')
if [ -z "$hop" ]; then
  hop=$host
fi
# A ping makes the kernel ask ARP for the next hop, whether or not the ping
# itself is answered (a firewall may drop it). Then the neighbour table says
# whether the next hop answered.
ping -c 1 -W 1 "$host" > /dev/null 2>&1
state=$(ip neigh show "$hop" | awk '{print $NF}')
if [ -z "$state" ] || [ "$state" = FAILED ] || [ "$state" = INCOMPLETE ]; then
  echo no-arp
  exit 0
fi

# Layer 4. nc says nothing either way without -v, so time it: a reset
# comes back in milliseconds, a drop takes the whole 2-second wait.
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
on office ~/bin/why-not 10.0.7.20 80
on office ~/bin/why-not 10.0.7.20 22
on office ~/bin/why-not 10.0.7.20 3306
on office ~/bin/why-not 10.0.7.200 80
on office ~/bin/why-not 10.0.9.30 5432
