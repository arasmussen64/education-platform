# Wrong: the right rules are loaded into the running kernel, but they were
# never written to /etc/nftables.conf and nftables isn't enabled, so the
# next reboot comes up with no firewall.
sudo systemctl enable --now shop-api
sudo nft -f - <<'NFT'
flush ruleset
table inet filter {
	chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; tcp dport 22 accept; tcp dport 8080 accept; }
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
