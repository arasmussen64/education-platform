#!/bin/bash
# Lays down the debug: the dated GPU table the build uses (its README gives
# every source), a README with the script's examples, and the colleague's
# fit-check in the learner's ~/bin.
set -euo pipefail

plan=/srv/plan
mkdir -p "$plan"
cp /usr/local/lib/lab/gpus.csv "$plan/gpus.csv"
rm /usr/local/lib/lab/gpus.csv

cat > "$plan/gpus-README.txt" <<'EOF'
gpus.csv: GPU instances on three clouds, one row each, read on 2026-11-11.

  as_of               the day the row was read
  cloud, region       aws us-east-1 (N. Virginia), azure eastus (East US),
                      gcp us-central1 (Iowa)
  instance            the provider's name for the size
  gpu                 the card
  gpu_count           how many cards the instance has
  gpu_mem_as_stated   one card's memory, in the provider's own figure and
                      unit: AWS in GiB, Azure and Google Cloud in GB
  gpu_mem_gib         the same figure converted to GiB: a GiB as stated is
                      kept, and a GB (1,000,000,000 bytes) is divided by
                      1.073741824, to two places
  vcpus               the instance's vCPUs
  hourly_usd          the on-demand price for Linux, US dollars an hour

The providers disagree about the same cards. AWS lists the L4 as 22 GiB and
Google Cloud as 24 GB, which is 22.35 GiB; AWS lists the T4 as 16 GiB and
Azure as 16 GB, which is 14.90 GiB. This table takes every figure at its
word and converts it, so it never pretends one unit is the other; on a real
machine, nvidia-smi's own total settles it. Work only with gpu_mem_gib.

Where each column came from, all read on 2026-11-11:
  AWS sizes and card memory  https://docs.aws.amazon.com/ec2/latest/instancetypes/ac.html
  AWS prices                 AWS's public price file for US East (N. Virginia),
                             Linux, on-demand, published 2026-11-10; today's are
                             at https://aws.amazon.com/ec2/pricing/on-demand/
  Azure sizes and memory     the size-series pages under
                             https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/
  Azure prices               https://prices.azure.com/api/retail/prices (East US,
                             pay-as-you-go); today's are at
                             https://azure.microsoft.com/pricing/details/virtual-machines/linux/
  Google Cloud sizes         https://docs.cloud.google.com/compute/docs/gpus
  Google Cloud prices        https://cloud.google.com/products/compute/pricing/accelerator-optimized
                             (Iowa)
Prices change. These are for this lab; today's will differ.
EOF

cat > "$plan/README.txt" <<'EOF'
fit-check: which instance in gpus.csv should a model run on?

  ~/bin/fit-check PARAMS_BILLION BITS HEADROOM_PCT

PARAMS_BILLION is the model's size in billions of parameters, BITS the bits
each parameter is stored in, and HEADROOM_PCT the room to leave on the card
on top of the weights, as a percentage of them. It prints one line: the
cheapest instance on which the model runs on one card with that headroom,
and its price an hour, like

  g4dn.xlarge 0.526

or "none" when no instance in the table can run it on one card. The team
used it last month like this:

  ~/bin/fit-check 9 16 15
  ~/bin/fit-check 42 16 10
EOF

chmod -R a+rX "$plan"
mkdir -p /home/learner/bin
cp /usr/local/lib/lab/fit-check /home/learner/bin/fit-check
chmod 755 /home/learner/bin/fit-check
chown -R learner:learner /home/learner/bin
rm /usr/local/lib/lab/fit-check

# The checksum of everything under /srv/plan, for the check that keeps the
# table as it was (the learner has sudo). Root's alone.
(cd "$plan" && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1) > /usr/local/lib/lab/plan.sha256
chmod 600 /usr/local/lib/lab/plan.sha256
