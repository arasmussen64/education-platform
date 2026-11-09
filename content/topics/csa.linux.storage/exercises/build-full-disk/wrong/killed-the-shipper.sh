# Wrong: stopping the shipper frees the space, and takes the shop's log
# shipping down with it.
sudo rm /srv/shop/logs/old/*.log
sudo systemctl stop log-shipper
sudo find /srv/shop/uploads/tmp -type f -delete
sudo lab-grow data1 300M
sudo resize2fs /dev/lab/data1
mkdir -p ~/report && df -h /srv/shop > ~/report/df.txt
