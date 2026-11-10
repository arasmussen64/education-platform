# Wrong: did the service and SSH, skipped the firewall step of the outline.
sudo systemctl enable --now shop-api
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
