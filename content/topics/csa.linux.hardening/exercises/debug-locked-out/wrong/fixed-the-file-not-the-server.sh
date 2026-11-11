# Wrong: the number is fixed and SSH restarted, which starts the server with
# the wrong group and key login still off. Then the rest of the file is
# corrected, but the server is never told: sshd -T reads the corrected file
# while the server that is running still turns ben away.
sudo sed -i 's/^MaxAuthTries .*/MaxAuthTries 3/' /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
sudo systemctl restart ssh
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
