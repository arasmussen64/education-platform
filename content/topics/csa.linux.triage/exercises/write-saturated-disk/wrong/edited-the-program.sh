# Wrong: the trace is switched off by editing the program itself, so that
# it ignores its TRACE setting. Orders are quick, but the settings file
# still says TRACE=on, which is now a lie, and the next release of the
# program brings the trace, and the fault, straight back.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo sed -i 's/^trace = .*/trace = False/' /usr/local/bin/shop-sync
sudo systemctl restart shop-sync
sleep 3
