# Wrong: a restart policy was set, but the wrong one. on-abort restarts a
# service only when a signal it didn't catch kills it; the ledger's crash
# is an exit with an error, which on-abort leaves alone.
sudo mkdir -p /etc/systemd/system/ledger.service.d
printf '[Service]\nRestart=on-abort\n' | sudo tee /etc/systemd/system/ledger.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now ledger
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
sudo mkdir -p /home/ana/.ssh
sudo cp /srv/keys/ana.pub /home/ana/.ssh/authorized_keys
sudo chmod 700 /home/ana/.ssh
sudo chmod 600 /home/ana/.ssh/authorized_keys
sudo chown -R ana:ana /home/ana/.ssh
ssh -i ~/keys/ana -o StrictHostKeyChecking=no -o BatchMode=yes ana@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && sudo systemctl reload ssh
