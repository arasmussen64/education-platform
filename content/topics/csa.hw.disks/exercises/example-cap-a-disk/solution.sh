F="--name=t --filename=/srv/data/fio-test --size=16M --direct=1 --runtime=5 --time_based"
sudo fio $F --rw=randwrite --bs=4k | grep -E 'IOPS=| lat .*avg'
sudo systemd-run -q --wait --pipe -p "IOWriteIOPSMax=/dev/lab/data 500" fio $F --rw=randwrite --bs=4k | grep -E 'IOPS=| lat .*avg'
sudo systemd-run -q --wait --pipe -p "IOWriteIOPSMax=/dev/lab/data 500" fio $F --rw=randwrite --bs=4k --ioengine=libaio --iodepth=16 | grep -E 'IOPS=| lat .*avg'
sudo systemd-run -q --wait --pipe -p "IOWriteIOPSMax=/dev/lab/data 500" -p "IOWriteBandwidthMax=/dev/lab/data 8M" fio $F --rw=write --bs=1M | grep -E 'IOPS=| lat .*avg'
sudo systemd-run -q --wait --pipe -p "IOWriteIOPSMax=/dev/lab/data 500" -p "IOWriteBandwidthMax=/dev/lab/data 8M" fio $F --rw=randwrite --bs=4k | grep -E 'IOPS=| lat .*avg'
systemctl show shop-db -p IOWriteIOPSMax; cat /sys/fs/cgroup/system.slice/shop-db.service/io.max
grep -o 'wios=[0-9]*' /sys/fs/cgroup/system.slice/shop-db.service/io.stat; sleep 5; grep -o 'wios=[0-9]*' /sys/fs/cgroup/system.slice/shop-db.service/io.stat; cat /sys/fs/cgroup/system.slice/shop-db.service/io.pressure
printf '%s\n' 500 503 7 > ~/example/disk.txt; cat ~/example/disk.txt
