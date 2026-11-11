# Wrong: all three are changed on the running service only (renice, and
# the cgroup's cpu.max and cpu.weight written directly), and the unit still
# says 5%, 19 and 1. It looks fixed now; the next restart or reboot brings
# every fault back.
pid=$(systemctl show shop-api -p MainPID --value)
sudo renice -n 0 -p "$pid" > /dev/null
echo "150000 100000" | sudo tee /sys/fs/cgroup/system.slice/shop-api.service/cpu.max > /dev/null
echo 100 | sudo tee /sys/fs/cgroup/system.slice/shop-api.service/cpu.weight > /dev/null
sleep 2
