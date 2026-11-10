# Wrong: the number and the group are fixed, but key authentication is still
# off, so ben's key is refused.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\nPubkeyAuthentication no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
