# The runbook, in one go. In the lab you'd do each part and check it.
# 1. Run the service: enabled for every boot, and started now.
sudo systemctl enable --now shop-api
# 2. The firewall: default deny, keep SSH and the API. It goes in the file
#    nftables loads at boot, the file is loaded now, and the service that
#    loads it at boot is enabled.
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
sudo systemctl enable nftables
# 3. Harden SSH. Prove the key works first, so that turning passwords off
#    can't lock anyone out.
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
# sshd -t only checks the file. The SSH server is already running (that
# first login started it) and keeps its old settings until it's reloaded.
sudo sshd -t && echo "sshd config valid" && sudo systemctl reload ssh
# Prove all three, from this machine and from the office.
sleep 1
curl -s localhost:8080
from-office curl -s http://10.0.9.1:8080/
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
