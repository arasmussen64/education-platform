# Wrong: passwords were turned on while getting ben in, SSH was restarted
# with that, and then the file was put back to "no" without a reload.
# sshd -T reads the file and says passwords are off; the server that is
# running still takes them.
printf 'PasswordAuthentication yes\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
sudo systemctl restart ssh
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
