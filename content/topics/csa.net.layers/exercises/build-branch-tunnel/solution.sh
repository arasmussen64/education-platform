# The reference build. "on r3 tee FILE << 'EOF'" writes the lines up to EOF
# into r3's FILE, as saving it in nano would.

# 1. How big a packet the internet path from r3 to r2 carries: tracepath
#    learns 1400 at the ISP's router. GRE needs 24 bytes of it (a 20-byte
#    outer IPv4 header and a 4-byte GRE header), so the tunnel's MTU is 1376.
on r3 tracepath -n 203.0.113.2

# 2. r3's network file: its addresses and its line to the ISP as before,
#    then the tunnel to r2's address on the internet, r3's end of it, its
#    MTU, and a route that sends only the cloud's network into it.
on r3 tee /etc/network/up > /dev/null << 'EOF'
# r3's network settings, run at every boot: the branch's router.
ip addr add 10.0.5.1/24 dev eth0
ip addr add 198.51.100.6/30 dev wan
# The branch's line to its ISP: everything not on the branch's own network
# goes there.
ip route add default via 198.51.100.5
# The tunnel to the cloud's router, r2, across the internet. Its MTU is the
# path's 1400 less GRE's 24 bytes.
ip link add gre1 type gre local 198.51.100.6 remote 203.0.113.2 ttl 64
ip addr add 10.255.1.2/30 dev gre1
ip link set gre1 mtu 1376
ip link set gre1 up
# Only the cloud's network goes through the tunnel.
ip route add 10.0.2.0/24 dev gre1
EOF

# 3. r3's firewall. From anywhere but the branch and the tunnel, only the
#    tunnel's own packets from r2 and what belongs to known connections get
#    in: "related" covers the ICMP messages about them, such as the ISP's
#    "fragmentation needed", which path MTU discovery needs. Forwarded: the
#    branch's machines and the cloud may start connections; the internet
#    may not.
on r3 tee /etc/nftables.conf > /dev/null << 'EOF'
#!/usr/sbin/nft -f
# r3's firewall: the branch's router, on the internet.
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
sudo systemctl enable nftables@r3

# 4. Everything built again from the files, as a reboot would, then a
#    look: the price list from the branch, and one packet captured on r3's
#    internet side, the outer GRE header with the branch's packet inside.
sudo netlab restart
on branch curl -s -o /dev/null -w '%{size_download} bytes\n' http://10.0.2.20/pricelist.csv
mkdir -p ~/build
on r3 timeout 5 tcpdump -nn -c 1 -i wan ip proto 47 > ~/build/tunnel.txt &
sleep 1; on branch ping -c 1 10.0.2.20 > /dev/null; wait
cat ~/build/tunnel.txt
