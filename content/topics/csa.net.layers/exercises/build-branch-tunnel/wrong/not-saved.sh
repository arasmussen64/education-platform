# Wrong: everything done with live commands only; r3's files are as they
# were, and nftables@r3 isn't enabled. It works until the next boot.
on r3 ip link add gre1 type gre local 198.51.100.6 remote 203.0.113.2 ttl 64
on r3 ip addr add 10.255.1.2/30 dev gre1
on r3 ip link set gre1 mtu 1376
on r3 ip link set gre1 up
on r3 ip route add 10.0.2.0/24 dev gre1
on r3 nft -f - << 'EOF'
flush ruleset
table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif lo accept
        ct state established,related accept
        iifname "eth0" accept
        iifname "wan" ip saddr 203.0.113.2 ip protocol gre accept
    }
    chain forward {
        type filter hook forward priority filter; policy drop;
        ct state established,related accept
        iifname { "eth0", "gre1" } accept
    }
}
EOF
mkdir -p ~/build
on r3 timeout 5 tcpdump -nn -c 1 -i wan ip proto 47 > ~/build/tunnel.txt &
sleep 1; on branch ping -c 1 10.0.2.20 > /dev/null; wait
