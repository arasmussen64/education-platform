# The symptom: a test order takes over a second to save. And it isn't the
# CPU: the shop's processes use next to none of it.
curl -s localhost:8080/order
pidstat 1 2 | tail -n 4

# 1. The disk. findmnt gives the data disk's device, and iostat -x reports
# on that one disk, four times a second apart. The first report is the
# average since the machine started; the later ones are the last second
# each. They show about 100 writes a second (w/s), each waiting about a
# third of a second (w_await, in ms), about 32 requests in the queue
# (aqu-sz) and the disk busy 100% of the time (%util): saturated. Saved
# before anything is changed.
findmnt /srv/data
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
cat ~/triage/iostat-before.txt

# 2. The process. pidstat -d lists what each process writes (kB_wr/s):
# shop-sync writes about 400 kB a second, a hundred 4 kB writes, the whole
# of the disk's allowance, while using next to no CPU. lsof shows what it
# has open on the data disk: 32 trace files. Its unit names its settings
# file, and the file says what the trace is.
sudo pidstat -d 1 3 | tail -n 5
sudo lsof /srv/data | awk 'NR > 1 {print $1}' | sort | uniq -c
systemctl cat shop-sync | grep EnvironmentFile
cat /etc/shop/sync.conf
printf 'culprit: shop-sync\nwhat: its debug trace, left on since a closed ticket: 32 workers each writing a record of every product straight to the data disk, which is all of its 100 writes a second\n' > ~/triage/finding.txt

# 3. The fix: the trace goes off in the service's settings (in the lab
# you'd edit the file with sudo nano), and the service is restarted so it
# reads them. The settings file is what the next boot reads too. The
# slice's setting, the disk's limit, is left exactly as it was: the load
# comes off the disk, the limit doesn't.
systemctl cat shop.slice | grep IOWriteIOPSMax
sudo sed -i 's/^TRACE=on$/TRACE=off/' /etc/shop/sync.conf
sudo systemctl restart shop-sync

# Measure again: orders in a few milliseconds, the disk nearly idle, and
# shop-sync, no longer waiting for the disk, at its full 320 a second.
sleep 3
curl -s localhost:8080/order
iostat -x "$disk" 1 3 | tail -n 3
sleep 10
journalctl -u shop-sync -n 2 -o cat --no-pager
