# Wrong: the disk's limit is lifted instead of the load being taken off
# it. The line in the server's io.max that holds the disk to 100 writes a
# second is rewritten to "max", and the trace is left on. Orders are quick
# on the lab machine, and on the cloud the disk would still hold the server
# to 100 writes a second: the lab no longer behaves like the server it
# stands in for.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
device=$(awk '/wiops=100/ {print $1}' /sys/fs/cgroup/io.max)
echo "$device wiops=max" | sudo tee /sys/fs/cgroup/io.max > /dev/null
sleep 3
