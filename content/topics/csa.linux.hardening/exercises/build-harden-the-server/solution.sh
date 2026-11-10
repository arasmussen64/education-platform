# The whole baseline, in one go; in the lab you'd use nano for each file.
# 1. Harden SSH.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "sshd config valid"
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
# 3. Close the open debugging door.
sudo systemctl stop shop-debug
sudo systemctl disable shop-debug
# 4. Prove the login still works.
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
sudo ss -ltnp | grep -E ':22|:9000' || true
