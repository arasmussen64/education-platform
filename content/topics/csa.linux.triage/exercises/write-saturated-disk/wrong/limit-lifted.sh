# Wrong: the disk's limit is lifted instead of the load being taken off
# it. set-property gives shop.slice a setting of "infinity" for the disk,
# which takes effect at once and is kept for every boot after, and the
# trace is left on. Orders are quick on the lab machine, and on the cloud
# the disk would still hold the server to 100 writes a second: the lab no
# longer behaves like the server it stands in for.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo systemctl set-property shop.slice "IOWriteIOPSMax=/dev/lab/data-backing infinity"
sleep 3
