# Wrong: the firewall is loaded into the running kernel but not saved to
# /etc/nftables.conf or enabled, so the first reboot comes up with no
# firewall.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo nft -f - <<'NFT'
flush ruleset
table inet filter {
	chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; tcp dport 22 accept; }
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo systemctl stop shop-debug
sudo systemctl disable shop-debug
