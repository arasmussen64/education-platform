# The seven faults, each with the evidence that gave it away.
# 1. The data area was full: df -h /srv/shop said 100%, and du and ls -l
#    found one big export that nobody had touched since 2019. That goes;
#    orders.db, the shop's live data, stays.
sudo rm -f /srv/shop/export-2019.bin
# 2. shop-api couldn't start: systemctl status said status=203/EXEC, which
#    is systemd failing at the step of running the program. Its ExecStart
#    named /usr/bin/shop-api, and ls shows the program is in /usr/local/bin.
sudo sed -i 's#^ExecStart=/usr/bin/shop-api#ExecStart=/usr/local/bin/shop-api#' /etc/systemd/system/shop-api.service
sudo systemctl daemon-reload
sudo systemctl restart shop-api
# 3. Ben's key was refused: journalctl -u ssh said "bad ownership or modes
#    for directory /home/ben/.ssh". Anyone could write to that folder, so
#    sshd wouldn't trust the keys in it. The fix is the folder, not sshd.
sudo chmod 700 /home/ben/.ssh
# 4. The API now answered here, but not from the office: the firewall had
#    no rule for its port. The rule goes in the file nftables loads at boot,
#    and the file is loaded now, so the running rules and the saved ones
#    are the same. (One rule for a set of ports; a second rule beside the
#    first is just as good.)
sudo sed -i 's/tcp dport 22 accept/tcp dport { 22, 8080 } accept/' /etc/nftables.conf
sudo nft -f /etc/nftables.conf
# 5. A CPU was busy for nothing: top named shop-worker, and its unit said
#    it was retired. Stopped now, and disabled so a reboot doesn't bring it
#    back.
sudo systemctl disable --now shop-worker
# 6 and 7. shop-search. Killed: systemctl status showed its memory at its
#    128 MB limit just before each kill, and journalctl -k had the kernel's
#    "Memory cgroup out of memory" line; given room, memory.peak settles at
#    about 160 MB. Throttled: nr_throttled in its cpu.stat rose in almost
#    every period under a 5% quota, and usage_usec showed it using about
#    20% of a CPU once it was let. A drop-in gives it limits it fits in,
#    still inside the allowance: 192 MB, and 40% of a CPU.
sudo mkdir -p /etc/systemd/system/shop-search.service.d
printf '[Service]\nMemoryMax=192M\nCPUQuota=40%%\n' | sudo tee /etc/systemd/system/shop-search.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-search
sleep 6
echo "--- restored:"
df -h /srv/shop | tail -1
from-office curl -s http://10.0.9.1:8080/
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
systemctl is-active shop-api shop-search
grep nr_throttled /sys/fs/cgroup/system.slice/shop-search.service/cpu.stat
journalctl -u shop-search -n 1 --no-pager
