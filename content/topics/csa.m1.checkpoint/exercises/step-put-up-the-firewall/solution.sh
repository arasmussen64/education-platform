# The one part left: a default-deny firewall that keeps SSH and the API,
# saved in the file nftables loads at boot, loaded now, and enabled.
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
# Prove it from both sides: the API from the office, the key login from here.
from-office curl -s http://10.0.9.1:8080/
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
