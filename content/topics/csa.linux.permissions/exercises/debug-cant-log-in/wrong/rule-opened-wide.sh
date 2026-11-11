# Wrong: the rule is "fixed" by letting the deploy group run anything as
# root without a password. The restart works, and so does everything else.
chmod 600 ~/keys/ben
sudo chmod 700 /home/ben/.ssh
echo '%deploy ALL=(ALL) NOPASSWD: ALL' | sudo tee /etc/sudoers.d/deploy > /dev/null
sudo visudo -c
