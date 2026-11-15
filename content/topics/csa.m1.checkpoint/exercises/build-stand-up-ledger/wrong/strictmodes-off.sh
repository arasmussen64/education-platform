# Wrong: Ana's ~/.ssh was left writable by everyone, and instead of fixing
# the permissions, sshd was told to stop checking them (StrictModes no).
# Ana can log in, and so can anyone who writes a key of their own into
# that folder.
sudo mkdir -p /etc/systemd/system/ledger.service.d
printf '[Service]\nRestart=on-failure\n' | sudo tee /etc/systemd/system/ledger.service.d/override.conf > /dev/null
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
sudo chown -R ana:ana /home/ana/.ssh
sudo chmod 777 /home/ana/.ssh
printf 'PasswordAuthentication no\nPermitRootLogin no\nStrictModes no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && (sudo systemctl reload ssh || sudo systemctl restart ssh)
sleep 1
ssh -i ~/keys/ana -o StrictHostKeyChecking=no -o BatchMode=yes ana@localhost whoami
