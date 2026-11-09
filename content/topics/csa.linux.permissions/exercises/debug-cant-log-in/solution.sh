# The three mistakes:
#   1. The private key was readable by everyone (644). ssh refuses to use a
#      key like that ("UNPROTECTED PRIVATE KEY FILE") and falls back to a
#      password Ben doesn't have.
#   2. Ben's ~/.ssh folder was 775: group-writable. sshd's StrictModes
#      ignores keys in a folder other people could change (journalctl -u ssh
#      says "bad ownership or modes for directory").
#   3. The sudo rule allowed "systemctl restart shopapi", a service that
#      doesn't exist, so the real command needed a password.
chmod 600 ~/keys/ben
sudo chmod 700 /home/ben/.ssh
# In the lab you'd edit the rule with: sudo visudo -f /etc/sudoers.d/deploy
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
sudo visudo -c
sudo -l -U ben
ssh -i ~/keys/ben -o StrictHostKeyChecking=accept-new ben@localhost 'sudo -n systemctl restart shop-api && echo "restarted the API as $(whoami)"'
