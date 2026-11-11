# Wrong: default-deny, saved and enabled, with SSH and the API, but also
# the web's two ports, 80 and 443, "in case the shop needs them later".
# Nobody asked for them, so from outside more than SSH and the API can be
# reached: anything that ever listens there is open to the world.
sudo systemctl enable --now shop-api
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; tcp dport { 22, 80, 443, 8080 } accept; }
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && sudo systemctl reload ssh
