# Wrong: the utilisation is the last second's, not the minute's. The card
# works in bursts, and the last second was a busy one: 54, where the mean
# over the minute is 18.
cd /srv/gpu/box-1
mkdir -p ~/example
echo "avg-util=$(tail -n 1 gpu.csv | cut -d, -f2)" > ~/example/verdict.txt
echo "idle-seconds=$(awk -F, 'NR > 1 && $2 == 0 {n++} END {print n}' gpu.csv)" >> ~/example/verdict.txt
echo "mem-used-pct=$(( 12450 * 100 / 81559 ))" >> ~/example/verdict.txt
echo "starved-by=cpu" >> ~/example/verdict.txt
