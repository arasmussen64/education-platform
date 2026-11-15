# The runbook for the ledger server, in one go. In the lab you'd write each
# file with nano (and the drop-in with `sudo systemctl edit ledger`); here
# `sudo tee FILE <<'NAME'` writes the lines that follow, up to NAME, into FILE.
# 1. The service. Its unit has no Restart= line (systemctl cat shows the
#    unit), so a drop-in adds one and leaves the unit as it was installed.
#    systemd reads unit files once: daemon-reload makes it read the drop-in,
#    and then the service is enabled for every boot and started now.
systemctl cat ledger
sudo mkdir -p /etc/systemd/system/ledger.service.d
sudo tee /etc/systemd/system/ledger.service.d/override.conf > /dev/null <<'UNIT'
[Service]
Restart=on-failure
RestartSec=2
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now ledger
sleep 1
curl -s localhost:7000
#    Prove the policy: crash it, wait out RestartSec, and it is back.
curl -s localhost:7000/crash
sleep 4
systemctl is-active ledger
curl -s localhost:7000
# 2. The firewall: default deny, and SSH is the only way in. There is no
#    rule for 7000, because no other machine is meant to reach the ledger;
#    `iif lo accept` is what keeps it answering on this machine. Saved in
#    the file nftables loads at boot, loaded now, and enabled.
sudo tee /etc/nftables.conf > /dev/null <<'NFT'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport 22 accept
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
# 3. SSH. First Ana's key, or turning passwords off would leave no way in:
#    her public key goes into her authorized_keys; the folder is 700, the
#    file 600, and both are hers. Then prove the key works.
sudo mkdir -p /home/ana/.ssh
sudo cp /srv/keys/ana.pub /home/ana/.ssh/authorized_keys
sudo chmod 700 /home/ana/.ssh
sudo chmod 600 /home/ana/.ssh/authorized_keys
sudo chown -R ana:ana /home/ana/.ssh
ssh -i ~/keys/ana -o StrictHostKeyChecking=no -o BatchMode=yes ana@localhost whoami
#    Now the hardening drop-in. sshd -t only checks the file. The SSH server
#    is already running (that login started it) and keeps its old settings
#    until it's reloaded.
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "sshd config valid" && sudo systemctl reload ssh
# Prove all three: the ledger here, SSH and no ledger from the office, and
# Ana's login.
sleep 1
curl -s localhost:7000
from-office nc -zv -w 3 10.0.9.1 22
from-office nc -zv -w 3 10.0.9.1 7000 || echo "7000 from the office: no answer at all, dropped"
ssh -i ~/keys/ana -o StrictHostKeyChecking=no -o BatchMode=yes ana@localhost whoami
