# Wrong: 5M for the bytes cap. To systemd that is 5,000,000 bytes a
# second, a little under the 5 MiB (5,242,880) the tier gives.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nIOWriteIOPSMax=/dev/lab/data 700\nIOWriteBandwidthMax=/dev/lab/data 5M\n' | sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
printf 'disk-4k-iops=700\ndisk-1m-mib-per-s=5\ndisk-1m-binding=throughput\ndisk-for.orders=network\ndisk-for.sort-scratch=local\ndisk-for.cache=local\n' > ~/review/answers.txt
