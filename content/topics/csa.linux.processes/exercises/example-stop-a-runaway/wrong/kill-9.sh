# Wrong: KILL ends the process at once; its trap never runs and nothing is
# cleaned up. TERM first.
kill -9 $(pgrep -x runaway.sh)
sleep 2; pgrep -a runaway || echo "it's gone"
mkdir -p ~/example && ps -o comm= -p 1 > ~/example/pid1.txt
