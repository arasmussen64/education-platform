# Step 1. The fault: the download times out, while the office still
# reaches the API.
curl -m 5 http://files.office.internal:8000/prices.csv || echo "the download failed"
from-office curl -m 5 http://shop.internal:8080/
# Step 2. The table. The dashboard's connection is the one from the office
# to port 8080 that stays ESTABLISHED; its first sport= is the office's
# port. At the keyboard you'd read the line and type the number. This picks
# it out: the health checks are open for a few thousandths of a second
# each, so a port that is ESTABLISHED in two listings four seconds apart is
# the dashboard's (uniq -d prints the lines that occur twice).
sudo conntrack -L
mkdir -p ~/conntrack
sudo conntrack -L 2> /dev/null | grep ESTABLISHED | grep 'dport=8080 src' | awk '{print $7}' > /tmp/first-look
sleep 4
sudo conntrack -L 2> /dev/null | grep ESTABLISHED | grep 'dport=8080 src' | awk '{print $7}' > /tmp/second-look
sort /tmp/first-look /tmp/second-look | uniq -d | cut -d= -f2 > ~/conntrack/dashboard-port.txt
cat ~/conntrack/dashboard-port.txt
# Step 3. The download is in the table too, as SYN_RECV: the kernel saw the
# office's reply, and the input chain then dropped it.
curl -m 3 http://files.office.internal:8000/prices.csv || true
sudo conntrack -L 2> /dev/null | grep dport=8000
sudo nft list ruleset
# Step 4. One rule, in the file: packets of a connection the kernel is
# already tracking are accepted. (sudo tee FILE <<'EOF' writes the lines up
# to EOF into the file; with nano you'd add the one line.)
sudo tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# The shop server's firewall: nothing in but SSH, the API and the name
# server; replies to our own connections; and the machine talking to itself.
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state invalid drop
		ct state established,related accept
		tcp dport { 22, 8080 } accept
		udp dport 53 accept
	}
	chain forward {
		type filter hook forward priority filter; policy drop;
	}
	chain output {
		type filter hook output priority filter; policy accept;
	}
}
EOF
sudo nft -f /etc/nftables.conf
curl -m 5 http://files.office.internal:8000/prices.csv
sudo conntrack -L 2> /dev/null | grep dport=8000
from-office nc -zv -w 3 shop.internal 5432 || echo "5432 from the office: still no answer at all"
