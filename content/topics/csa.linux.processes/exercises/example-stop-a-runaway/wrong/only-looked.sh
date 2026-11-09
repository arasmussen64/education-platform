# Wrong: looked at the tree and noted PID 1, but never sent the signal.
ps -ef --forest | head -n 15
pgrep -a runaway
mkdir -p ~/example && ps -o comm= -p 1 > ~/example/pid1.txt
