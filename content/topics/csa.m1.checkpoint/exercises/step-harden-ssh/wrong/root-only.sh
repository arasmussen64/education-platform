# Wrong: the drop-in turns off root login but leaves out the password
# setting, so password logins are still accepted.
printf 'PermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
