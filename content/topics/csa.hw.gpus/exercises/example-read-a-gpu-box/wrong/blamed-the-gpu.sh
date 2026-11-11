# Wrong: the numbers are right, but the verdict blames nothing. A card at
# 18% with every vCPU flat out is waiting for its input, which the CPUs
# prepare; "none" is the verdict for a card that is itself the limit.
cd /srv/gpu/box-1
mkdir -p ~/example
echo "avg-util=$(awk -F, 'NR > 1 {s += $2; n++} END {printf "%.0f", s / n}' gpu.csv)" > ~/example/verdict.txt
echo "idle-seconds=$(awk -F, 'NR > 1 && $2 == 0 {n++} END {print n}' gpu.csv)" >> ~/example/verdict.txt
echo "mem-used-pct=$(( 12450 * 100 / 81559 ))" >> ~/example/verdict.txt
echo "starved-by=none" >> ~/example/verdict.txt
