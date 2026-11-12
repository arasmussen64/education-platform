# A reference solution. Files are written whole with
# "on MACHINE tee FILE << 'EOF'": tee, as root on that machine, writes what
# follows, up to the line EOF, into the file (nano does the same by hand).
#
# 1. The archive. shop sends it, with the system's congestion control,
# CUBIC, which takes every lost packet as a sign of congestion: a few
# Mbit/s on this link. ss on shop during a run shows cubic.
archive-push
archive-push > /dev/null & sleep 3; on shop ss -tni dst 10.0.6.20; wait
# Congestion control runs where data is sent from, so the setting belongs
# on shop: BBR for good, in shop's own /etc/sysctl.d, and applied now.
on shop tee /etc/sysctl.d/60-bbr.conf << 'EOF'
# The nightly archive crosses a long link that loses packets at random:
# BBR keeps its rate where a loss-based algorithm keeps slowing down.
net.ipv4.tcp_congestion_control = bbr
EOF
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
archive-push
#
# 2. HTTP/3. Caddy's defaults already offer it: its HTTPS answers carry
# alt-svc, and it listens on UDP port 443. But from the office HTTP/3 gets
# no answer, while HTTPS over TCP works: fw lets in only TCP.
on office curl -sI https://shop.test/
on shop ss -ulpn
on office h3get https://shop.test/
on fw nft list ruleset
# fw's file lets UDP 443 through to shop as well, and nothing else new, and
# is loaded again.
on fw tee /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f
# fw: the site's firewall, between the internet and shop. It lets the
# internet reach shop's SSH and the site (HTTP and HTTPS over TCP, HTTP/3
# over UDP 443), lets out everything shop starts, and drops everything
# else. fw itself takes nothing from the internet.
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif lo accept
        ct state established,related accept
    }
    chain forward {
        type filter hook forward priority filter; policy drop;
        ct state established,related accept
        iifname "shop" oifname "isp" accept
        iifname "isp" oifname "shop" ip daddr 203.0.113.10 tcp dport { 22, 80, 443 } accept
        iifname "isp" oifname "shop" ip daddr 203.0.113.10 udp dport 443 accept
    }
}
EOF
sudo systemctl reload nftables@fw
on office h3get https://shop.test/
