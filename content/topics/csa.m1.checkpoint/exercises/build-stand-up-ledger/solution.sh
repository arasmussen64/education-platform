# The runbook for the ledger server, in one go.
# 1. Run the service: enabled for every boot, and started now.
sudo systemctl enable --now ledger
# 2. The firewall: default deny, keep SSH and the ledger (here each rule
#    also counts the packets it accepts, which nft list ruleset then shows),
#    saved in the file nftables loads at boot, loaded now, and enabled.
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; tcp dport 22 counter accept; tcp dport 7000 counter accept; }
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
# 3. Harden SSH: prove the key first, write the drop-in, check it, and
#    reload the server that is already running so it takes the new settings.
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "sshd config valid" && sudo systemctl reload ssh
# Prove all three, from this machine and from the office.
sleep 1
curl -s localhost:7000
from-office curl -s http://10.0.9.1:7000/
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
