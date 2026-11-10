# Wrong: guessed "memory" without checking; free -m and vmstat's si/so would
# have shown memory is fine. The verdict names the wrong resource.
mkdir -p ~/triage
ps -eo pid,comm,%cpu --sort=-%cpu | head -4 > ~/triage/top-cpu.txt
{ echo "bottleneck: memory"; echo "culprit: shop-worker"; echo "memory: low"; echo "disk: ok"; } > ~/triage/verdict.txt
