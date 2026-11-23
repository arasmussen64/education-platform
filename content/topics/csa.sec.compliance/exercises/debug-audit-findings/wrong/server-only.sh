# The server is fixed and the pack is left as it was handed over.

# 1. Root over SSH. The rule passes and sshd's files say no, yet the login
# is allowed: a benchmark rule and "sshd -T" read files, and the running
# server was started with a setting of its own. "systemctl status" shows a
# drop-in for the unit, and "systemctl cat" shows what it does: it starts
# sshd with "-o PermitRootLogin=yes", which beats every file. Remove it,
# have systemd read its unit files again, and restart the server.
sudo sshd -T | grep -i permitrootlogin
systemctl status ssh --no-pager | head -n 6
systemctl cat ssh
sudo rm /etc/systemd/system/ssh.service.d/20-support.conf
sudo systemctl daemon-reload
sudo systemctl restart ssh

# 2. The journal. Its file is under /run, which is memory. The settings in
# force show two Storage= lines, and for journald the last one read wins:
# a later drop-in says volatile. Remove it and restart journald, which
# reads its settings when it starts. A journal that began in memory moves to
# the disk at the next boot, or at once when asked with --flush.
sudo journalctl --header | grep 'File path'
systemd-analyze cat-config systemd/journald.conf | grep -E '^# |Storage'
sudo rm /etc/systemd/journald.conf.d/90-wear.conf
sudo systemctl restart systemd-journald
sudo journalctl --flush
sudo journalctl --header | grep 'File path'

