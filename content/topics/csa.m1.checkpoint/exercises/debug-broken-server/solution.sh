# Restore the server, five faults, without weakening security.
# 1. Free the disk: an old file was filling the data area.
sudo rm -f /srv/shop/old.bin
# 2. Fix the service: its ExecStart named a binary that isn't there.
sudo sed -i 's#/usr/local/bin/shop-api-typo#/usr/local/bin/shop-api#' /etc/systemd/system/shop-api.service
sudo systemctl daemon-reload
sudo systemctl restart shop-api
# 3. Fix ben's key permissions: a world-writable ~/.ssh is refused.
sudo chmod 700 /home/ben/.ssh
# 4. Open the API's port, keeping the firewall default-deny, and persist it.
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport 22 accept
		tcp dport 8080 accept
	}
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo nft -f /etc/nftables.conf
# 5. Stop the runaway at its service, so it stays stopped.
sudo systemctl disable --now shop-worker
echo "--- restored:"
df -h /srv/shop | tail -1
systemctl is-active shop-api
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
