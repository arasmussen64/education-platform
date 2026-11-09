# Wrong: the rotated logs are gone, but the deleted log the shipper holds
# open still takes its space, and nobody looked for it.
sudo rm /srv/shop/logs/old/*.log
sudo find /srv/shop/uploads/tmp -type f -delete
sudo lab-grow data1 300M
sudo resize2fs /dev/lab/data1
mkdir -p ~/report && df -h /srv/shop > ~/report/df.txt
