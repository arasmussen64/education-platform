systemctl is-active blog-web || true; sudo ss -ltnp | grep -E ':22 |:8000 ' || echo "(nothing listening on 8000 yet)"
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
sudo systemctl enable --now blog-web; sleep 1; curl -s localhost:8000
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; tcp dport 22 accept; tcp dport 8000 accept; }
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo nft -f /etc/nftables.conf; sudo systemctl enable nftables; from-office curl -s http://10.0.9.1:8000/
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf; sudo sshd -t && echo "config valid" && sudo systemctl reload ssh
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
mkdir -p ~/runbook; { echo "service: $(systemctl is-active blog-web)"; echo "answers: $(curl -s localhost:8000)"; echo "login: $(ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami)"; } > ~/runbook/done.txt; cat ~/runbook/done.txt
