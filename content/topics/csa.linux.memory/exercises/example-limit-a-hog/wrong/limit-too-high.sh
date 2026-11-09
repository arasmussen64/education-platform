# Wrong: with a 512 MB limit the hog fits, finishes, and nothing is learned
# about the OOM killer.
sudo systemd-run --unit=hog -p MemoryMax=512M -p MemorySwapMax=0 memhog 200 2
sleep 4
mkdir -p ~/example && systemctl show hog -p Result --value > ~/example/result.txt && grep '^MemAvailable:' /proc/meminfo > ~/example/available.txt
