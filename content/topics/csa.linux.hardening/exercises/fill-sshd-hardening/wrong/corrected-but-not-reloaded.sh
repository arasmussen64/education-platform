# Wrong: the gaps were first filled with passwords left on, and SSH was
# restarted with that. Then the file was corrected, but the server was never
# told: sshd -T reads the corrected file, while the SSH server that is
# running still offers password login.
printf 'PasswordAuthentication yes\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
sudo systemctl restart ssh
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
