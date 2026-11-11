# Wrong: the drop-in is correct, but the SSH server was already running
# (the first login started it) and was never reloaded, so the server that
# is actually answering still accepts passwords.
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
