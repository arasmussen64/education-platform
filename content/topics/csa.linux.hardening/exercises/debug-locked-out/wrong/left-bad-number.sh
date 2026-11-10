# Wrong: the group and the key setting are fixed, but MaxAuthTries is still
# a word, so sshd -t rejects the file and SSH won't start.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries nope\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t || true
