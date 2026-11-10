# Wrong: the verdict blames shop-logger, the disk writer, instead of the CPU
# hog. shop-logger does write steadily, but the disk isn't saturated and the
# machine is short of CPU, not disk.
mkdir -p ~/triage
ps -eo pid,comm,%cpu --sort=-%cpu | head -4 > ~/triage/top-cpu.txt
{ echo "bottleneck: disk"; echo "culprit: shop-logger"; echo "memory: ok"; echo "disk: saturated"; } > ~/triage/verdict.txt
