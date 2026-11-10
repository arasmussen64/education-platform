# Wrong: everything but the service is fixed; its unit still points at a
# binary that isn't there, so it stays failed.
sudo rm -f /srv/shop/old.bin
sudo chmod 700 /home/ben/.ssh
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
sudo systemctl disable --now shop-worker
