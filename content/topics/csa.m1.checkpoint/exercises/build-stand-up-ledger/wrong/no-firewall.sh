# Wrong: the service and SSH are done, but no firewall was put up, so the
# office can reach the ledger and anything else that listens.
sudo mkdir -p /etc/systemd/system/ledger.service.d
printf '[Service]\nRestart=on-failure\n' | sudo tee /etc/systemd/system/ledger.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now ledger
sudo mkdir -p /home/ana/.ssh
sudo cp /srv/keys/ana.pub /home/ana/.ssh/authorized_keys
sudo chmod 700 /home/ana/.ssh
sudo chmod 600 /home/ana/.ssh/authorized_keys
sudo chown -R ana:ana /home/ana/.ssh
ssh -i ~/keys/ana -o StrictHostKeyChecking=no -o BatchMode=yes ana@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && sudo systemctl reload ssh
