# The tier: 700 writes a second and 5 MiB a second.
cat /srv/review/disk-tier.txt
# 1. A drop-in holds the database to both, from /etc, so it lasts. 5 MiB is
#    5 x 1,048,576 = 5,242,880 bytes (systemd would read 5M as 5,000,000).
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nIOWriteIOPSMax=/dev/lab/data 700\nIOWriteBandwidthMax=/dev/lab/data 5242880\n' | sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
systemctl show shop-db -p IOWriteIOPSMax -p IOWriteBandwidthMax
# 2. fio under the same two caps, on a test file on the data disk.
F="--name=t --filename=/srv/data/fio-test --size=16M --direct=1 --runtime=5 --time_based"
sudo systemd-run -q --wait --pipe -p "IOWriteIOPSMax=/dev/lab/data 700" -p "IOWriteBandwidthMax=/dev/lab/data 5242880" fio $F --rw=randwrite --bs=4k | grep 'IOPS='
sudo systemd-run -q --wait --pipe -p "IOWriteIOPSMax=/dev/lab/data 700" -p "IOWriteBandwidthMax=/dev/lab/data 5242880" fio $F --rw=write --bs=1M | grep 'IOPS='
# They print IOPS=700 (4 KiB: 700 x 4 KiB is 2.7 MiB a second, under the
# bytes cap, so the writes cap binds) and IOPS=5, BW=5120KiB/s (1 MiB:
# 700 x 1 MiB would be 700 MiB a second, so the bytes cap binds: 5 MiB a
# second). The arithmetic gives the same without fio.
# 3. The only copy of the orders goes on a network disk, which keeps it
#    through a stop; scratch space and a cache that can be rebuilt go on
#    the local disk, which is fast, free and costs the network disk's
#    allowance nothing.
cat > ~/review/answers.txt <<'EOF'
disk-4k-iops=700
disk-1m-mib-per-s=5
disk-1m-binding=throughput
disk-for.orders=network
disk-for.sort-scratch=local
disk-for.cache=local
EOF
cat ~/review/answers.txt
