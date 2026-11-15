# Wrong: sshd_config was closed, the two cron folders were not, so
# FILE-7524 still reports.
# (The scans here run only the tests in question, which takes seconds.)
mkdir -p ~/scan
sudo lynis audit system --quick --tests "SSH-7402 SSH-7404 SSH-7406 SSH-7408 FILE-7524 BANN-7126" > /dev/null 2>&1
sudo cat /var/log/lynis-report.dat > ~/scan/before.dat
echo 'MaxAuthTries 3' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && sudo systemctl reload ssh
sudo chmod 600 /etc/ssh/sshd_config
printf 'Authorized users only. Activity on this system is monitored and logged.\nUnauthorized access is prohibited and may lead to legal action.\n' | sudo tee /etc/issue > /dev/null
echo "SSH-7408 Port: left on 22. Moving the port hides nothing from a scanner; keys and the firewall protect it." > ~/scan/exceptions.txt
sleep 1
sudo lynis audit system --quick --tests "SSH-7402 SSH-7404 SSH-7406 SSH-7408 FILE-7524 BANN-7126" > /dev/null 2>&1
sudo cat /var/log/lynis-report.dat > ~/scan/after.dat
