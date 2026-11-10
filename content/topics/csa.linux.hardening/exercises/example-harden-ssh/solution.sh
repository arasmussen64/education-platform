sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^maxauthtries'
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "config valid"
sudo systemctl reload ssh
sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^allowgroups|^maxauthtries'
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
mkdir -p ~/baseline
sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^allowgroups|^maxauthtries' | sort > ~/baseline/ssh.txt
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami > ~/baseline/login.txt
cat ~/baseline/ssh.txt ~/baseline/login.txt
