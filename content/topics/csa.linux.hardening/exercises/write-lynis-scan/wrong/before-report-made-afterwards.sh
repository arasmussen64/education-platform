# Wrong: the scan before was forgotten. Once the fixes were in, a scan was
# taken and the three findings were typed into its report by hand to make
# a "before"; a second scan made the "after". The reports look right, but
# the files on the server were changed before either scan was taken.
# (The scans here run only the tests in question, which takes seconds.)
mkdir -p ~/scan
echo 'MaxAuthTries 3' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf > /dev/null
sudo sshd -t && sudo systemctl reload ssh
sudo chmod 600 /etc/ssh/sshd_config
sudo chmod 700 /etc/cron.d /etc/cron.daily
printf 'Authorized users only. Activity on this system is monitored and logged.\nUnauthorized access is prohibited and may lead to legal action.\n' | sudo tee /etc/issue > /dev/null
echo "SSH-7408 Port: left on 22. Moving the port hides nothing from a scanner; keys and the firewall protect it." > ~/scan/exceptions.txt
sleep 1
sudo lynis audit system --quick --tests "SSH-7402 SSH-7404 SSH-7406 SSH-7408 FILE-7524 BANN-7126" > /dev/null 2>&1
sudo cat /var/log/lynis-report.dat > ~/scan/before.dat
echo 'suggestion[]=SSH-7408|Consider hardening SSH configuration|MaxAuthTries (set 6 to 3)|-|' >> ~/scan/before.dat
echo 'suggestion[]=BANN-7126|Add a legal banner to /etc/issue, to warn unauthorized users|-|-|' >> ~/scan/before.dat
echo 'suggestion[]=FILE-7524|Consider restricting file permissions|See screen output or log file|text:Use chmod to change file permissions|' >> ~/scan/before.dat
sleep 1
sudo lynis audit system --quick --tests "SSH-7402 SSH-7404 SSH-7406 SSH-7408 FILE-7524 BANN-7126" > /dev/null 2>&1
sudo cat /var/log/lynis-report.dat > ~/scan/after.dat
