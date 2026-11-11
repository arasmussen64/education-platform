# The whole runbook, from the outline.
# 1. Run the service.
sudo systemctl enable --now shop-api
# 2. Put up the firewall, and try it from the office.
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
sleep 1
from-office curl -s http://10.0.9.1:8080/
# 3. Harden SSH: the key first, then the drop-in, the check, and the reload
#    that makes the server that is already running take the new settings.
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "sshd config valid" && sudo systemctl reload ssh
sleep 1
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
