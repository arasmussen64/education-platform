echo $((2#11110000)); printf '%d\n' 0xF0
mkdir -p ~/bin ~/example
cat > ~/bin/cidr-lib.sh << 'EOF'
# cidr-lib.sh: IPv4 addresses as numbers. Load it with: . ~/bin/cidr-lib.sh
# ip2int 10.20.30.77 prints the address as one 32-bit number.
ip2int() { local a b c d; IFS=. read -r a b c d <<< "$1"; echo $(( (a << 24) | (b << 16) | (c << 8) | d )); }
# int2ip 169090637 prints a 32-bit number as a dotted address again.
int2ip() { echo "$(( $1 >> 24 & 255 )).$(( $1 >> 16 & 255 )).$(( $1 >> 8 & 255 )).$(( $1 & 255 ))"; }
EOF
. ~/bin/cidr-lib.sh
n=$(ip2int 10.20.30.77); echo "$n"
m=$(( (0xFFFFFFFF << (32 - 27)) & 0xFFFFFFFF )); int2ip "$m"
int2ip $(( n & m ))
int2ip $(( n | (~m & 0xFFFFFFFF) ))
ipcalc -b 10.20.30.77/27
for z in 0 1 2; do echo "zone-$z 10.20.$((z * 16)).0/20"; done | tee ~/example/plan.txt
for s in 0 1 2 3; do echo "zone-0 subnet-$s 10.20.$s.0/24"; done
on h1 ping -c 1 10.20.2.10
on h1 ip addr add 10.20.1.10/16 dev eth0
on h1 ip addr del 10.20.1.10/24 dev eth0
on h1 ip route
on h1 ping -c 1 -W 3 10.20.2.10
on h1 ip neigh | tee ~/example/neigh.txt
sudo netlab restart
on h1 ping -c 1 10.20.2.10
on h1 ip neigh
on r1 ip addr add 10.20.3.1/23 dev lanc
on r1 ip route | tee ~/example/moved.txt
ipcalc -b 10.20.3.1/23
on r1 ip addr del 10.20.3.1/23 dev lanc
