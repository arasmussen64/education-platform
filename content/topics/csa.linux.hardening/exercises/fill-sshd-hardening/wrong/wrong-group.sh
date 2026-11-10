# Wrong: AllowGroups was filled in as a group ben isn't in, so the config
# looks hardened but ben can't log in.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups admins\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
