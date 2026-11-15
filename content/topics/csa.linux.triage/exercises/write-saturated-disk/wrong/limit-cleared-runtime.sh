# Wrong: the trace is switched off, which is the right fix, but on the way
# the slice's limit was cleared with set-property --runtime and never put
# back. The setting sits under /run until the next reboot: for now the
# disk has no limit at all, so nothing measured on this server today says
# how it will behave tomorrow.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo systemctl set-property --runtime shop.slice "IOWriteIOPSMax=/dev/lab/data-backing infinity"
sudo sed -i 's/^TRACE=on$/TRACE=off/' /etc/shop/sync.conf
sudo systemctl restart shop-sync
sleep 3
