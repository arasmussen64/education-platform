# Wrong: root login and the group are set, but password authentication was
# left on, so guessing attacks still work.
printf 'PermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
mkdir -p ~/baseline
sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^allowgroups|^maxauthtries' | sort > ~/baseline/ssh.txt
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami > ~/baseline/login.txt
