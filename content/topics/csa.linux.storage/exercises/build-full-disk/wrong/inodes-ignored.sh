# Wrong: the uploads volume still has no inodes left; "No space left" was
# read as bytes, and bytes it had.
sudo rm /srv/shop/logs/old/*.log
pid=$(sudo lsof +L1 | awk '$(NF-1) ~ "^/srv/shop/" {print $2; exit}')
fd=$(sudo lsof +L1 | awk '$(NF-1) ~ "^/srv/shop/" {print $4; exit}' | tr -d 'rwu')
sudo truncate -s 0 /proc/$pid/fd/$fd
sudo lab-grow data1 300M
sudo resize2fs /dev/lab/data1
mkdir -p ~/report && df -h /srv/shop > ~/report/df.txt
