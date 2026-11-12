# A reference gateway. Forwarding first: a file of its own in gw's
# /etc/sysctl.d, named so it comes after 60-hardening.conf (files apply in
# name order, the later one winning), applied now with sysctl -p. Then gw's
# whole /etc/nftables.conf, written with "on gw tee FILE <<'EOF'", which
# copies every line up to the one that says EOF into the file (as nano
# would save it): the filter table that drops what no rule accepts, the
# published port on 198.51.100.2 only, and source NAT with the payment rule
# first, because the first source NAT rule that matches a connection wins.
# nft checks the file, nftables@gw loads it now and at every boot, and the
# rest tries it.
echo 'net.ipv4.ip_forward = 1' | on gw tee /etc/sysctl.d/90-gateway.conf
on gw sysctl -p /etc/sysctl.d/90-gateway.conf
on gw tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# gw: the shop's gateway. The shop goes out as 198.51.100.2, payments as
# 198.51.100.3, the app is published on 198.51.100.2's port 443, and
# nothing else comes in.
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
    chain output {
        type filter hook output priority filter; policy accept;
    }
}

table ip nat {
    chain prerouting {
        type nat hook prerouting priority dstnat; policy accept;
        iifname "wan" ip daddr 198.51.100.2 tcp dport 443 dnat to 10.1.0.20:8443
    }
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        oifname "wan" ip saddr 10.1.0.20 ip daddr 203.0.113.10 tcp dport 443 snat to 198.51.100.3
        oifname "wan" snat to 198.51.100.2
    }
}
EOF
on gw nft -c -f /etc/nftables.conf
sudo systemctl enable --now nftables@gw
on office curl -sS -m 3 http://203.0.113.10/
on app curl -sS -m 3 http://203.0.113.10/
on client curl -sS -m 3 http://198.51.100.2:443/
on app holdconns 300 203.0.113.10 443 1
