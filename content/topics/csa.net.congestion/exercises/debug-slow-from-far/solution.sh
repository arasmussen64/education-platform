# A reference solution, with the evidence that leads to each fault. Files
# are written whole with "on MACHINE tee FILE << 'EOF'": tee, as root on
# that machine, writes what follows, up to the line EOF, into the file
# (nano does the same by hand).
#
# The archive crawls: a few Mbit/s of 50. Over a lossy link that is what a
# loss-based sender gets, so look at the sender's connection while it runs:
# ss on shop names its congestion control, cubic, with a small cwnd.
archive-push
archive-push > /dev/null & sleep 3; on shop ss -tni dst 10.0.6.20; wait
on shop sysctl net.ipv4.tcp_congestion_control
# Someone did ask for BBR, but in dr1's files: dr1 only receives the
# archive, and congestion control runs where data is sent from.
on dr1 grep -r congestion /etc/sysctl.d
# Fault 1: shop, the sender, gets BBR for good, in its own /etc/sysctl.d,
# applied now with sysctl -p (the kernel loads BBR on first use).
on shop tee /etc/sysctl.d/60-bbr.conf << 'EOF'
# The nightly archive crosses a long link that loses packets at random:
# BBR keeps its rate where a loss-based algorithm keeps slowing down.
net.ipv4.tcp_congestion_control = bbr
EOF
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
archive-push
# HTTP/3: the site's HTTPS answers carry no alt-svc header, and nothing on
# shop listens on UDP port 443 (ss -u lists UDP sockets).
on office curl -sI https://shop.test/
on office h3get https://shop.test/
on shop ss -ulpn
on shop cat /etc/caddy/Caddyfile
# Fault 2: the Caddyfile's protocols line leaves h3 out. With it back, a
# reload brings the UDP listener and the alt-svc header.
on shop tee /etc/caddy/Caddyfile << 'EOF'
# The shop's site, served by Caddy over HTTPS, with a certificate from
# Caddy's own local certificate authority (tls internal), which every
# machine in the lab trusts. skip_install_trust: the lab trusts that
# authority itself, so Caddy needn't try to.
{
	skip_install_trust
	servers {
		protocols h1 h2 h3
	}
}

shop.test {
	tls internal
	respond "hello over {http.request.proto}
"
}
EOF
sudo systemctl reload caddy@shop
on shop ss -ulpn
on office curl -sI https://shop.test/
# Advertised now, but HTTP/3 still gets no answer from the office, while
# HTTPS over TCP works: something drops the datagrams. shop's firewall lets
# in UDP 4433, not 443.
on office h3get https://shop.test/
on shop nft list ruleset
# Fault 3: the firewall's file opens UDP 443 and nothing else new, and the
# file is loaded again.
on shop tee /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f
# shop: the web server's own firewall. It lets in SSH and the site, and
# the answers to connections shop starts itself (the nightly archive);
# everything else is dropped.
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif lo accept
        ct state established,related accept
        # SSH, and the site over TCP: HTTP and HTTPS.
        tcp dport { 22, 80, 443 } accept
        # The site over HTTP/3.
        udp dport 443 accept
    }
}
EOF
sudo systemctl reload nftables@shop
on office h3get https://shop.test/
