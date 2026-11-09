ps -ef --forest | head -n 15
pgrep -a runaway
kill $(pgrep -x runaway.sh)
sleep 2; pgrep -a runaway || echo "it's gone"
tail -n 3 /var/log/shop/runaway.log
mkdir -p ~/example && ps -o comm= -p 1 > ~/example/pid1.txt && cat ~/example/pid1.txt
