# Wrong: the drop-in that was in the way is simply deleted. SSH starts and
# ben gets in, but every bit of the hardening went with the file: passwords
# are back on, root may log in with a key, any group may log in, six tries.
sudo rm /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
sudo systemctl restart ssh
