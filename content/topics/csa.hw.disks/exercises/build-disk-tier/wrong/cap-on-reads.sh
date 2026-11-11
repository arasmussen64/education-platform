# Wrong: the writes-a-second figure goes on reads (IOReadIOPSMax). The
# database hardly reads, so nothing holds its writes to 700 a second.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nIOReadIOPSMax=/dev/lab/data 700\nIOWriteBandwidthMax=/dev/lab/data 5242880\n' | sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
printf 'disk-4k-iops=700\ndisk-1m-mib-per-s=5\ndisk-1m-binding=throughput\ndisk-for.orders=network\ndisk-for.sort-scratch=local\ndisk-for.cache=local\n' > ~/review/answers.txt
