#!/bin/bash
# Lays down four slow VMs' evidence under /srv/tickets, and the learner's
# four answer files. Everything here is constructed, not captured: written in
# the real layouts (Ubuntu 24.04's vmstat, mpstat, free and uptime, the
# kernel's /proc/stat, pressure and cgroup files) with invented numbers, from
# arithmetic on counters, never from randomness, so the checks work out
# every right answer from the same files. Every folder holds the same files,
# so the list gives nothing away.
set -euo pipefail

t=/srv/tickets

# vmstat_lines R B SWPD FREE BUFF CACHE SI SO BI BO US SY ID WA ST: sixty
# lines of vmstat 1 in Ubuntu 24.04's layout (gu is the last column), each
# value nudged a little from line to line, as a real minute is.
vmstat_lines() {
  local r=$1 b=$2 swpd=$3 free=$4 buff=$5 cache=$6 si=$7 so=$8 bi=$9 bo=${10}
  local us=${11} sy=${12} id=${13} wa=${14} st=${15} j
  echo "procs -----------memory---------- ---swap-- -----io---- -system-- -------cpu-------"
  echo " r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st gu"
  for ((j = 0; j < 60; j++)); do
    local nudge=$(((j * 7) % 3 - 1)) rr=$((r + (j % 5 == 0 ? 1 : 0) - (j % 7 == 0 ? 1 : 0)))
    local uu=$((us + nudge)) ii=$((id - nudge))
    if ((ii < 0)); then uu=$((uu + ii)); ii=0; fi
    printf '%2d %2d %6d %6d %6d %6d %4d %4d %5d %5d %4d %4d %2d %2d %2d %2d %2d %2d\n' \
      $((rr < 0 ? 0 : rr)) "$b" "$swpd" $((free + (j * 13) % 41)) "$buff" $((cache + (j * 5) % 17)) \
      $((si > 0 ? si + (j * 37) % 211 : 0)) $((so > 0 ? so + (j * 29) % 173 : 0)) \
      $((bi + (j * 11) % 23)) $((bo + (j * 17) % 31)) $((1200 + (j * 19) % 97)) $((2100 + (j * 23) % 131)) \
      "$uu" "$sy" "$ii" "$wa" "$st" 0
  done
}

# mpstat_file HOST CPUS LINE...: mpstat -P ALL 60 1, the same rows under the
# first header and under Average. Each LINE is one CPU's row of numbers, the
# first for "all".
mpstat_file() {
  local host=$1 cpus=$2 label line cpu
  shift 2
  printf 'Linux 6.8.0-1017 (%s) \t11/09/26 \t_x86_64_\t(%d CPU)\n\n' "$host" "$cpus"
  for label in 14:02:10 Average:; do
    printf '%-8s     CPU    %%usr   %%nice    %%sys %%iowait    %%irq   %%soft  %%steal  %%guest  %%gnice   %%idle\n' "$label"
    cpu=all
    for line in "$@"; do
      # shellcheck disable=SC2086
      printf '%-8s %7s %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f\n' "$label" "$cpu" $line
      if [ "$cpu" = all ]; then cpu=0; else cpu=$((cpu + 1)); fi
    done
    echo
  done
}

lscpu_file() {
  local cpus=$1 threads=$2
  cat <<EOF
Architecture:                         x86_64
CPU op-mode(s):                       32-bit, 64-bit
Byte Order:                           Little Endian
CPU(s):                               $cpus
On-line CPU(s) list:                  0-$((cpus - 1))
Vendor ID:                            GenuineIntel
Model name:                           Intel(R) Xeon(R) Platinum (constructed)
Thread(s) per core:                   $threads
Core(s) per socket:                   $((cpus / threads))
Socket(s):                            1
Hypervisor vendor:                    KVM
Virtualization type:                  full
NUMA node(s):                         1
NUMA node0 CPU(s):                    0-$((cpus - 1))
EOF
}

dmesg_file() {
  cat <<'EOF'
[    0.000000] Linux version 6.8.0-1017 (buildd@lcy02-amd64-031) (x86_64-linux-gnu-gcc-13 (Ubuntu 13.2.0-23ubuntu4) 13.2.0) #18-Ubuntu SMP
[    0.000000] Hypervisor detected: KVM
[    2.114209] EXT4-fs (nvme0n1p1): mounted filesystem with ordered data mode. Quota mode: none.
[    3.902114] ens5: renamed from eth0
EOF
}

# The cgroup files a slow service always has, given its numbers.
cgroup_files() {
  local d=$1/cgroup
  mkdir -p "$d"
  echo "$2" > "$d/cpu.max"
  echo "$3" > "$d/memory.max"
  echo "$4" > "$d/memory.high"
  echo "$5" > "$d/memory.current"
  : > "$d/io.max"
}

cpu_stat() {
  printf 'usage_usec %d\nuser_usec %d\nsystem_usec %d\nnr_periods %d\nnr_throttled %d\nthrottled_usec %d\nnr_bursts 0\nburst_usec 0\n' "$@"
}

mem_events() {
  printf 'low 0\nhigh %d\nmax 0\noom 0\noom_kill 0\noom_group_kill 0\n' "$1"
}

io_stat() {
  printf '259:0 rbytes=%d wbytes=%d rios=%d wios=%d dbytes=0 dios=0\n' "$@"
}

mkdir -p "$t"

# --- vm-a ------------------------------------------------------------------------
# 2 vCPUs: 60 s x 100 ticks x 2 = 12,000 ticks between the stat files, of
# which 8,352 were stolen (69.6%); since boot, 4.2% has been. The report
# gets about the 30% it is due, and a load of 2.4 on 2 CPUs.
v=$t/vm-a
mkdir -p "$v/pressure"
cat > "$v/ticket.txt" <<'EOF'
Ticket 5102, from the reporting team:
"The nightly report took 40 minutes for a year. Since Tuesday it takes two
hours, and nothing about the report has changed."

The VM: vm-a, 2 vCPUs, 8 GiB, a burstable instance: a baseline of 30% of
each vCPU, in standard mode (it doesn't buy CPU beyond its credits).
Its CPU credit balance when this was saved: 0.
The report runs as the service report; cgroup/ holds its files.
Everything here was saved while the report was running.
EOF
lscpu_file 2 2 > "$v/lscpu.txt"
echo " 01:12:40 up 9 days,  6:03,  0 users,  load average: 2.41, 2.38, 2.20" > "$v/uptime.txt"
printf '               total        used        free      shared  buff/cache   available\nMem:            7937        2104        3811          18        2022        5833\nSwap:              0           0           0\n' > "$v/free.txt"
vmstat_lines 2 0 0 3902000 120400 1938000 0 0 12 40 27 3 0 0 70 > "$v/vmstat.txt"
mpstat_file vm-a 2 \
  "26.70 0.00 3.20 0.15 0.00 0.05 69.60 0.00 0.00 0.30" \
  "26.95 0.00 3.05 0.10 0.00 0.05 69.55 0.00 0.00 0.30" \
  "26.45 0.00 3.35 0.20 0.00 0.05 69.65 0.00 0.00 0.30" > "$v/mpstat.txt"
echo "cpu  1800000 200 210000 9800000 15000 0 8000 520000 0 0" > "$v/stat-before.txt"
echo "cpu  1803204 200 210384 9800036 15018 0 8006 528352 0 0" > "$v/stat-after.txt"
printf 'some avg10=38.40 avg60=37.95 avg300=31.12 total=922113520\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n' > "$v/pressure/cpu"
printf 'some avg10=0.00 avg60=0.00 avg300=0.00 total=104511\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=80213\n' > "$v/pressure/memory"
printf 'some avg10=0.12 avg60=0.10 avg300=0.08 total=3033120\nfull avg10=0.05 avg60=0.04 avg300=0.03 total=1301870\n' > "$v/pressure/io"
cgroup_files "$v" "max 100000" max max 734003200
cpu_stat 41234000000 36110000000 5124000000 0 0 0 > "$v/cgroup/cpu.stat.before"
cpu_stat 41269920000 36142000000 5127920000 0 0 0 > "$v/cgroup/cpu.stat.after"
mem_events 0 > "$v/cgroup/memory.events.before"
mem_events 0 > "$v/cgroup/memory.events.after"
io_stat 1840000000 9200000000 41000 260000 > "$v/cgroup/io.stat.before"
io_stat 1840200000 9203100000 41012 260190 > "$v/cgroup/io.stat.after"
dmesg_file > "$v/dmesg.txt"

# --- vm-b ------------------------------------------------------------------------
# 4 vCPUs: 24,000 ticks, 30% busy and no steal. The API's cgroup was throttled
# in 330 of the minute's 600 periods (55%), though in only 8.2% of all its
# periods since boot, so the totals mislead.
v=$t/vm-b
mkdir -p "$v/pressure"
cat > "$v/ticket.txt" <<'EOF'
Ticket 5117, from a customer's developers:
"Our API answers in bursts: quick for a moment, then nothing for a fraction
of a second, all day long, since Monday's deploy. The VM looks mostly idle,
so it can't be short of CPU."

The VM: vm-b, 4 vCPUs, 16 GiB, a fixed-size (not burstable) instance.
The API runs as the service api; cgroup/ holds its files.
Everything here was saved while the API was busy.
EOF
lscpu_file 4 2 > "$v/lscpu.txt"
echo " 11:40:05 up 31 days,  2:18,  1 user,  load average: 1.12, 1.08, 1.03" > "$v/uptime.txt"
printf '               total        used        free      shared  buff/cache   available\nMem:           15951        3540         412          22       12309       12411\nSwap:              0           0           0\n' > "$v/free.txt"
vmstat_lines 1 0 0 421000 310200 12290000 0 0 8 52 27 3 69 1 0 > "$v/vmstat.txt"
mpstat_file vm-b 4 \
  "27.00 0.00 3.00 0.50 0.00 0.50 0.00 0.00 0.00 69.00" \
  "27.40 0.00 2.90 0.40 0.00 0.50 0.00 0.00 0.00 68.80" \
  "26.70 0.00 3.10 0.60 0.00 0.40 0.00 0.00 0.00 69.20" \
  "27.10 0.00 3.00 0.50 0.00 0.60 0.00 0.00 0.00 68.80" \
  "26.80 0.00 3.00 0.50 0.00 0.50 0.00 0.00 0.00 69.20" > "$v/mpstat.txt"
echo "cpu  30000000 1000 3400000 80000000 300000 0 200000 0 0 0" > "$v/stat-before.txt"
echo "cpu  30006480 1000 3400720 80016560 300120 0 200120 0 0 0" > "$v/stat-after.txt"
printf 'some avg10=22.51 avg60=21.98 avg300=20.40 total=4411320011\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n' > "$v/pressure/cpu"
printf 'some avg10=0.00 avg60=0.00 avg300=0.00 total=210044\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=180113\n' > "$v/pressure/memory"
printf 'some avg10=0.08 avg60=0.07 avg300=0.06 total=5033120\nfull avg10=0.02 avg60=0.02 avg300=0.02 total=2101870\n' > "$v/pressure/io"
cgroup_files "$v" "50000 100000" 4294967296 max 1288490188
cpu_stat 912345678000 801234567000 111111111000 1204300 98410 7012345678 > "$v/cgroup/cpu.stat.before"
cpu_stat 912375678000 801261567000 111114111000 1204900 98740 7028845678 > "$v/cgroup/cpu.stat.after"
mem_events 0 > "$v/cgroup/memory.events.before"
mem_events 0 > "$v/cgroup/memory.events.after"
io_stat 2210000000 7400000000 52000 199000 > "$v/cgroup/io.stat.before"
io_stat 2210100000 7401900000 52006 199120 > "$v/cgroup/io.stat.after"
dmesg_file > "$v/dmesg.txt"

# --- vm-c ------------------------------------------------------------------------
# 4 vCPUs, 8 GiB: 2.3% of memory available, swapping in and out by
# thousands of KiB a second, 35% of the time waiting on the disk (which is
# the swapping), the stock app's cgroup held at its memory.high and its high
# count climbing, and no OOM kill.
v=$t/vm-c
mkdir -p "$v/pressure"
cat > "$v/ticket.txt" <<'EOF'
Ticket 5121, from the warehouse:
"The stock app takes seconds to open every page, and the whole machine is
sluggish. Someone said the disk must be failing: it is busy all the time."

The VM: vm-c, 4 vCPUs, 8 GiB, a fixed-size (not burstable) instance.
The stock app runs as the service stock; cgroup/ holds its files.
Everything here was saved while the app was slow.
EOF
lscpu_file 4 2 > "$v/lscpu.txt"
echo " 15:21:44 up 4 days, 22:10,  2 users,  load average: 3.62, 3.40, 3.11" > "$v/uptime.txt"
printf '               total        used        free      shared  buff/cache   available\nMem:            7937        7412          61          12         463         184\nSwap:           4095        3180         915\n' > "$v/free.txt"
vmstat_lines 1 2 3256000 62000 4100 430000 2400 3100 9600 12400 10 6 48 35 0 > "$v/vmstat.txt"
mpstat_file vm-c 4 \
  "10.20 0.00 6.10 35.10 0.00 0.60 0.00 0.00 0.00 48.00" \
  "10.50 0.00 6.30 34.80 0.00 0.70 0.00 0.00 0.00 47.70" \
  "9.90 0.00 5.90 35.60 0.00 0.50 0.00 0.00 0.00 48.10" \
  "10.30 0.00 6.20 34.90 0.00 0.60 0.00 0.00 0.00 48.00" \
  "10.10 0.00 6.00 35.10 0.00 0.60 0.00 0.00 0.00 48.20" > "$v/mpstat.txt"
echo "cpu  4000000 500 1900000 41000000 3600000 0 90000 0 0 0" > "$v/stat-before.txt"
echo "cpu  4002400 500 1901440 41011520 3608400 0 90240 0 0 0" > "$v/stat-after.txt"
printf 'some avg10=8.31 avg60=7.92 avg300=6.40 total=611320011\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n' > "$v/pressure/cpu"
printf 'some avg10=45.12 avg60=43.80 avg300=40.02 total=2841177120\nfull avg10=30.48 avg60=29.65 avg300=27.11 total=1940113560\n' > "$v/pressure/memory"
printf 'some avg10=38.20 avg60=37.41 avg300=33.90 total=2433120773\nfull avg10=25.10 avg60=24.66 avg300=22.04 total=1601870226\n' > "$v/pressure/io"
cgroup_files "$v" "max 100000" max 6442450944 6439001088
cpu_stat 512345000000 401234000000 111111000000 0 0 0 > "$v/cgroup/cpu.stat.before"
cpu_stat 512355800000 401241200000 111114600000 0 0 0 > "$v/cgroup/cpu.stat.after"
mem_events 1204331 > "$v/cgroup/memory.events.before"
mem_events 1262018 > "$v/cgroup/memory.events.after"
io_stat 91000000000 23000000000 9100000 2100000 > "$v/cgroup/io.stat.before"
io_stat 91141000000 23009460000 9134400 2102310 > "$v/cgroup/io.stat.after"
{
  dmesg_file
  echo "[    4.200133] Adding 4194300k swap on /swapfile.  Priority:-2 extents:6 across:4194300k SS"
} > "$v/dmesg.txt"

# --- vm-d ------------------------------------------------------------------------
# 4 vCPUs, a quarter busy: one CPU at 99% user time and the other three
# idle. Steal 0.1%, no throttling, memory and pressure quiet.
v=$t/vm-d
mkdir -p "$v/pressure"
cat > "$v/ticket.txt" <<'EOF'
Ticket 5130, from finance:
"The month-end export took ten minutes last year and takes an hour now,
with twice the orders. The monitoring page says the VM is only a quarter
busy, so the VM can't be the problem."

The VM: vm-d, 4 vCPUs, 16 GiB, a fixed-size (not burstable) instance.
The export runs as the service export; cgroup/ holds its files.
Everything here was saved while the export was running.
EOF
lscpu_file 4 2 > "$v/lscpu.txt"
echo " 09:05:31 up 63 days,  1:44,  1 user,  load average: 1.04, 1.02, 0.97" > "$v/uptime.txt"
printf '               total        used        free      shared  buff/cache   available\nMem:           15951        2210        9420          20        4321       13741\nSwap:              0           0           0\n' > "$v/free.txt"
vmstat_lines 1 0 0 9645000 210300 4210000 0 0 4 30 25 0 75 0 0 > "$v/vmstat.txt"
mpstat_file vm-d 4 \
  "25.10 0.00 0.35 0.05 0.00 0.05 0.10 0.00 0.00 74.35" \
  "0.45 0.00 0.30 0.05 0.00 0.05 0.10 0.00 0.00 99.05" \
  "0.50 0.00 0.40 0.05 0.00 0.05 0.10 0.00 0.00 98.90" \
  "99.10 0.00 0.40 0.00 0.00 0.05 0.10 0.00 0.00 0.35" \
  "0.40 0.00 0.30 0.10 0.00 0.05 0.10 0.00 0.00 99.05" > "$v/mpstat.txt"
echo "cpu  52000000 300 4100000 160000000 90000 0 41000 9000 0 0" > "$v/stat-before.txt"
echo "cpu  52006036 300 4100084 160017832 90012 0 41012 9024 0 0" > "$v/stat-after.txt"
printf 'some avg10=0.42 avg60=0.40 avg300=0.37 total=81320011\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n' > "$v/pressure/cpu"
printf 'some avg10=0.00 avg60=0.00 avg300=0.00 total=110044\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=90113\n' > "$v/pressure/memory"
printf 'some avg10=0.03 avg60=0.03 avg300=0.02 total=1033120\nfull avg10=0.01 avg60=0.01 avg300=0.01 total=501870\n' > "$v/pressure/io"
cgroup_files "$v" "max 100000" max max 1610612736
cpu_stat 2012345000000 1990234000000 22111000000 0 0 0 > "$v/cgroup/cpu.stat.before"
cpu_stat 2012404400000 1990293100000 22111300000 0 0 0 > "$v/cgroup/cpu.stat.after"
mem_events 0 > "$v/cgroup/memory.events.before"
mem_events 0 > "$v/cgroup/memory.events.after"
io_stat 12000000000 3100000000 400000 90000 > "$v/cgroup/io.stat.before"
io_stat 12004000000 3100900000 400090 90022 > "$v/cgroup/io.stat.after"
dmesg_file > "$v/dmesg.txt"

# --- The rules -----------------------------------------------------------------------
cat > "$t/README.txt" <<'EOF'
Four slow VMs: what goes in ~/diagnosis/
=========================================

vm-a/ to vm-d/ hold what an on-call script saved from four customers' VMs
at the moment each ticket came in. Every folder has the same files:

  ticket.txt             the ticket in the customer's words, and the VM's size
  lscpu.txt, uptime.txt, free.txt     those commands' output
  vmstat.txt             sixty lines of vmstat 1
  mpstat.txt             mpstat -P ALL 60 1
  stat-before.txt, stat-after.txt     /proc/stat's first line, 60 s apart
  pressure/              /proc/pressure/cpu, memory and io
  cgroup/                the slow service's cgroup files: cpu.max, memory.max,
                         memory.high, memory.current, io.max, and cpu.stat,
                         memory.events and io.stat twice, as .before and
                         .after, 60 s apart
  dmesg.txt              the kernel's log

They are constructed, not captured: every file is in the real layout of the
tool or kernel file it is named after (Ubuntu 24.04's vmstat, mpstat, free
and uptime; the kernel's /proc/stat, pressure and cgroup files), with
invented numbers.

For each VM, write ~/diagnosis/vm-X.txt, three lines:

  cause=      one of: steal, cpu-quota, memory-pressure, disk-cap,
              too-few-cpus, single-thread, healthy
  evidence=   the one number that shows the cause:
                steal            the steal % between the two stat files
                cpu-quota        the % of periods throttled between the two
                                 cpu.stat files
                memory-pressure  some avg10 in pressure/memory
                disk-cap         writes a second between the two io.stat files
                too-few-cpus     the average of vmstat's r column
                single-thread    the busiest CPU's %usr in mpstat's Average rows
                healthy          0
  fix=        one of: fixed-size-or-unlimited, dedicated-host,
              raise-cpu-quota, more-memory-or-raise-throttle,
              faster-disk-tier, more-vcpus, fix-the-program, nothing

The lists are longer than what is wrong. Numbers may be written with or
without decimals. evidence is checked to within 1.0, or within 0.5 for
memory-pressure.
EOF

mkdir -p /home/learner/diagnosis
for vm in vm-a vm-b vm-c vm-d; do
  printf 'cause=\nevidence=\nfix=\n' > "/home/learner/diagnosis/$vm.txt"
done
chown -R learner:learner /home/learner/diagnosis
chmod -R a+rX "$t"

# The checksum of everything under /srv/tickets, for the check that keeps the
# evidence as it was saved (the learner has sudo). Root's alone.
mkdir -p /usr/local/lib/lab
(cd "$t" && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1) > /usr/local/lib/lab/tickets.sha256
chmod 600 /usr/local/lib/lab/tickets.sha256
