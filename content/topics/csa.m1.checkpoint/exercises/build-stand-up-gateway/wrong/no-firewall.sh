# Wrong: the service and SSH are done, but no firewall was put up.
sudo systemctl enable --now gateway
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
