# Wrong: the fix is right, but the finding names shop-orders, the service
# that is slow, instead of the one whose writes fill the disk's queue. The
# slow service is where the symptom shows, not where the cause is, and the
# next person is sent the wrong way.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-orders\nwhat: it takes over a second to save an order\n' > ~/triage/finding.txt
sudo sed -i 's/^TRACE=on$/TRACE=off/' /etc/shop/sync.conf
sudo systemctl restart shop-sync
sleep 3
