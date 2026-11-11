# Wrong: the drop-in is written and sshd -t and sshd -T both look right, but
# the SSH server was already running (the first login started it) and was
# never reloaded, so it still has the settings it started with and still
# offers password login. Everything else is done.
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "sshd config valid"
sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^allowgroups|^maxauthtries'
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; tcp dport 22 accept; }
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
sudo systemctl stop shop-debug
sudo systemctl disable shop-debug
