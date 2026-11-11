# Wrong: ssh-users is allowed, and so is everyone else. AllowGroups takes
# patterns, and * matches every group, so the line no longer limits
# anything, though sshd -T still lists ssh-users first.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users *\nMaxAuthTries 3\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
sudo systemctl restart ssh
