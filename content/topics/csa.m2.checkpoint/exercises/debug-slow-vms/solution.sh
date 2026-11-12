# A reference, one way among several. The order of questions is the one the
# cores topic taught, and the same for every VM: is CPU being stolen (st,
# %steal, the stat files)? is something capped (cpu.stat's throttled
# periods, memory.events' high count, io.max)? is something simply full
# (vmstat's r against the CPUs, free's available)? is it one thread
# (mpstat, CPU by CPU)? The first yes is the cause. printf '...\n' > FILE
# writes the three lines into FILE.
cd /srv/tickets
cat README.txt

# vm-a: st is about 70 on both vCPUs and us + sy about 30, which is the
# baseline of a burstable VM whose credits are spent. No quota, no memory
# trouble; the load of 2.4 on 2 CPUs is the stolen time, not a shortage.
# Steal over the minute: the eighth counter's growth over the first eight's.
cat vm-a/ticket.txt
head -5 vm-a/vmstat.txt
cat vm-a/cgroup/cpu.max
paste vm-a/stat-before.txt vm-a/stat-after.txt | awk '{for (i = 2; i <= 9; i++) t += $(i + 11) - $i; printf "%.1f\n", ($20 - $9) * 100 / t}'
printf 'cause=steal\nevidence=69.6\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-a.txt

# vm-b: no steal and 69% idle, but the API's cgroup has a quota of half a
# CPU, and in the minute it was throttled in 330 of 600 periods. (Since
# boot it is 8%, which hides it.)
cat vm-b/ticket.txt
cat vm-b/cgroup/cpu.max
paste vm-b/cgroup/cpu.stat.before vm-b/cgroup/cpu.stat.after
awk '$1 == "nr_periods" {p[FILENAME] = $2} $1 == "nr_throttled" {n[FILENAME] = $2} END {printf "%.1f\n", (n[ARGV[2]] - n[ARGV[1]]) * 100 / (p[ARGV[2]] - p[ARGV[1]])}' vm-b/cgroup/cpu.stat.before vm-b/cgroup/cpu.stat.after
printf 'cause=cpu-quota\nevidence=55\nfix=raise-cpu-quota\n' > ~/diagnosis/vm-b.txt

# vm-c: no steal, no quota, but 184 MiB available of 7,937, swapping in and
# out thousands of KiB a second, the stock app's cgroup held at its
# memory.high with the high count climbing, and memory pressure at 45%.
# The disk waits are the swapping, not a slow disk: io.max is empty.
cat vm-c/ticket.txt
cat vm-c/free.txt
head -5 vm-c/vmstat.txt
cat vm-c/cgroup/memory.high vm-c/cgroup/memory.current
grep high vm-c/cgroup/memory.events.before vm-c/cgroup/memory.events.after
cat vm-c/pressure/memory
printf 'cause=memory-pressure\nevidence=45.12\nfix=more-memory-or-raise-throttle\n' > ~/diagnosis/vm-c.txt

# vm-d: a quarter busy in all, which is one CPU of four at 99% user time
# while the other three idle: a program that does its work on one thread.
# No steal, no throttling, memory and pressure quiet.
cat vm-d/ticket.txt
grep Average vm-d/mpstat.txt
printf 'cause=single-thread\nevidence=99.1\nfix=fix-the-program\n' > ~/diagnosis/vm-d.txt

head ~/diagnosis/*.txt
