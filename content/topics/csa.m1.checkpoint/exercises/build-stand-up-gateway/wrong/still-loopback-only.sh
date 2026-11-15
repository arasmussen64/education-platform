# Wrong: everything else is right, but the unit's BIND=127.0.0.1 was left
# alone. The gateway answers curl on this machine and the firewall lets its
# ports in, and from the office the connection is refused: nothing listens
# at 10.0.9.1.
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
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && sudo systemctl reload ssh
