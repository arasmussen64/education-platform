# Wrong: all three put right on the running service only. set-property
# --runtime writes its settings under /run, which the next boot empties, and
# the unit still says 10%, 48M and CPU 0. It looks fixed until a restart.
sudo systemctl set-property --runtime shop-db CPUQuota=150% MemoryHigh=infinity "AllowedCPUs=$(cat /sys/devices/system/cpu/online)"
sleep 3
