# The finished drop-in. In the lab you'd fill the four gaps with nano; here
# it's written in one go.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "config valid"
# Apply it. The service couldn't start while the file had gaps, so there is
# nothing running to reload: restart starts it with the finished file.
sudo systemctl restart ssh
sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^allowgroups|^maxauthtries'
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
