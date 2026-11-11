# Wrong: the key file and the rule are fixed, but Ben's .ssh folder can
# still be written by the deploy group, which has Ana in it, so sshd still
# ignores his authorized_keys. Only the server's check fails.
chmod 600 ~/keys/ben
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
