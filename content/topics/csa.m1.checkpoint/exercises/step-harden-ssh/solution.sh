# The one part left: turn off password and root logins, and prove the key
# still works. First the key, before anything changes.
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
# sshd -t only checks the file. The SSH server is already running (that
# first login started it) and keeps its old settings until it's reloaded.
sudo sshd -t && echo "sshd config valid" && sudo systemctl reload ssh
sleep 1
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
