# The three faults were all in the hardening drop-in:
# 1. MaxAuthTries was a word, not a number, so sshd rejected the whole
#    configuration and the service couldn't start: connections were reset,
#    then refused. `sudo sshd -t` named the file and the line.
# 2. AllowGroups named "admins", a group ben isn't in (he's in ssh-users),
#    so once the server started it turned him away. `journalctl -u ssh`
#    said so.
# 3. PubkeyAuthentication was "no", which switched off key login itself:
#    with passwords off too, the server offered no way in at all
#    ("Permission denied ()").
# The corrected drop-in: a real number, the right group, keys back on, and
# passwords and root still off. In the lab you'd edit it with sudo nano.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\nPubkeyAuthentication yes\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "config valid"
# The service isn't running (it couldn't start), so there's nothing to
# reload: restart starts it with the corrected file.
sudo systemctl restart ssh
sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^allowgroups|^maxauthtries|^pubkeyauthentication'
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
