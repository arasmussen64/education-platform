# Wrong: the checkpoint's build, pasted from its steps with only the names
# changed (shop-api to gateway, 8080 to 9090). Every command works, and the
# result is the shop's server, not this one: the gateway is still bound to
# 127.0.0.1, so no other machine can reach it; port 9191 is shut; and
# nothing stops Kit, who isn't in ssh-users, from logging in.
sudo systemctl enable --now gateway
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport 22 accept
		tcp dport 9090 accept
	}
	chain forward { type filter hook forward priority filter; policy drop; }
	chain output { type filter hook output priority filter; policy accept; }
}
NFT
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "sshd config valid" && sudo systemctl reload ssh
sleep 1
curl -s localhost:9090
from-office curl -s --max-time 3 http://10.0.9.1:9090/ || echo "(no answer from the office)"
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
