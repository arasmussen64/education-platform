# A reference solution. Files are written whole with
# "on MACHINE tee FILE << 'EOF'": tee, as root on that machine, writes what
# follows, up to the line EOF, into the file (nano does the same by hand).
#
# Neither file loads yet: nft names the line it can't read, and Caddy's
# journal says why it stopped.
on shop nft -c -f /etc/nftables.conf
journalctl -u caddy@shop -n 3 --no-pager
# The firewall: HTTP/3 runs on QUIC, and QUIC on UDP, on the same port 443
# as HTTPS. nft -c checks the file without loading it and says nothing
# when it's right; the restart loads it (the unit failed at boot, so a
# reload has nothing to reload).
on shop tee /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f
# shop: the web server's own firewall. It lets in SSH and the site, and
# the answers to connections shop starts itself; everything else is
# dropped.
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
on shop nft -c -f /etc/nftables.conf
sudo systemctl restart nftables@shop
# Caddy: h3 is HTTP/3's name in its protocols list.
on shop tee /etc/caddy/Caddyfile << 'EOF'
# The shop's site, served by Caddy over HTTPS, with a certificate from
# Caddy's own local certificate authority (tls internal), which every
# machine in the lab trusts. skip_install_trust: the lab trusts that
# authority itself, so Caddy needn't try to.
{
	skip_install_trust
	# The HTTP versions the site speaks.
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
sudo systemctl restart caddy@shop
# Caddy listens on UDP 443 too, the site advertises it, and HTTP/3 answers.
on shop ss -ulpn
on office curl -sI https://shop.test/
on office h3get https://shop.test/
