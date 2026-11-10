# Wrong: "fixed" the lock-out by turning password authentication back on,
# which lets ben in but undoes the hardening.
printf 'PasswordAuthentication yes\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
