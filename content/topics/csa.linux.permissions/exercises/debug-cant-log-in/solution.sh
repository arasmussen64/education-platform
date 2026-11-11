# The three mistakes:
#   1. Ben's ~/.ssh could be written by its group, deploy, which has Ana in
#      it too. sshd ignores the keys in a folder someone else could change
#      (journalctl -u ssh says "bad ownership or modes for directory").
#      Ubuntu's sshd lets a folder's group write to it only when nobody but
#      the owner is in that group, as with Ben's own group, ben.
#   2. The private key was readable by everyone (644). ssh refuses to use a
#      key like that ("UNPROTECTED PRIVATE KEY FILE") and falls back to a
#      password Ben doesn't have. It shows only once the server accepts the
#      folder, because ssh opens the private key after the server has
#      accepted the public one.
#   3. The sudo rule allowed "systemctl restart shopapi", a service that
#      doesn't exist, so the real command needed a password.
sudo chmod 700 /home/ben/.ssh
chmod 600 ~/keys/ben
# In the lab you'd edit the rule with: sudo visudo -f /etc/sudoers.d/deploy
sudo sed -i 's|restart shopapi|restart shop-api|' /etc/sudoers.d/deploy
sudo visudo -c
sudo -l -U ben
ssh -i ~/keys/ben -o StrictHostKeyChecking=accept-new ben@localhost 'sudo -n systemctl restart shop-api && echo "restarted the API as $(whoami)"'
