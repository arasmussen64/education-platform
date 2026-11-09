# Wrong: run as a service but with no limit, so it takes its 200 MB from a
# machine that has plenty and finishes happily.
sudo systemd-run --unit=hog memhog 200 2
sleep 4
mkdir -p ~/example && systemctl show hog -p Result --value > ~/example/result.txt && grep '^MemAvailable:' /proc/meminfo > ~/example/available.txt
