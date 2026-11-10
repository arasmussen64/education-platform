# Wrong: AllowGroups was set to a group ben isn't in, so the settings look
# hardened but ben, the person who needs access, is locked out. The login
# proof fails.
printf 'PasswordAuthentication no\nPermitRootLogin no\nAllowGroups admins\nMaxAuthTries 3\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
mkdir -p ~/baseline
sudo sshd -T | grep -iE '^passwordauthentication|^permitrootlogin|^allowgroups|^maxauthtries' | sort > ~/baseline/ssh.txt
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami > ~/baseline/login.txt 2>/dev/null || echo "(locked out)" > ~/baseline/login.txt
