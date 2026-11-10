# Wrong: the service and SSH were done and the proof written, but the
# firewall steps were skipped.
sudo systemctl enable --now blog-web
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t
mkdir -p ~/runbook; { echo "service: $(systemctl is-active blog-web)"; echo "answers: $(curl -s localhost:8000)"; echo "login: $(ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami)"; } > ~/runbook/done.txt
