# Wrong: r2 is fixed, and instead of letting web hear "fragmentation
# needed", r2 clamps the MSS of TCP connections through it, so web's TCP
# sends smaller segments. The download works; web still drops the ICMP
# that path MTU discovery needs (anything that isn't TCP still breaks).
# r2 has no firewall of its own yet, so it is given one.
on r2 sed -i '/10.0.2.30 lladdr/d; /ip link set prn down/d' /etc/network/up
sudo tee /etc/netns/r2/nftables.conf > /dev/null << 'NFT'
flush ruleset
table inet mangle {
    chain forward {
        type filter hook forward priority mangle; policy accept;
        tcp flags syn tcp option maxseg size set rt mtu
    }
}
NFT
sudo systemctl enable nftables@r2 2> /dev/null
sudo netlab restart
