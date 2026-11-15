# Wrong: the checkpoint's build, pasted from its steps with only the names
# changed (shop-api to ledger, 8080 to 7000, ben to ana). The result is the
# shop's server, not this one: nothing restarts the ledger after a crash;
# its port, which only this machine should reach, is open to the office;
# and passwords were turned off with no key installed for Ana, so nobody
# can log in. The only additions are the "|| echo" on the logins, which
# fail here, so that the script itself ends without an error.
sudo systemctl enable --now ledger
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport 22 accept
		tcp dport 7000 accept
	}
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
ssh -i ~/keys/ana -o StrictHostKeyChecking=no -o BatchMode=yes ana@localhost whoami || echo "(Ana can't log in)"
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "sshd config valid" && sudo systemctl reload ssh
sleep 1
curl -s localhost:7000
from-office curl -s http://10.0.9.1:7000/
ssh -i ~/keys/ana -o StrictHostKeyChecking=no -o BatchMode=yes ana@localhost whoami || echo "(Ana can't log in)"
