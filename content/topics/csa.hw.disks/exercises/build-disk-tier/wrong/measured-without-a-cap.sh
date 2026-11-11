# Wrong: the database is held to the tier, but fio ran with no cap, so
# the review gives the lab disk's numbers, a file on a fast computer, not
# the tier's.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nIOWriteIOPSMax=/dev/lab/data 700\nIOWriteBandwidthMax=/dev/lab/data 5242880\n' | sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
F="--name=t --filename=/srv/data/fio-test --size=16M --direct=1 --runtime=5 --time_based"
sudo fio $F --rw=randwrite --bs=4k | grep 'IOPS='
printf 'disk-4k-iops=22500\ndisk-1m-mib-per-s=900\ndisk-1m-binding=throughput\ndisk-for.orders=network\ndisk-for.sort-scratch=local\ndisk-for.cache=local\n' > ~/review/answers.txt
