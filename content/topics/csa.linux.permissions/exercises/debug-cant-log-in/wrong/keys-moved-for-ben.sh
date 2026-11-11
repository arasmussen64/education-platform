# Wrong: instead of fixing Ben's folder, the SSH server is told to read
# Ben's keys from a root-owned file elsewhere, in a "Match User ben" block.
# Ben gets in, but his ~/.ssh can still be written by the deploy group, and
# the server is less strict for him than it was. Plain sshd -T doesn't show
# a Match block's settings; the check asks for the ones Ben's login gets.
chmod 600 ~/keys/ben
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
sudo mkdir -p /etc/ssh/keys
sudo cp /home/ben/.ssh/authorized_keys /etc/ssh/keys/ben
sudo chmod 644 /etc/ssh/keys/ben
printf 'Match User ben\n    AuthorizedKeysFile /etc/ssh/keys/%%u\n' | sudo tee /etc/ssh/sshd_config.d/60-ben-keys.conf > /dev/null
sudo systemctl restart ssh
