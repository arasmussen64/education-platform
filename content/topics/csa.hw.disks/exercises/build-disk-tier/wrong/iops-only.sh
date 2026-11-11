# Wrong: only the writes-a-second cap, here and in the measurement. With
# no bytes cap, 1 MiB writes run at whatever the lab's disk can do, and
# the review says the writes cap binds at 1 MiB.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nIOWriteIOPSMax=/dev/lab/data 700\n' | sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
F="--name=t --filename=/srv/data/fio-test --size=16M --direct=1 --runtime=5 --time_based"
sudo systemd-run -q --wait --pipe -p "IOWriteIOPSMax=/dev/lab/data 700" fio $F --rw=write --bs=1M | grep 'IOPS='
printf 'disk-4k-iops=700\ndisk-1m-mib-per-s=700\ndisk-1m-binding=iops\ndisk-for.orders=network\ndisk-for.sort-scratch=local\ndisk-for.cache=local\n' > ~/review/answers.txt
