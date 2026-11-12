#!/bin/bash
# Lays down a sizing review under /srv/sizing, for one of four stories:
#
#   seed.sh shop        the checkpoint's build, and its four steps
#   seed.sh bakery      a fresh version of the build
#   seed.sh print-shop  another fresh version
#   seed.sh clinic      the solved example, with three workloads
#
# prices.csv is a dated table of real list prices; README.txt, below, gives
# every source. The workloads' metrics are constructed, not captured: from
# arithmetic on a sample counter (a working day, quiet nights and weekends,
# a few busy hours, a spike or two), never from randomness, so the checks
# work out every right answer from the same files. The same file is in every
# sizing lab of this checkpoint; only the story named in its Dockerfile
# differs.
set -euo pipefail

story=$1
s=/srv/sizing
mkdir -p "$s/workloads"
cp /usr/local/lib/lab/prices.csv "$s/prices.csv"

# metrics WORKLOAD NAME=VALUE...: writes the workload's metrics.csv.
#   mode=week     a week of 5-minute samples, 7 x 24 x 12 = 2,016 of them
#   mode=nights   only the hours a nightly job runs: 7 nights x hours x 12
#   night, work, busy, eve, wkf   CPU levels (% of the machine it runs on
#       now) at night, in the working day, in the busy hours (10:00 to
#       12:00 and 14:00 to 16:00 on weekdays) and in the evening, and how
#       much of them a weekend keeps. A nightly job's first and last hours
#       (loading and writing out) run at half its busy level.
#   spikes        sample:value pairs, a few minutes of something unusual
#   mbase, mbusy  memory in use, in GiB, and what the busy hours add
#   mpeak_at, mpeak   the sample with the week's largest memory, and it
#   gpu=1, gutil, gbase, gpeak_at, gpeak   for a GPU job: its utilisation,
#       and its GPU memory in use, in GiB, with the week's largest
metrics() {
  local w=$1 kv
  shift
  local args=()
  for kv in "$@"; do args+=(-v "$kv"); done
  awk "${args[@]}" 'BEGIN {
    n = split(spikes, sp, ",")
    for (x = 1; x <= n; x++) { split(sp[x], pair, ":"); spike[pair[1]] = pair[2] }
    rows = (mode == "week") ? 2016 : 7 * hours * 12
    printf "sample,cpu_pct,mem_gib"
    if (gpu) printf ",gpu_util_pct,gpu_mem_gib"
    print ""
    for (i = 1; i <= rows; i++) {
      j = i - 1
      edge = 0
      if (mode == "week") {
        day = int(j / 288); hour = int((j % 288) / 12); weekday = day < 5
        busyhour = weekday && (hour == 10 || hour == 11 || hour == 14 || hour == 15)
        if (busyhour) cpu = busy + ((j * 7) % 11 - 5) * 0.2
        else if (hour < 7 || hour >= 22) cpu = night + (j % 5) * 0.3
        else if (hour < 18) cpu = work + (j % 7) * 0.4
        else cpu = eve + (j % 3) * 0.5
        if (!weekday) cpu = cpu * wkf
      } else {
        k = j % (hours * 12); phase = int(k / 12)
        edge = (phase == 0 || phase == hours - 1)
        busyhour = !edge
        if (edge) cpu = busy * 0.5 + (j % 3) * 0.3
        else cpu = busy + ((j * 7) % 11 - 5) * 0.2
      }
      if (i in spike) cpu = spike[i]
      mem = mbase + (busyhour ? mbusy : 0) + (j % 9) * 0.1
      if (i == mpeak_at) mem = mpeak
      printf "%d,%.1f,%.1f", i, cpu, mem
      if (gpu) {
        util = edge ? 6 + (j % 5) : gutil + ((j * 3) % 9 - 4)
        if (mode == "nights" && phase == 0) gm = gbase * (k % 12 + 1) / 12
        else gm = gbase + (j % 7) * 0.1
        if (i == gpeak_at) gm = gpeak
        printf ",%.0f,%.1f", util, gm
      }
      print ""
    }
  }' > "$s/workloads/$w/metrics.csv"
}

# brief WORKLOAD: its brief.txt, from standard input.
brief() {
  mkdir -p "$s/workloads/$1"
  cat > "$s/workloads/$1/brief.txt"
}

case $story in
shop)
  company="the shop"
  workloads="w1 w2 w3 w4 w5"
  brief w1 <<'EOF'
w1: orders-api
  What it is    The shop's orders API, a web service on Linux.
  Runs now      Google Cloud, n4-standard-8, Linux, all month.
  What it runs  A Java service, and a monitoring agent from the shop's
                vendor, which comes only as a program compiled for x86.
  May move to   Google Cloud only, beside the shop's other services there.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         long: it is busy through the working day.
EOF
  metrics w1 mode=week night=4 work=10 busy=27 eve=14 wkf=0.6 spikes=1300:68 mbase=7.8 mbusy=2.4 mpeak_at=900 mpeak=11.2
  brief w2 <<'EOF'
w2: ledger-db
  What it is    The shop's accounts database.
  Runs now      Azure, D16s_v5, with Windows Server and SQL Server
                Standard, both licences included in the hourly price.
  What it runs  SQL Server Standard on Windows Server.
  May move to   Azure only.
  Licences      Windows Server and SQL Server Standard, included in the
                price: the shop owns no licences with Software Assurance.
  Hours         730 a month: it runs all the time.
  Peaks         long: the month-end close keeps it busy for days.
EOF
  metrics w2 mode=week night=6 work=14 busy=24 eve=12 wkf=0.7 spikes=1700:52 mbase=34 mbusy=5 mpeak_at=1450 mpeak=41.3
  brief w3 <<'EOF'
w3: thumbnailer
  What it is    Makes the small pictures of every product, a stateless
                service on Linux.
  Runs now      AWS, m7i.xlarge, Linux, all month.
  What it runs  A Go program, compiled in the shop's own build pipeline,
                which already builds its container image for x86 and for
                Arm. On a test machine with Arm processors it served the
                same requests a vCPU. The team has decided to move it to
                Arm, as long as nothing in it stops that.
  May move to   AWS only.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         long: new products arrive all day.
EOF
  metrics w3 mode=week night=12 work=30 busy=50 eve=36 wkf=0.8 spikes=600:83,601:79 mbase=6.0 mbusy=2.0 mpeak_at=1210 mpeak=9.0
  brief w4 <<'EOF'
w4: caption-model
  What it is    Writes a caption for every new product photo, in one
                batch a night, with a model on one GPU.
  Runs now      Azure, NC24ads_A100_v4, Linux. The VM is started for the
                job at 23:00 and stopped after it at 05:00.
  What it runs  A Python program and NVIDIA's CUDA libraries, in a
                container image built for x86.
  May move to   any of the three clouds.
  Licences      none: Linux.
  Hours         180 a month: six hours a night. metrics.csv holds a
                week of those nights, 5-minute samples while the job ran.
  Peaks         long: the whole six hours.
EOF
  metrics w4 mode=nights hours=6 busy=8 mbase=9.4 mbusy=0.8 mpeak_at=223 mpeak=11.6 gpu=1 gutil=38 gbase=17.6 gpeak_at=351 gpeak=19.4
  brief w5 <<'EOF'
w5: wiki
  What it is    The staff wiki, a small internal tool on Linux.
  Runs now      AWS, m7i.large, Linux, all month.
  What it runs  The wiki's own image, which its maker ships for x86 only.
  May move to   AWS or Azure.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         short: a few minutes at a time, when someone rebuilds the
                search index.
EOF
  metrics w5 mode=week night=3 work=6 busy=30 eve=5 wkf=0.8 spikes=410:85,411:82,1250:85,1251:84,1252:80 mbase=1.5 mbusy=0.4 mpeak_at=1251 mpeak=2.9
  ;;
bakery)
  company="the bakery"
  workloads="w1 w2 w3 w4 w5"
  brief w1 <<'EOF'
w1: shop-front
  What it is    The bakery's online shop, a web service on Linux.
  Runs now      AWS, m7i.2xlarge, Linux, all month.
  What it runs  A PHP site, and a payment module from the bakery's bank,
                which comes only as a library compiled for x86.
  May move to   AWS only.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         long: it is busy from breakfast to late evening.
EOF
  metrics w1 mode=week night=5 work=12 busy=22 eve=15 wkf=0.9 spikes=1590:61 mbase=7.4 mbusy=2.1 mpeak_at=1592 mpeak=10.4
  brief w2 <<'EOF'
w2: orders-db
  What it is    The bakery's orders database.
  Runs now      AWS, r7i.2xlarge, with Windows Server and SQL Server
                Standard, both licences included in the hourly price.
  What it runs  SQL Server Standard on Windows Server.
  May move to   AWS only.
  Licences      Windows Server and SQL Server Standard, included in the
                price: the bakery owns no licences with Software Assurance.
  Hours         730 a month: it runs all the time.
  Peaks         long: orders for the morning's bake arrive all evening.
EOF
  metrics w2 mode=week night=8 work=15 busy=26 eve=19 wkf=0.8 spikes=800:57 mbase=18.5 mbusy=3.2 mpeak_at=1105 mpeak=23.0
  brief w3 <<'EOF'
w3: recipe-search
  What it is    Search over the bakery's recipes and stock, on Linux.
  Runs now      Azure, D4s_v6, Linux, all month.
  What it runs  A Rust program, compiled in the bakery's build pipeline,
                which already builds its container image for x86 and for
                Arm. On a test machine with Arm processors it answered the
                same searches a vCPU. The team has decided to move it to
                Arm, as long as nothing in it stops that.
  May move to   Azure only.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         long: the bakers search all day.
EOF
  metrics w3 mode=week night=10 work=28 busy=45 eve=30 wkf=0.7 spikes=1001:77 mbase=5.9 mbusy=1.8 mpeak_at=1777 mpeak=8.8
  brief w4 <<'EOF'
w4: forecast-tuning
  What it is    Fine-tunes the bakery's demand forecast every night, with
                a model on one GPU.
  Runs now      Google Cloud, a2-highgpu-1g, Linux. The VM is started for
                the job at 01:00 and stopped after it at 05:00.
  What it runs  A Python program and NVIDIA's CUDA libraries, in a
                container image built for x86.
  May move to   any of the three clouds.
  Licences      none: Linux.
  Hours         120 a month: four hours a night. metrics.csv holds a
                week of those nights, 5-minute samples while the job ran.
  Peaks         long: the whole four hours.
EOF
  metrics w4 mode=nights hours=4 busy=15 mbase=17.0 mbusy=2.2 mpeak_at=130 mpeak=20.5 gpu=1 gutil=71 gbase=28.6 gpeak_at=310 gpeak=31.0
  brief w5 <<'EOF'
w5: till-sync
  What it is    Keeps the shops' tills and the stock list in step, a
                small service on Linux.
  Runs now      AWS, m7i.xlarge, Linux, all month.
  What it runs  Its maker's image, built for x86 only.
  May move to   AWS or Azure.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         long: it is busy from early morning to late at night, and
                syncs the tills all night: there are no quiet hours.
EOF
  metrics w5 mode=week night=21 work=24 busy=26.5 eve=23 wkf=1.0 mbase=3.9 mbusy=0.3 mpeak_at=1660 mpeak=5.1
  ;;
print-shop)
  company="the print shop"
  workloads="w1 w2 w3 w4 w5"
  brief w1 <<'EOF'
w1: job-tracker
  What it is    Tracks every print job from order to dispatch, a web
                service on Linux.
  Runs now      Azure, D8s_v5, Linux, all month.
  What it runs  A Node.js service, and a licence server from the print
                shop's software vendor, which comes only as a program
                compiled for x86.
  May move to   Azure only.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         long: it is busy through the working day.
EOF
  metrics w1 mode=week night=3 work=9 busy=20 eve=8 wkf=0.5 spikes=470:58 mbase=7.0 mbusy=1.7 mpeak_at=1180 mpeak=9.6
  brief w2 <<'EOF'
w2: quotes-db
  What it is    The print shop's quotes and invoices database.
  Runs now      Google Cloud, n4-highmem-8, with Windows Server and SQL
                Server Standard, both licences included in the price.
  What it runs  SQL Server Standard on Windows Server.
  May move to   Google Cloud only.
  Licences      Windows Server and SQL Server Standard, included in the
                price: the print shop owns no licences of its own.
  Hours         730 a month: it runs all the time.
  Peaks         long: quotes are priced all day.
EOF
  metrics w2 mode=week night=5 work=13 busy=21 eve=10 wkf=0.6 spikes=1340:49 mbase=17.6 mbusy=3.0 mpeak_at=1020 mpeak=22.4
  brief w3 <<'EOF'
w3: proof-renderer
  What it is    Turns customers' files into proofs to approve, a
                stateless service on Linux.
  Runs now      Google Cloud, n4-standard-8, Linux, all month.
  What it runs  A Java program and a C library for colour profiles, both
                built in the print shop's own build pipeline, which
                already builds its container image for x86 and for Arm. On
                a test machine with Arm processors it rendered the same
                proofs a vCPU. The team has decided to move it to Arm, as
                long as nothing in it stops that.
  May move to   Google Cloud only.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         long: proofs are sent all day.
EOF
  metrics w3 mode=week night=6 work=14 busy=22 eve=12 wkf=0.6 spikes=950:66 mbase=7.8 mbusy=2.0 mpeak_at=1620 mpeak=10.8
  brief w4 <<'EOF'
w4: press-check
  What it is    Looks at a photo of every sheet off the press for faults,
                with a model on one GPU, as the sheets come off.
  Runs now      Azure, NV36ads_A10_v5, Linux, all month.
  What it runs  A Python program and NVIDIA's CUDA libraries, in a
                container image built for x86.
  May move to   AWS or Azure: the press's maker supports no other cloud.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         long: the presses run in shifts.
EOF
  metrics w4 mode=week night=3 work=4 busy=5 eve=3.5 wkf=0.8 mbase=9.8 mbusy=1.1 mpeak_at=1488 mpeak=12.0 gpu=1 gutil=44 gbase=15.2 gpeak_at=702 gpeak=17.0
  brief w5 <<'EOF'
w5: staff-handbook
  What it is    The staff handbook and rota, a small internal tool on
                Linux.
  Runs now      AWS, m7i.xlarge, Linux, all month.
  What it runs  Its maker's image, built for x86 only.
  May move to   AWS only: it signs people in through an AWS service.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         short: a few minutes at a time, when the week's rota is
                published.
EOF
  metrics w5 mode=week night=8 work=13 busy=26 eve=11 wkf=0.9 spikes=520:71,521:69,1830:74 mbase=4.3 mbusy=0.4 mpeak_at=1831 mpeak=5.6
  ;;
clinic)
  company="the clinic"
  workloads="c1 c2 c3"
  brief c1 <<'EOF'
c1: booking-api
  What it is    The clinic's appointment booking API, on Linux.
  Runs now      Google Cloud, n4-standard-8, Linux, all month.
  What it runs  A Python service, and a security agent the clinic's
                insurer requires, which comes only as a program compiled
                for x86.
  May move to   Google Cloud only.
  Licences      none: Linux.
  Hours         730 a month: it runs all the time.
  Peaks         long: bookings come in all day.
EOF
  metrics c1 mode=week night=2 work=5 busy=10 eve=4 wkf=0.7 spikes=880:33 mbase=3.5 mbusy=1.0 mpeak_at=1414 mpeak=5.4
  brief c2 <<'EOF'
c2: records-db
  What it is    The clinic's patient records database.
  Runs now      AWS, r7i.2xlarge, with Windows Server and SQL Server
                Standard, both licences included in the hourly price.
  What it runs  SQL Server Standard on Windows Server.
  May move to   AWS only.
  Licences      Windows Server and SQL Server Standard, included in the
                price: the clinic owns no licences of its own.
  Hours         730 a month: it runs all the time.
  Peaks         long: clinics are open all day.
EOF
  metrics c2 mode=week night=3 work=6 busy=9 eve=4 wkf=0.6 spikes=1530:31 mbase=9.0 mbusy=1.5 mpeak_at=630 mpeak=11.6
  brief c3 <<'EOF'
c3: scan-reader
  What it is    Reads the day's scanned letters into the records system,
                in one batch a night, with a model on one GPU.
  Runs now      AWS, g5.xlarge, Linux. The VM is started for the job at
                02:00 and stopped after it at 05:00.
  What it runs  A Python program and NVIDIA's CUDA libraries, in a
                container image built for x86.
  May move to   any of the three clouds.
  Licences      none: Linux.
  Hours         90 a month: three hours a night. metrics.csv holds a
                week of those nights, 5-minute samples while the job ran.
  Peaks         long: the whole three hours.
EOF
  metrics c3 mode=nights hours=3 busy=30 mbase=8.2 mbusy=0.7 mpeak_at=100 mpeak=9.8 gpu=1 gutil=55 gbase=10.5 gpeak_at=170 gpeak=11.8
  ;;
*)
  echo "seed.sh: no story called '$story'" >&2
  exit 1
  ;;
esac

# --- The rules ---------------------------------------------------------------------
{
  cat <<EOF
The sizing review: what goes in ~/sizing/answers.csv
====================================================

Before $company signs its cloud contracts again, each workload below gets
the size that fits it, on the clouds it may use, and a month's cost.

The files
  prices.csv          the sizes a workload may move to, on three clouds,
                      with their list prices (its columns are below)
  workloads/*/        one folder a workload:
    brief.txt         what it is, where it runs now, what it runs (which
                      says what it can run on), the clouds it may move to,
                      its licences, the hours it runs, and its peaks
    metrics.csv       a week of its numbers from the machine it runs on now
  metric-summary FILE prints each column's average, median, 95th percentile
                      and largest value; the raw files are there for anyone
                      who wants to check with sort and awk

metrics.csv's columns
  sample          the sample's number; one every 5 minutes
  cpu_pct         CPU in use, as a percentage of all the vCPUs of the
                  machine it runs on now
  mem_gib         memory in use, in GiB
  gpu_util_pct    (a GPU job) the GPU's utilisation, in %
  gpu_mem_gib     (a GPU job) the GPU's memory in use, in GiB

The sizing policy
  CPU        the 95th percentile of cpu_pct, as vCPUs of the machine it
             runs on now, is at most 60% of the new size's vCPUs
  Memory     the largest mem_gib is at most 80% of the new size's memory
  GPU        the largest gpu_mem_gib is at most 90% of the new size's GPU
             memory (gpu_mem_gib in prices.csv)
  Burstable  a size with a baseline_pct only when the brief says the
             workload's peaks are short, and its average CPU, as vCPUs of
             the machine it runs on now, is at most baseline_pct of the
             new size's vCPUs
  Then       among the sizes that meet all of that, on the clouds the
             brief allows, with processors that can run what the workload
             runs (and the ones its team has chosen, where the brief says
             so), and with a price for its licences, the cheapest for the
             hours it runs. Anything that costs at most 15% more than the
             cheapest is accepted.
  The 95th percentile is the nearest-rank one: sort the samples from
  smallest to largest and take the one at position 95% of the count,
  rounded up. metric-summary prints it.

What a month costs
  the hourly price x the hours a month the workload runs: 730 hours for
  one that runs all the time, and the hours its brief gives for one that
  runs part of the day
  Linux                  linux_hourly
  Windows Server         windows_hourly, with the licence included (empty:
                         no Windows price was read for that size)
  SQL Server Standard    on top of the Windows price, with the licence
                         included, for each of the VM's vCPUs an hour:
                           AWS            $0.12
                           Azure          $0.10
                           Google Cloud   $0.12
                         On all three, a VM with fewer than 4 vCPUs pays
                         for 4.

prices.csv's columns
  as_of            the day the row was read
  cloud, region    aws us-east-1 (N. Virginia), azure eastus (East US),
                   gcp us-central1 (Iowa)
  instance         the provider's name for the size (Azure's without its
                   Standard_ in front)
  kind             general, compute, memory, burstable or gpu
  arch             x86 or arm
  vcpus, mem_gib   the size's vCPUs and its memory in GiB
  gpu              its card, for a GPU size (one card each)
  gpu_mem_as_stated  the card's memory, in the provider's own figure and
                   unit: AWS in GiB, Azure and Google Cloud in GB
  gpu_mem_gib      the same converted to GiB (a GB, 1,000,000,000 bytes,
                   is 0.931 of a GiB); work only with this one
  baseline_pct     a burstable size's baseline, a share of each vCPU
  linux_hourly     the on-demand price for Linux, US dollars an hour
  windows_hourly   the same with Windows Server's licence included

Where the prices came from, all read on 2026-11-11
  AWS     the public price files behind https://aws.amazon.com/ec2/pricing/on-demand/
          for US East (N. Virginia), on-demand: Linux, Windows, and
          Windows with SQL Server Standard (published 2026-11-10); sizes
          and card memory from https://docs.aws.amazon.com/ec2/latest/instancetypes/ac.html
          and the instance type pages; baselines from
          https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html
  Azure   the public Azure Retail Prices API, https://prices.azure.com/api/retail/prices,
          East US, pay-as-you-go, for the sizes and the SQL Server
          Standard licence meters; sizes, memory and baselines from the
          size-series pages under
          https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/
  Google  https://cloud.google.com/products/compute/pricing/general-purpose
          and .../accelerator-optimized (Iowa), and
          https://cloud.google.com/compute/disks-image-pricing for Windows
          Server ($0.046 a vCPU an hour, added in windows_hourly) and SQL
          Server Standard ($0.12 a core an hour, 4 cores at least)
Prices change. These are for this review; today's will differ.

answers.csv
  workload,instance,monthly_usd     the header, as it is
  one row a workload                its name, the size you choose (as
                                    prices.csv names it), and what a month
                                    of it will cost, licences included
  saving,,AMOUNT                    what the workloads cost a month today,
                                    on the machines they run on now, minus
                                    what your rows add up to
  Write numbers as plain digits, with or without decimals and without a $
  sign. Every monthly_usd, and the saving, is checked to within 15% of the
  check's own sum for the sizes you chose. Lines that start with # are
  ignored.
EOF
} > "$s/README.txt"

# --- The answers sheet ---------------------------------------------------------------
mkdir -p /home/learner/sizing
{
  echo "workload,instance,monthly_usd"
  for w in $workloads; do echo "$w,,"; done
  echo "saving,,"
} > /home/learner/sizing/answers.csv
chown -R learner:learner /home/learner/sizing
chmod -R a+rX "$s"

# The checksum of everything under /srv/sizing, for the check that keeps the
# evidence as it was (the learner has sudo). Root's alone.
(cd "$s" && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1) > /usr/local/lib/lab/sizing.sha256
chmod 600 /usr/local/lib/lab/sizing.sha256
