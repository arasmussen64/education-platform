# Wrong: the trace is switched off with a drop-in under /run, as
# "sudo systemctl edit --runtime shop-sync" makes one, pointing the
# service at a copy of its settings there. Everything is right until the
# next reboot, which forgets /run: the settings file in /etc still says
# TRACE=on, and the fault is back.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo mkdir -p /run/shop /run/systemd/system/shop-sync.service.d
sed 's/^TRACE=on$/TRACE=off/' /etc/shop/sync.conf | sudo tee /run/shop/sync.conf > /dev/null
printf '[Service]\nEnvironmentFile=\nEnvironmentFile=/run/shop/sync.conf\n' | sudo tee /run/systemd/system/shop-sync.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-sync
sleep 3
