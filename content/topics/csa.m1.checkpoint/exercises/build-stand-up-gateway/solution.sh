# The runbook for the gateway server, in one go. In the lab you'd write each
# file with nano (and the drop-in with `sudo systemctl edit gateway`); here
# `sudo tee FILE <<'NAME'` writes the lines that follow, up to NAME, into FILE.
# 1. The service. Its unit binds it to 127.0.0.1 (systemctl cat shows the
#    line), so a drop-in overrides that one setting and leaves the unit as
#    it was installed. systemd reads unit files once: daemon-reload makes it
#    read the drop-in, and then the service is enabled for every boot and
#    started now. ss shows 0.0.0.0 on both ports.
systemctl cat gateway
sudo mkdir -p /etc/systemd/system/gateway.service.d
sudo tee /etc/systemd/system/gateway.service.d/override.conf > /dev/null <<'UNIT'
[Service]
Environment=BIND=0.0.0.0
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now gateway
sleep 1
sudo ss -ltnp | grep -E ':9090|:9191'
# 2. The firewall: default deny, keep SSH and both of the gateway's ports
#    (one rule for a set of three), saved in the file nftables loads at
#    boot, loaded now, and enabled.
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport { 22, 9090, 9191 } accept
	}
	chain forward {
		type filter hook forward priority filter; policy drop;
	}
	chain output {
		type filter hook output priority filter; policy accept;
	}
}
NFT
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
# 3. Harden SSH. Prove Ben's key first, so that turning passwords off can't
#    lock him out. AllowGroups is the line that turns Kit away: Kit's key is
#    a good one, but Kit isn't in ssh-users.
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
# sshd -t only checks the file. The SSH server is already running (that
# first login started it) and keeps its old settings until it's reloaded.
sudo sshd -t && echo "sshd config valid" && sudo systemctl reload ssh
# Prove all three: both ports from the office, Kit turned away, Ben let in.
sleep 1
from-office curl -s http://10.0.9.1:9090/
from-office curl -s http://10.0.9.1:9191/
ssh -i ~/keys/kit -o StrictHostKeyChecking=no -o BatchMode=yes kit@localhost whoami || echo "Kit is turned away"
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
