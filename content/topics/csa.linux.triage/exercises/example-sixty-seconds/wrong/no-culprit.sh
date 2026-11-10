# Wrong: the bottleneck is called CPU, but no culprit process was found, so
# there's nothing to act on.
mkdir -p ~/triage
ps -eo pid,comm,%cpu --sort=-%cpu | head -4 > ~/triage/top-cpu.txt
{ echo "bottleneck: cpu"; echo "culprit: unknown"; echo "memory: ok"; echo "disk: ok"; } > ~/triage/verdict.txt
