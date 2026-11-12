# Wrong: the payment rule names a range of 100 ports, copied from an
# example, so only 100 of the app's 300 connections to the provider get a
# port; the other SYNs are dropped at gw and time out.
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
        oifname "wan" ip saddr 10.1.0.20 ip daddr 203.0.113.10 tcp dport 443 snat to 198.51.100.3:40000-40099
        oifname "wan" snat to 198.51.100.2
    }
}
EOF
sudo systemctl enable --now nftables@gw
