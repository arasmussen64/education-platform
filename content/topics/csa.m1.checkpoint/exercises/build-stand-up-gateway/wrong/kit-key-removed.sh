# Wrong: instead of a rule about who may log in, Kit's installed key was
# deleted. Kit is turned away today, but the runbook's rule, only the
# ssh-users group, isn't on the server: the next account with a key gets in.
sudo mkdir -p /etc/systemd/system/gateway.service.d
printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/gateway.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now gateway
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; tcp dport { 22, 9090, 9191 } accept; }
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
sudo rm /home/kit/.ssh/authorized_keys
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && sudo systemctl reload ssh
