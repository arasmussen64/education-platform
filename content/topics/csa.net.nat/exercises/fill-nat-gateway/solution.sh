# The answer, as you'd make it with nano: gw's whole /etc/nftables.conf,
# written here with "on gw tee FILE <<'EOF'", which copies every line up to
# the one that says EOF into the file (a machine's own file straight in /etc
# can be written into, never replaced). The five gaps: dnat, then
# 10.1.0.20:8443, then postrouting and srcnat, then wan. Then nft checks the
# file, nftables@gw loads it (restart, because its start at boot failed on
# the gaps), and the office and a customer try it.
on gw tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# gw's firewall and NAT. The shop's machines go out to the internet as
# 198.51.100.2; the shop's app is published on 198.51.100.2's port 443;
# nothing else comes in. nftables@gw loads this file at every boot.
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif lo accept
        ct state established,related accept
        iifname "lan" accept
    }
    chain forward {
        type filter hook forward priority filter; policy drop;
        ct state established,related accept
        iifname "lan" oifname "wan" accept
        ct status dnat accept
    }
}

table ip nat {
    chain prerouting {
        type nat hook prerouting priority dstnat; policy accept;
        iifname "wan" tcp dport 443 dnat to 10.1.0.20:8443
    }
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        oifname "wan" masquerade
    }
}
EOF
on gw nft -c -f /etc/nftables.conf
sudo systemctl restart nftables@gw
on office curl -sS -m 3 http://203.0.113.10/
on client curl -sS -m 3 http://198.51.100.2:443/
