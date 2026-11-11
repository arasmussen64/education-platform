# Wrong: instead of fixing Ben's folder, StrictModes is switched off, so the
# server trusts keys in a folder anyone in the deploy group can change. Ben
# gets in, but the server is less strict than it was.
chmod 600 ~/keys/ben
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
echo 'StrictModes no' | sudo tee /etc/ssh/sshd_config.d/50-let-ben-in.conf > /dev/null
sudo systemctl restart ssh
