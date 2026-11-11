cd /srv/gpu/box-1 && cat README && cat nvidia-smi.txt
grep -o '[0-9]*MiB / *[0-9]*MiB' nvidia-smi.txt
echo "$(( 81559 / 1024 )) GiB total, $(( 12450 * 100 / 81559 ))% in use"
grep -A 5 'Processes:' nvidia-smi.txt
awk -F, 'NR > 1 {s += $2; n++} END {print s / n}' gpu.csv
tail -n 1 gpu.csv
awk -F, 'NR > 1 && $2 == 0 {n++} END {print n, "of", NR - 1, "seconds idle"}' gpu.csv
cat mpstat.txt
cat iostat.txt
mkdir -p ~/example
echo "avg-util=$(awk -F, 'NR > 1 {s += $2; n++} END {printf "%.0f", s / n}' gpu.csv)" > ~/example/verdict.txt
echo "idle-seconds=$(awk -F, 'NR > 1 && $2 == 0 {n++} END {print n}' gpu.csv)" >> ~/example/verdict.txt
echo "mem-used-pct=$(( 12450 * 100 / 81559 ))" >> ~/example/verdict.txt
echo "starved-by=cpu" >> ~/example/verdict.txt
cat ~/example/verdict.txt
