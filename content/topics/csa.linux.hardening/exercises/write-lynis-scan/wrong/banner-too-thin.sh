# Wrong: /etc/issue was replaced with a line that warns nobody: Lynis
# looks for the words of a legal notice and finds fewer than five.
# (The scans here run only the tests in question, which takes seconds.)
mkdir -p ~/scan
sudo lynis audit system --quick --tests "SSH-7402 SSH-7404 SSH-7406 SSH-7408 FILE-7524 BANN-7126" > /dev/null 2>&1
sudo cat /var/log/lynis-report.dat > ~/scan/before.dat
echo 'MaxAuthTries 3' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && sudo systemctl reload ssh
sudo chmod 600 /etc/ssh/sshd_config
sudo chmod 700 /etc/cron.d /etc/cron.daily
echo 'Welcome to the shop server. Private.' | sudo tee /etc/issue > /dev/null
echo "SSH-7408 Port: left on 22. Moving the port hides nothing from a scanner; keys and the firewall protect it." > ~/scan/exceptions.txt
sleep 1
sudo lynis audit system --quick --tests "SSH-7402 SSH-7404 SSH-7406 SSH-7408 FILE-7524 BANN-7126" > /dev/null 2>&1
sudo cat /var/log/lynis-report.dat > ~/scan/after.dat
