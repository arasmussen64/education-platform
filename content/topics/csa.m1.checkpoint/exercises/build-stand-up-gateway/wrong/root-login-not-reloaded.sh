# Wrong: passwords were turned off, the group rule added and the SSH server
# reloaded, and then root logins were turned off in the same file with no
# second reload. The files say no to root; the server that is running still
# has its old setting.
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
printf 'PasswordAuthentication no\nAllowGroups ssh-users\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && sudo systemctl reload ssh
sleep 2
printf 'PermitRootLogin no\n' | sudo tee -a /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t
