# Wrong: the last step uses 10.20.4.1/23, which is already in an aligned
# /23 (4 is a multiple of 2), so the kernel's route is 10.20.4.0/23 and
# nothing moved: moved.txt doesn't show the block being shifted. The rest
# of the walkthrough is done.
mkdir -p ~/bin ~/example
cat > ~/bin/cidr-lib.sh << 'EOF'
ip2int() { local a b c d; IFS=. read -r a b c d <<< "$1"; echo $(( (a << 24) | (b << 16) | (c << 8) | d )); }
int2ip() { echo "$(( $1 >> 24 & 255 )).$(( $1 >> 16 & 255 )).$(( $1 >> 8 & 255 )).$(( $1 & 255 ))"; }
EOF
for z in 0 1 2; do echo "zone-$z 10.20.$((z * 16)).0/20"; done > ~/example/plan.txt
on h1 ip addr add 10.20.1.10/16 dev eth0
on h1 ip addr del 10.20.1.10/24 dev eth0
on h1 ping -c 1 -W 3 10.20.2.10 || true
on h1 ip neigh > ~/example/neigh.txt
sudo netlab restart
on r1 ip addr add 10.20.4.1/23 dev lanc
on r1 ip route > ~/example/moved.txt
on r1 ip addr del 10.20.4.1/23 dev lanc
