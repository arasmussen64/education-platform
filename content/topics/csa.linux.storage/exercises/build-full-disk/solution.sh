# 1. Who's using the space? df for the filesystem, du for the folders.
df -h /srv/shop
sudo du -sh /srv/shop/* | sort -rh
sudo rm /srv/shop/logs/old/*.log

# 2. The space du can't see: a deleted file something still holds open.
#    lsof +L1 names the process (PID), its file descriptor (FD) and the
#    file. Emptying the file through /proc/PID/fd/FD frees the space and
#    leaves the process running. (The lesson's `: > /proc/PID/fd/FD` does
#    the same; truncate is easier to run through sudo.)
sudo lsof +L1
pid=$(sudo lsof +L1 | awk '$(NF-1) ~ "^/srv/shop/" {print $2; exit}')
fd=$(sudo lsof +L1 | awk '$(NF-1) ~ "^/srv/shop/" {print $4; exit}' | tr -d 'rwu')
sudo truncate -s 0 /proc/$pid/fd/$fd
df -h /srv/shop

# 3. "No space left" with space free: out of inodes, not bytes.
df -h /srv/shop/uploads
df -i /srv/shop/uploads
sudo find /srv/shop/uploads/tmp -type f -delete
df -i /srv/shop/uploads

# 4. The volume is bigger; tell the filesystem, while it stays mounted.
sudo lab-grow data1 300M
sudo resize2fs /dev/lab/data1
df -h /srv/shop

# 5. The report.
mkdir -p ~/report && df -h /srv/shop > ~/report/df.txt && cat ~/report/df.txt
