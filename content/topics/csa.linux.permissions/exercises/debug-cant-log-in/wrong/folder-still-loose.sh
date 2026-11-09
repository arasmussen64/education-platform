# Wrong: the key file and the rule are fixed, but Ben's .ssh folder is
# still group-writable, so sshd still ignores his authorized_keys.
chmod 600 ~/keys/ben
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
