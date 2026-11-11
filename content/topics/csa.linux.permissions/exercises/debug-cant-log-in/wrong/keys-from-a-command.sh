# Wrong: instead of fixing Ben's folder, the SSH server is given a command
# that prints Ben's keys from a root-owned file, so it never reads his
# ~/.ssh at all. Ben gets in, but the folder can still be written by the
# deploy group, and the server is less strict than it was.
chmod 600 ~/keys/ben
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
sudo mkdir -p /etc/ssh/keys
sudo cp /home/ben/.ssh/authorized_keys /etc/ssh/keys/ben
sudo chmod 644 /etc/ssh/keys/ben
printf 'AuthorizedKeysCommand /usr/bin/cat /etc/ssh/keys/%%u\nAuthorizedKeysCommandUser nobody\n' | sudo tee /etc/ssh/sshd_config.d/60-ben-keys.conf > /dev/null
sudo systemctl restart ssh
