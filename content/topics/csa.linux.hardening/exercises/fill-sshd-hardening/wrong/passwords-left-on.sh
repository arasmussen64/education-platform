# Wrong: root login, group and tries are set, but password authentication
# was filled in as yes, so guessing attacks still work.
printf 'PasswordAuthentication yes\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
