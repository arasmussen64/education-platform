# The reference: three faults, each found from the evidence, fixed at its
# cause in the file the machine reads at boot. "on MACHINE COMMAND" runs a
# command on a machine. "on M tee FILE <<'EOF'" writes the lines up to EOF
# into FILE on M, as saving it in nano would (sed -i can't replace a file
# that sits straight in a machine's /etc, such as its nftables.conf).
#
# Right after a boot BGP takes a few seconds, so wait until r2 has its
# route to the cloud over both tunnels.
for _ in $(seq 1 30); do on r2 ip route show 10.30.0.0/24 | grep tun2 > /dev/null && break; sleep 1; done

# The monitor's log: loads that try 10.30.0.11 first and then 10.20.0.11
# take 2.5 seconds (curl gives each address half its time); and for about
# half a minute at a time, every load goes to 10.20.0.13, which nothing
# answers.
tail -n 20 /var/log/shop-monitor.log

# 1. The names. ns1 and ns2 give the same serial and different answers:
#    ns1 has www on app1 and app2, ns2 still the old server, 10.20.0.13.
#    ns2's log says ns1's NOTIFY found the "zone is up to date": the zone
#    file was edited on 3 November without a higher serial, so ns2 never
#    copied it. The resolver asks either server, so for a TTL at a time
#    the office is given the dead address. A higher serial (today's date
#    and a count), then ns1 reloads, notifies ns2, and ns2 copies it.
on pc dig +short @10.20.0.53 shop.test SOA
on pc dig +short @10.30.0.200 shop.test SOA
journalctl -u named@ns2 --no-pager | grep 'up to date' | tail -n 1
on ns1 sed -i 's/2026101501 ; serial/2026111201 ; serial/' /etc/bind/db.shop.test
sudo systemctl reload named@ns1
for _ in $(seq 1 30); do
  s2=$(on pc dig +short +time=1 +tries=1 @10.30.0.200 shop.test SOA | cut -d' ' -f3)
  [ "$s2" = 2026111201 ] && break
  sleep 1
done

# 2. app2. With the names right, loads by name that start at app2 are
#    still 2.5 seconds slow: from the office, app2's port 80 gives no
#    answer, while from app1, in the data centre, it does, and the
#    counter on app2's last rule climbs. Its firewall lets the web in
#    from the data centre's network only. The office is one of the shop's
#    networks; nothing wider.
on app2 nft list ruleset
on app2 tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# app2's own firewall: SSH, and the web server for the shop's networks.
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		ct state invalid drop
		icmp type echo-request accept
		tcp dport 22 accept
		ip saddr { 10.10.0.0/24, 10.20.0.0/24 } tcp dport 80 accept
		counter
	}
}
EOF
sudo systemctl reload nftables@app2

# 3. The tunnels. Now some loads to app2 hang instead: the same laptop
#    and server, and only the source port differs, so the variable is the
#    path. Captures on r2's eth0, tun1 and tun2 show every SYN arriving and
#    none leaving on tun2, and the counter of r2's rule from tun2's
#    acceptance test climbs. The rule goes; the one that keeps the cloud
#    out of the office's administration ports stays.
on r2 nft list ruleset
on r2 tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# r2's firewall for the traffic it forwards.
flush ruleset
table inet filter {
	chain forward {
		type filter hook forward priority filter; policy accept;
		# Nothing in the cloud may reach the office's administration ports.
		iifname { "tun1", "tun2" } oifname "eth0" tcp dport { 22, 3389 } counter drop
	}
}
EOF
sudo systemctl reload nftables@r2

# The resolver may still hold the old answer for up to 10 seconds: let it
# forget what it has for shop.test. Then watch the monitor again.
on resolver unbound-control flush_zone shop.test
on resolver unbound-control flush_infra all
sleep 5
tail -n 5 /var/log/shop-monitor.log
