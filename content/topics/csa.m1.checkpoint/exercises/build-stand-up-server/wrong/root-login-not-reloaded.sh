# Wrong: passwords were turned off and the SSH server reloaded, and then
# root logins were turned off in the same file with no second reload. The
# files say no to root; the server that is running still has its old
# setting, which lets root in with a key.
sudo systemctl enable --now shop-api
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; tcp dport 22 accept; tcp dport 8080 accept; }
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && sudo systemctl reload ssh
sleep 2
printf 'PermitRootLogin no\n' | sudo tee -a /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
