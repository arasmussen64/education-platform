# One way through the review, with the pipelines from the topic's practice.
# Every number could also be worked out by hand or with a calculator; that
# is the same skill.
r=/srv/review
cd ~/review

# Cores: one line per CPU from lscpu -p, one per core once sort -u has
# dropped the second thread of each. NUMA: lscpu's own line, and CPU 40's
# node from the per-CPU list.
for m in app-1 db-2 arm-2; do
  echo "cores.$m=$(lscpu --sysroot $r/machines/$m -p=CORE,SOCKET | grep -v '^#' | sort -u | wc -l)"
done > answers.txt
echo "numa-nodes.db-2=$(lscpu --sysroot $r/machines/db-2 | awk -F': *' '/^NUMA node\(s\)/ {print $2}')" >> answers.txt
echo "node-of-cpu-40.db-2=$(lscpu --sysroot $r/machines/db-2 -p=CPU,NODE | grep -v '^#' | awk -F, '$1 == 40 {print $2}')" >> answers.txt

# Steal over the ten minutes: the growth of the eighth counter over the
# growth of the first eight (write-steal-pct's sum).
echo "steal-pct=$(paste $r/stat-before.txt $r/stat-after.txt | awk '{for (i = 2; i <= 9; i++) t += $(i + 11) - $i; printf "%.1f", ($20 - $9) * 100 / t}')" >> answers.txt

# The credits: fill-credit-bucket's walk through the minutes.
v=$(grep '^vcpus=' $r/burst/instance.conf | cut -d= -f2)
p=$(grep '^baseline_pct=' $r/burst/instance.conf | cut -d= -f2)
s=$(grep '^start_credits=' $r/burst/instance.conf | cut -d= -f2)
m=$(grep '^max_credits=' $r/burst/instance.conf | cut -d= -f2)
awk -F, -v v="$v" -v p="$p" -v b="$s" -v m="$m" 'NR > 1 {
  b = b + v * p / 100 - v * $2 / 100
  if (b <= 0 && e == "") e = $1
  if (b < 0) b = 0; if (b > m) b = m
  if (b == 0 && $2 > p) h++
} END {
  print "credits-empty-minute=" (e == "" ? "never" : e)
  print "minutes-held-to-baseline=" h + 0
}' $r/burst/usage.csv >> answers.txt

# The web server: the 95th percentile of CPU (the 1,916th of 2,016 sorted)
# and the peak of memory, then the cheapest size that holds both with the
# policy's headroom.
p95=$(tail -n +2 $r/sizing/metrics.csv | cut -d, -f2 | sort -n | awk '{v[NR] = $1} END {k = NR * 95 / 100; if (k > int(k)) k = int(k) + 1; print v[k]}')
peak=$(tail -n +2 $r/sizing/metrics.csv | cut -d, -f3 | sort -n | tail -n 1)
echo "p95 $p95% of 16 vCPUs, peak $peak GiB"
echo "size.web=$(awk -F, -v p95="$p95" -v peak="$peak" 'NR > 1 && p95 / 100 * 16 <= 0.70 * $2 && peak <= 0.75 * $3 {print $4, $1}' $r/sizing/sizes.csv | sort -n | head -n 1 | cut -d' ' -f2)" >> answers.txt

# The ticket: no steal (0.1% between the stat files), no throttling (no
# quota, nr_throttled 0), memory fine (no throttle, nothing in memory
# pressure), every CPU busy rather than one; but r, the tasks ready to run,
# is far above the 4 CPUs, and CPU pressure is high. Too few CPUs.
echo "ticket.cause=too-few-cpus" >> answers.txt
echo "ticket.evidence=$(awk 'NR > 2 {t += $1; n++} END {printf "%.1f", t / n}' $r/ticket/vmstat.txt)" >> answers.txt
echo "ticket.fix=more-vcpus" >> answers.txt
cat answers.txt
