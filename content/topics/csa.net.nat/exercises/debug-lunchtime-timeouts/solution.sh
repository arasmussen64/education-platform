# A reference fix. The three faults were all in gw's /etc/nftables.conf:
# 1. the payment rule translated to only 50 ports (40000-40049), fewer than
#    the lunchtime peak's 120 connections to one destination, so the rest of
#    the SYNs were dropped at gw (conntrack -S: insert_failed) and timed out;
#    without a range, snat uses the whole port range of 198.51.100.3;
# 2. the catch-all masquerade matched iifname "wan", traffic that arrived
#    from the internet, so every customer reached the app as gw's LAN
#    address, 10.1.0.1; a catch-all for what leaves is oifname "wan";
# 3. the office's rule still named the office's old network, 10.1.1.0/24,
#    so its PCs left untranslated (conntrack: a reply tuple to 10.1.0.10)
#    and no reply could come back.
# The whole file is written here with "on gw tee FILE <<'EOF'", which copies
# every line up to the one that says EOF into the file, as nano would save
# it; nft checks it; restarting nftables@gw loads it, as every boot does.
on gw tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# gw: the shop's gateway. The office and the app go out to the internet as
# 198.51.100.2; the app's card payments go out as 198.51.100.3, the address
# the payment provider allows; the shop's app is published on 198.51.100.2's
# port 443; nothing else comes in. nftables@gw loads this file at every boot.
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
        # The shop's app, for customers.
        iifname "wan" ip daddr 198.51.100.2 tcp dport 443 dnat to 10.1.0.20:8443
    }
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        # Card payments, from the app to the payment provider.
        oifname "wan" ip saddr 10.1.0.20 ip daddr 203.0.113.10 tcp dport 443 snat to 198.51.100.3
        # The app's other traffic.
        oifname "wan" ip saddr 10.1.0.20 snat to 198.51.100.2
        # The office.
        oifname "wan" ip saddr 10.1.0.0/24 snat to 198.51.100.2
    }
}
EOF
on gw nft -c -f /etc/nftables.conf
sudo systemctl restart nftables@gw
on office curl -sS -m 3 http://203.0.113.10/
on client curl -sS -m 3 http://198.51.100.2:443/
on app holdconns 240 203.0.113.10 443 1
