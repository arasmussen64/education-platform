# Wrong: every step but the reload. sshd -T reads the files, so the saved
# proof says passwords are off, while the SSH server that the first login
# started still has its old settings and still offers password login.
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups ssh-users\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && echo "config valid"
mkdir -p ~/baseline
sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^allowgroups|^maxauthtries' | sort > ~/baseline/ssh.txt
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami > ~/baseline/login.txt
