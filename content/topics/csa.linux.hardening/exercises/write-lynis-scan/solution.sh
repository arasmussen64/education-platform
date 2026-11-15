# 1. Scan before changing anything, and keep the report. Lynis writes its
#    findings as plain lines to /var/log/lynis-report.dat, which only root
#    may read; `sudo cat ... > file` makes a copy that is yours.
mkdir -p ~/scan
sudo lynis audit system
sudo cat /var/log/lynis-report.dat > ~/scan/before.dat
grep -E '^(warning|suggestion)' ~/scan/before.dat | grep -E 'SSH-7408|FILE-7524|BANN-7126'

# 2. Three fixes. SSH-7408 asks for MaxAuthTries 3: a drop-in, tested
#    before the reload, and ben's login tried after it.
echo 'MaxAuthTries 3' | sudo tee /etc/ssh/sshd_config.d/90-hardening.conf
sudo sshd -t && sudo systemctl reload ssh
ssh -i ~/keys/ben -o StrictHostKeyChecking=accept-new -o BatchMode=yes ben@localhost whoami

#    FILE-7524: the test's own log names each path and the mode it expects.
sudo lynis show details FILE-7524 | grep 'not matching'
sudo chmod 600 /etc/ssh/sshd_config
sudo chmod 700 /etc/cron.d /etc/cron.daily

#    BANN-7126: the test counted the words of a legal notice in /etc/issue
#    and found none. A warning goes where the Ubuntu version was.
#    (`sudo tee FILE <<'EOF'` writes the lines up to EOF into the file, as
#    root. In the lab, `sudo nano /etc/issue` does the same job.)
sudo lynis show details BANN-7126 | grep 'key words'
cat /etc/issue
sudo tee /etc/issue > /dev/null <<'EOF'
Authorized users only. Activity on this system is monitored and logged.
Unauthorized access is prohibited and may lead to legal action.
EOF

# 3. The finding that stays: the port. Written down, with the reason.
echo "SSH-7408 Port: left on 22. Moving the port hides nothing from a scanner; keys only and the firewall protect it." > ~/scan/exceptions.txt

# 4. Scan again, keep the second report, and compare the two. `show
#    details` reads the newest scan, so it now shows the banner passing.
sudo lynis audit system
sudo cat /var/log/lynis-report.dat > ~/scan/after.dat
grep -E '^(warning|suggestion)' ~/scan/after.dat | grep -E 'SSH-7408|FILE-7524|BANN-7126'
sudo lynis show details BANN-7126 | grep 'key words'
grep hardening_index ~/scan/before.dat ~/scan/after.dat
ssh -i ~/keys/ben -o StrictHostKeyChecking=accept-new -o BatchMode=yes ben@localhost whoami
