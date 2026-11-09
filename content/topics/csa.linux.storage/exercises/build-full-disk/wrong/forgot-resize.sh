# Wrong: the volume is bigger but the filesystem was never told, so df
# still shows the old size.
sudo rm /srv/shop/logs/old/*.log
pid=$(sudo lsof +L1 | awk '$(NF-1) ~ "^/srv/shop/" {print $2; exit}')
fd=$(sudo lsof +L1 | awk '$(NF-1) ~ "^/srv/shop/" {print $4; exit}' | tr -d 'rwu')
sudo truncate -s 0 /proc/$pid/fd/$fd
sudo find /srv/shop/uploads/tmp -type f -delete
sudo lab-grow data1 300M
mkdir -p ~/report && df -h /srv/shop > ~/report/df.txt
