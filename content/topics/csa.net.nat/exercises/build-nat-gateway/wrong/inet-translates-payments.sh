# Wrong: one masquerade rule for everything at gw, so payments leave from
# 198.51.100.2, and the provider's router, inet, changed by hand to turn
# them into 198.51.100.3 on their way to srv. Every payment opens, but
# through a change on somebody else's machine, in no file of its own, which
# the next boot of inet (or a real provider) takes away.
echo 'net.ipv4.ip_forward = 1' | on gw tee /etc/sysctl.d/90-gateway.conf > /dev/null
on gw sysctl -p /etc/sysctl.d/90-gateway.conf > /dev/null
on gw tee /etc/nftables.conf > /dev/null <<'EOF'
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
        iifname "wan" ip daddr 198.51.100.2 tcp dport 443 dnat to 10.1.0.20:8443
    }
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        oifname "wan" masquerade
    }
}
EOF
sudo systemctl enable --now nftables@gw
on inet nft add table ip nat
on inet nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; policy accept; }'
on inet nft add rule ip nat postrouting ip saddr 198.51.100.2 ip daddr 203.0.113.10 tcp dport 443 snat to 198.51.100.3
