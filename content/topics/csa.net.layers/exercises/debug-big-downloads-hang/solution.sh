# The reference fix: each fault fixed at its cause, in the file the machine
# reads at boot. "on MACHINE COMMAND" runs a command on a machine.

# 1. web's firewall dropped every ICMP message before the rule that lets in
#    what belongs to known connections, so r2's "fragmentation needed"
#    never reached web's kernel, and web kept sending packets too big for
#    the tunnel. Now it drops only ping's echo requests, as the server team
#    meant. tee FILE <<'EOF' writes the lines up to EOF into FILE; in the
#    lab, nano does the same (sed -i can't replace a machine's own file
#    that sits straight in /etc).
on web tee /etc/nftables.conf > /dev/null << 'EOF'
#!/usr/sbin/nft -f
# web's firewall: from outside, only the website.
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif lo accept
        # The server team's hardening: no ping.
        icmp type echo-request drop
        ct state established,related accept
        tcp dport 80 accept
    }
}
EOF
sudo systemctl reload nftables@web

# 2 and 3. r2 pinned the file server's address to a network card it no
#    longer has, so frames for it went to a MAC address nobody owns; and
#    r2's printer link was set down, so its default route sent the
#    printer's traffic back into the tunnel, round and round. Both lines
#    go (ARP finds the file server's card by itself), and the network is
#    built again from the files. sed -i '/TEXT/d' deletes each line that
#    holds TEXT.
on r2 sed -i '/10.0.2.30 lladdr/d; /ip link set prn down/d' /etc/network/up
sudo netlab restart

# Look: the price list, the file server and the printer, from the office.
on office curl -s -o /dev/null -w '%{size_download} bytes\n' http://10.0.2.20/pricelist.csv
on office curl -s http://10.0.2.30/
on office ping -c 2 10.0.3.5
