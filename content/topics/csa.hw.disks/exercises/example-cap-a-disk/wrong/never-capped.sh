# Wrong: fio was only ever run without a cap, three times, and those are
# the numbers saved: a file on your own computer, behind its caches, not a
# disk held to an allowance.
F="--name=t --filename=/srv/data/fio-test --size=16M --direct=1 --runtime=5 --time_based"
sudo fio $F --rw=randwrite --bs=4k | grep -E 'IOPS=| lat .*avg'
printf '%s\n' 22500 41000 900 > ~/example/disk.txt
