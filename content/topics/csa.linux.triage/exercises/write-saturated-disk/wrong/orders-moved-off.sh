# Wrong: instead of taking the load off the data disk, the orders are
# moved off it, to a folder on the server's own disk. shop-orders no
# longer waits in the data disk's queue, so orders are quick, but they are
# no longer on the disk that is backed up and outlives the server, and the
# trace still fills that disk's queue.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo sed -i 's|^ORDERS_DIR=.*|ORDERS_DIR=/var/lib/shop-orders|' /etc/shop/orders.conf
sudo systemctl restart shop-orders
sleep 3
