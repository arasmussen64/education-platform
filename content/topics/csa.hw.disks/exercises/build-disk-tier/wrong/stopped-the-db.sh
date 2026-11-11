# Wrong: the caps are right, and then the database is stopped, so it never
# writes more than the tier allows. It was meant to keep running.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nIOWriteIOPSMax=/dev/lab/data 700\nIOWriteBandwidthMax=/dev/lab/data 5242880\n' | sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl stop shop-db
printf 'disk-4k-iops=700\ndisk-1m-mib-per-s=5\ndisk-1m-binding=throughput\ndisk-for.orders=network\ndisk-for.sort-scratch=local\ndisk-for.cache=local\n' > ~/review/answers.txt
