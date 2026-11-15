# Wrong: the service and SSH are done, but no firewall was put up.
sudo mkdir -p /etc/systemd/system/gateway.service.d
printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/gateway.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now gateway
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && sudo systemctl reload ssh
