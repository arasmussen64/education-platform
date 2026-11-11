# Wrong: the caps are set with set-property --runtime, which puts them
# under /run. The database is held to them now, and the next reboot
# forgets them.
sudo systemctl set-property --runtime shop-db "IOWriteIOPSMax=/dev/lab/data 700" "IOWriteBandwidthMax=/dev/lab/data 5242880"
printf 'disk-4k-iops=700\ndisk-1m-mib-per-s=5\ndisk-1m-binding=throughput\ndisk-for.orders=network\ndisk-for.sort-scratch=local\ndisk-for.cache=local\n' > ~/review/answers.txt
