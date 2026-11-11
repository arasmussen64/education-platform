#!/bin/bash
# Lays down the capacity review under /srv/review. Everything here is
# constructed, not captured: written in the real layouts (the kernel's /proc
# and /sys, vmstat, mpstat, the pressure files, AWS's price list) with
# invented numbers, from arithmetic on counters, never from randomness, so
# the checks work out every right answer from the same files.
set -euo pipefail

# mask_of TOTAL CPU...: the kernel's hexadecimal mask of a set of CPUs, as in
# topology/thread_siblings: groups of 32 CPUs, the highest group first. lscpu
# reads the masks, not the lists, so both are written.
mask_of() {
  local total=$1 group word cpu out=""
  shift
  for ((group = (total + 31) / 32 - 1; group >= 0; group--)); do
    word=0
    for cpu in "$@"; do
      if ((cpu / 32 == group)); then word=$((word | (1 << (cpu % 32)))); fi
    done
    out+=$(printf '%08x' "$word")
    if ((group > 0)); then out+=","; fi
  done
  echo "$out"
}

# list_of CPU...: the kernel's list form of the same set, like 0-23,48-71.
list_of() {
  local out="" start="" prev="" cpu
  for cpu in $(printf '%s\n' "$@" | sort -n); do
    if [ -z "$start" ]; then
      start=$cpu
    elif ((cpu != prev + 1)); then
      out+="${out:+,}$(span "$start" "$prev")"
      start=$cpu
    fi
    prev=$cpu
  done
  echo "${out:+$out,}$(span "$start" "$prev")"
}
span() { if (($1 == $2)); then echo "$1"; else echo "$1-$2"; fi; }

# machine DIR SOCKETS CORES_PER_SOCKET THREADS_PER_CORE KIND
# KIND is x86 or arm. Each socket is one NUMA node. CPUs are numbered as Linux
# numbers most x86 servers: the first thread of every core, socket by socket,
# then the second threads in the same order, so CPU 0's sibling on a 96-CPU
# machine is CPU 48.
machine() {
  local dir=$1 sockets=$2 cores=$3 threads=$4 kind=$5
  local total=$((sockets * cores * threads)) firsts=$((sockets * cores))
  local sys="$dir/sys/devices/system" cpu thread socket core x y
  mkdir -p "$sys/cpu" "$sys/node" "$dir/proc"
  for name in possible present online; do echo "0-$((total - 1))" > "$sys/cpu/$name"; done
  : > "$dir/proc/cpuinfo"
  for ((cpu = 0; cpu < total; cpu++)); do
    thread=$((cpu / firsts))
    socket=$(((cpu % firsts) / cores))
    core=$((cpu % cores))
    local siblings=() package=()
    for ((x = 0; x < threads; x++)); do siblings+=($((x * firsts + socket * cores + core))); done
    for ((x = 0; x < threads; x++)); do
      for ((y = 0; y < cores; y++)); do package+=($((x * firsts + socket * cores + y))); done
    done
    local topology="$sys/cpu/cpu$cpu/topology"
    mkdir -p "$topology"
    echo 1 > "$sys/cpu/cpu$cpu/online"
    echo "$socket" > "$topology/physical_package_id"
    echo "$core" > "$topology/core_id"
    echo 0 > "$topology/die_id"
    mask_of "$total" "${siblings[@]}" > "$topology/thread_siblings"
    list_of "${siblings[@]}" > "$topology/thread_siblings_list"
    mask_of "$total" "${package[@]}" > "$topology/core_siblings"
    list_of "${package[@]}" > "$topology/core_siblings_list"
    cp "$topology/thread_siblings" "$topology/core_cpus"
    cp "$topology/thread_siblings_list" "$topology/core_cpus_list"
    cp "$topology/core_siblings" "$topology/package_cpus"
    cp "$topology/core_siblings_list" "$topology/package_cpus_list"
    if [ "$kind" = x86 ]; then
      printf 'processor\t: %d\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 143\nmodel name\t: Intel(R) Xeon(R) Platinum (constructed)\nphysical id\t: %d\nsiblings\t: %d\ncore id\t\t: %d\ncpu cores\t: %d\nflags\t\t: fpu sse sse2 ht hypervisor\n\n' \
        "$cpu" "$socket" $((cores * threads)) "$core" "$cores" >> "$dir/proc/cpuinfo"
    else
      printf 'processor\t: %d\nBogoMIPS\t: 2100.00\nFeatures\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics\nCPU implementer\t: 0x41\nCPU architecture: 8\nCPU variant\t: 0x1\nCPU part\t: 0xd0c\nCPU revision\t: 1\n\n' \
        "$cpu" >> "$dir/proc/cpuinfo"
    fi
  done
  for ((socket = 0; socket < sockets; socket++)); do
    local members=()
    for ((cpu = 0; cpu < total; cpu++)); do
      if (((cpu % firsts) / cores == socket)); then members+=("$cpu"); fi
    done
    mkdir -p "$sys/node/node$socket"
    mask_of "$total" "${members[@]}" > "$sys/node/node$socket/cpumap"
    list_of "${members[@]}" > "$sys/node/node$socket/cpulist"
  done
  echo "0-$((sockets - 1))" > "$sys/node/online"
  echo "0-$((sockets - 1))" > "$sys/node/possible"
}


review=/srv/review

# --- Three machines the shop is moving ------------------------------------------
# app-1: 1 socket x 4 cores x 2 threads = 8 CPUs. db-2: 2 sockets x 16 cores
# x 2 threads = 64 CPUs on 2 NUMA nodes; CPU 40 is a second thread of a core
# on socket 0, so it is on node 0 though it is past the middle. arm-2: 16
# cores of 1 thread.
machine $review/machines/app-1 1 4 2 x86
machine $review/machines/db-2 2 16 2 x86
machine $review/machines/arm-2 1 16 1 arm

# --- The admin tool, proposed for a burstable size --------------------------------
# A t3.large (AWS's table, read 2026-11-11: 2 vCPUs, a baseline of 30% a vCPU,
# 36 credits an hour, at most 864), 250 credits at midnight, and a day of its
# minutes: a quiet night, a long busy working day, a quiet evening, a nightly
# job, and quiet again.
mkdir -p $review/burst
cat > $review/burst/instance.conf <<'EOF'
# shop-admin's proposed instance: a t3.large in standard mode
vcpus=2
baseline_pct=30
start_credits=250
max_credits=864
EOF
{
  echo "minute,cpu_pct"
  while read -r from to pct; do
    for ((minute = from; minute <= to; minute++)); do echo "$minute,$pct"; done
  done <<'EOF'
1 420 12
421 900 88
901 1140 20
1141 1260 75
1261 1440 10
EOF
} > $review/burst/usage.csv

# --- Two readings of the reporting server's /proc/stat, ten minutes apart ---------
# 4 vCPUs: 600 seconds x 100 ticks x 4 = 240,000 ticks, of which 26,400 were
# stolen (11.0%). Since boot, about 1.3% has been.
echo "cpu  48211000 2100 7140500 98760300 410200 0 512800 2003100 0 0" > $review/stat-before.txt
echo "cpu  48307000 2100 7154900 98858700 412600 0 515200 2029500 0 0" > $review/stat-after.txt

# --- The web server's week, and the sizes it could move to ------------------------
# A week of 5-minute samples (7 x 24 x 12 = 2,016) from its current machine,
# an m7i.4xlarge (16 vCPUs, 64 GiB): CPU as a percentage of those 16 vCPUs,
# and memory in use in GiB. Quiet nights, a working day, a busy evening on
# weekdays, lighter weekends, and on Saturday one runaway report.
mkdir -p $review/sizing
awk 'BEGIN {
  print "sample,cpu_pct,mem_gib"
  for (i = 1; i <= 2016; i++) {
    j = i - 1; day = int(j / 288); hour = int((j % 288) / 12)
    evening = (hour >= 18 && hour < 22)
    if (hour < 7) cpu = 3 + (j % 5) * 0.4
    else if (hour < 18) cpu = 8 + (j % 7) * 0.5
    else if (evening) cpu = 15 + (j * 7) % 11
    else cpu = 5 + (j % 3) * 0.5
    if (day >= 5) cpu = cpu * 0.6
    mem = 8 + (evening ? 3.4 : 0) + (j % 9) * 0.1
    if (i == 820) cpu = 41
    if (i == 1500) { cpu = 64; mem = 13.2 }
    if (i == 1501) cpu = 41
    printf "%d,%.1f,%.1f\n", i, cpu, mem
  }
}' > $review/sizing/metrics.csv
# The sizes, from AWS's public price file for US East (N. Virginia), Linux,
# on-demand, published 2026-11-10 and read 2026-11-11
# (https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20(N.%20Virginia)/Linux/index.json).
cat > $review/sizing/sizes.csv <<'EOF'
instance,vcpus,mem_gib,usd_per_hour
m7i.large,2,8,0.1008
m7i.xlarge,4,16,0.2016
m7i.2xlarge,8,32,0.4032
m7i.4xlarge,16,64,0.8064
c7i.xlarge,4,8,0.1785
c7i.2xlarge,8,16,0.357
r7i.large,2,16,0.1323
r7i.xlarge,4,32,0.2646
r7i.2xlarge,8,64,0.5292
EOF

# --- A ticket: a VM that is simply too small --------------------------------------
# What an on-call script saved from a 4-vCPU fixed-size VM while its export
# ran: the same files a slow VM's ticket always has, so the file list gives
# nothing away.
t=$review/ticket
mkdir -p $t/pressure $t/cgroup
cat > $t/ticket.txt <<'EOF'
Ticket 4471, from the finance team:
"The order export used to take twenty minutes. Since the two new shops
joined last month it takes an hour, and the whole machine is sluggish
while it runs."

The VM: shop-export, 4 vCPUs, 16 GiB, a fixed-size (not burstable) instance.
The export runs as the service shop-export; cgroup/ holds its files.
Everything here was saved while the export was running.
EOF
cat > $t/lscpu.txt <<'EOF'
Architecture:                         x86_64
CPU op-mode(s):                       32-bit, 64-bit
Byte Order:                           Little Endian
CPU(s):                               4
On-line CPU(s) list:                  0-3
Vendor ID:                            GenuineIntel
Model name:                           Intel(R) Xeon(R) Platinum (constructed)
Thread(s) per core:                   2
Core(s) per socket:                   2
Socket(s):                            1
Hypervisor vendor:                    KVM
Virtualization type:                  full
NUMA node(s):                         1
NUMA node0 CPU(s):                    0-3
EOF
# vmstat 1 for sixty seconds, in Ubuntu 24.04's layout (gu is the last column).
{
  echo "procs -----------memory---------- ---swap-- -----io---- -system-- -------cpu-------"
  echo " r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st gu"
  for ((j = 0; j < 60; j++)); do
    r=$((8 + (j * 7) % 5 + (j % 6 == 0 ? 1 : 0)))
    us=$((86 + j % 4)); sy=$((12 - j % 4 - (j % 5 == 0 ? 1 : 0))); id=$((100 - us - sy))
    printf '%2d %2d %6d %6d %6d %6d %4d %4d %5d %5d %4d %4d %2d %2d %2d %2d %2d %2d\n' \
      "$r" 0 0 $((3912000 - j * 97)) 210448 8120332 0 0 $((16 + j % 9)) $((132 + j % 13)) $((4100 + j * 3)) $((5800 + j * 11)) "$us" "$sy" "$id" 0 0 0
  done
} > $t/vmstat.txt
# mpstat -P ALL 60 1: every CPU busy, none of it stolen.
{
  printf 'Linux 6.8.0-1017-aws (shop-export) \t11/04/26 \t_x86_64_\t(4 CPU)\n\n'
  for label in 14:03:11 Average:; do
    printf '%s     CPU    %%usr   %%nice    %%sys %%iowait    %%irq   %%soft  %%steal  %%guest  %%gnice   %%idle\n' "$label"
    printf '%s     all   87.42    0.00   11.31    0.02    0.00    0.48    0.05    0.00    0.00    0.72\n' "$label"
    printf '%s       0   88.10    0.00   10.92    0.00    0.00    0.33    0.03    0.00    0.00    0.62\n' "$label"
    printf '%s       1   86.95    0.00   11.70    0.05    0.00    0.52    0.07    0.00    0.00    0.71\n' "$label"
    printf '%s       2   87.36    0.00   11.28    0.02    0.00    0.61    0.05    0.00    0.00    0.68\n' "$label"
    printf '%s       3   87.27    0.00   11.34    0.01    0.00    0.46    0.05    0.00    0.00    0.87\n' "$label"
    echo
  done
} > $t/mpstat.txt
# /proc/stat's first line, sixty seconds apart: 4 x 6,000 = 24,000 ticks.
echo "cpu  9120400 300 1210800 40213500 8100 0 52200 2400 0 0" > $t/stat-before.txt
echo "cpu  9141380 300 1213520 40213670 8105 0 52313 2412 0 0" > $t/stat-after.txt
printf 'some avg10=71.42 avg60=69.80 avg300=55.13 total=842113520\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n' > $t/pressure/cpu
printf 'some avg10=0.00 avg60=0.00 avg300=0.00 total=1204511\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=880213\n' > $t/pressure/memory
printf 'some avg10=0.31 avg60=0.28 avg300=0.22 total=9033120\nfull avg10=0.12 avg60=0.10 avg300=0.08 total=3301870\n' > $t/pressure/io
echo "max 100000" > $t/cgroup/cpu.max
printf 'usage_usec 801224000\nuser_usec 702310000\nsystem_usec 98914000\nnr_periods 0\nnr_throttled 0\nthrottled_usec 0\n' > $t/cgroup/cpu.stat.before
printf 'usage_usec 1003117000\nuser_usec 880102000\nsystem_usec 123015000\nnr_periods 0\nnr_throttled 0\nthrottled_usec 0\n' > $t/cgroup/cpu.stat.after
echo "max" > $t/cgroup/memory.max
echo "max" > $t/cgroup/memory.high
echo "2306867200" > $t/cgroup/memory.current
for when in before after; do
  printf 'low 0\nhigh 0\nmax 0\noom 0\noom_kill 0\noom_group_kill 0\n' > $t/cgroup/memory.events.$when
done
cat > $t/dmesg.txt <<'EOF'
[    0.000000] Linux version 6.8.0-1017-aws (buildd@lcy02-amd64-031) (x86_64-linux-gnu-gcc-13 (Ubuntu 13.2.0-23ubuntu4) 13.2.0) #18-Ubuntu SMP
[    0.000000] Hypervisor detected: KVM
[    2.114209] EXT4-fs (nvme0n1p1): mounted filesystem with ordered data mode. Quota mode: none.
[    3.902114] ena 0000:00:05.0 ens5: renamed from eth0
[ 5021.553310] systemd-journald[201]: Time spent on flushing to /var/log/journal is 1.226ms
EOF
cat > $t/README <<'EOF'
What the on-call script saved from shop-export while the export ran.
Constructed, not captured: every file is in the real layout of the tool or
kernel file it is named after (Ubuntu 24.04's vmstat and mpstat, the
kernel's pressure and cgroup files), with invented numbers. The .before and
.after files, and stat-before.txt and stat-after.txt, are sixty seconds
apart.
EOF

# --- The brief's rules ------------------------------------------------------------
cat > $review/README.txt <<'EOF'
The capacity review: what goes in ~/review/answers.txt
======================================================

One key=value line for each key below; ~/review/answers.txt lists the keys.

Machines (machines/app-1, db-2, arm-2: copies of each one's /proc and /sys,
for lscpu --sysroot)
  cores.app-1, cores.db-2, cores.arm-2   physical cores in each machine
  numa-nodes.db-2                       how many NUMA nodes db-2 has
  node-of-cpu-40.db-2                   the NUMA node CPU 40 of db-2 is on

The reporting server (stat-before.txt, stat-after.txt: its /proc/stat first
line, ten minutes apart)
  steal-pct    the share of those ten minutes that was stolen, in %, to one
               decimal place

The admin tool's proposed burstable instance (burst/instance.conf and
burst/usage.csv, one line a minute for a day; minutes count from 1)
  credits-empty-minute       the first minute at whose end the balance is 0
                             or less, or "never"
  minutes-held-to-baseline   the minutes that end with the balance at 0
                             while the tool asked for more CPU than the
                             baseline
  (Each minute the instance earns vcpus x baseline / 100 credits and spends
  vcpus x cpu_pct / 100; the balance never goes below 0 or above
  max_credits.)

The web server (sizing/metrics.csv: a week of 5-minute samples from its
current m7i.4xlarge, 16 vCPUs, CPU as a percentage of those 16; sizing/
sizes.csv: the sizes it may move to)
  size.web   the cheapest size in sizes.csv that meets the shop's policy:
             - CPU: the 95th percentile of cpu_pct, as vCPUs of the current
               machine, is at most 70% of the new size's vCPUs;
             - memory: the largest mem_gib is at most 75% of the new size's
               memory.
             The 95th percentile here is the nearest-rank one: sort the
             samples from smallest to largest and take the one at position
             95% of the count, rounded up.
  The prices in sizes.csv are AWS's on-demand prices for Linux in US East
  (N. Virginia), in US dollars an hour, read on 2026-11-11 from AWS's public
  price list. Today's are at https://aws.amazon.com/ec2/pricing/on-demand/
  and will differ.

The ticket (ticket/: what was saved from a slow VM, and the ticket itself)
  ticket.cause      one of: steal, cpu-quota, memory-pressure, disk-cap,
                    too-few-cpus, single-thread, healthy
  ticket.evidence   the one number that shows the cause:
                      steal            the steal % between the two stat files
                      cpu-quota        the % of periods throttled between the
                                       two cpu.stat files
                      memory-pressure  some avg10 in pressure/memory
                      disk-cap         writes a second between two io.stat
                                       readings (the next topic, Memory
                                       tiers and disks, teaches this one)
                      too-few-cpus     the average of vmstat's r column
                      single-thread    the busiest CPU's %usr in mpstat
                      healthy          0
  ticket.fix        one of: fixed-size-or-unlimited, dedicated-host,
                    raise-cpu-quota, more-memory-or-raise-throttle,
                    faster-disk-tier, more-vcpus, fix-the-program, nothing

Numbers may be written with or without decimals. steal-pct and
ticket.evidence are checked to within 0.5; the rest exactly.
EOF

mkdir -p /home/learner/review
cat > /home/learner/review/answers.txt <<'EOF'
cores.app-1=
cores.db-2=
cores.arm-2=
numa-nodes.db-2=
node-of-cpu-40.db-2=
steal-pct=
credits-empty-minute=
minutes-held-to-baseline=
size.web=
ticket.cause=
ticket.evidence=
ticket.fix=
EOF
chown -R learner:learner /home/learner/review
chmod -R a+rX $review

# The checksum of everything under /srv/review, for the check that keeps the
# evidence as it was (the learner has sudo). Root's alone.
mkdir -p /usr/local/lib/lab
(cd $review && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1) > /usr/local/lib/lab/review.sha256
chmod 600 /usr/local/lib/lab/review.sha256
