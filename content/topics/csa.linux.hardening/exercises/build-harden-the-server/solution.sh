# The whole baseline, in one go; in the lab you'd use nano for each file.
# Before anything changes, prove the key works. (This first login is also
# what starts the SSH server, which then keeps the settings it read.)
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
# 1. Harden SSH: write the drop-in, check it, then tell the running server.
#    Without the reload, sshd -T would show the new settings while the
#    server went on taking passwords.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "sshd config valid"
sudo systemctl reload ssh
sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^allowgroups|^maxauthtries'
# 2. A default-deny firewall that keeps SSH.
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport 22 accept
	}
	chain forward {
		type filter hook forward priority filter; policy drop;
	}
	chain output {
		type filter hook output priority filter; policy accept;
	}
}
NFT
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
# 3. Close the open debugging door, now and at the next boot.
sudo systemctl stop shop-debug
sudo systemctl disable shop-debug
# 4. Prove it from outside: the login still works, the old door gets no
#    answer, and the server can still reach out.
from-office ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@10.0.9.1 whoami
from-office nc -zv -w 3 10.0.9.1 9000 || echo "9000 from the office: no answer at all, dropped"
nc -zv -w 3 10.0.9.2 9100
sudo ss -ltnp | grep -E ':22|:9000' || true
