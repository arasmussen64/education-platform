#!/bin/bash
# Writes the access log: 120 days of requests, 2026-07-04 to 2026-10-31,
# from a loop counter, so the log is the same in every build and the
# checks know what is in it.
set -euo pipefail

mkdir -p /var/log/ops
log=/var/log/ops/access.log
: > "$log"

for i in $(seq 0 119); do
  day=$(date -u -d "2026-07-04 +$i days" +%F)

  # reports: orders every day, a report file every week, and the quarter's
  # summary once, on day 15 (2026-07-19), 104 days before the last line.
  echo "$day reports read Order/o-$((1000 + i))" >> "$log"
  if (( i % 7 == 0 )); then
    echo "$day reports write Report/weekly-$((i / 7))" >> "$log"
  fi
  if (( i == 15 )); then
    echo "$day reports export Summary/q2-2026" >> "$log"
  fi

  # deployer: a change and a release every third day, an update the day
  # after. Twice (days 40 and 85) it approved its own change, which its
  # broad access let it do and its job says it never should.
  if (( i % 3 == 0 )); then
    echo "$day deployer open Change/c-$i" >> "$log"
    echo "$day deployer create Release/r-$i" >> "$log"
  fi
  if (( i % 3 == 1 )); then
    echo "$day deployer update Release/r-$((i - 1))" >> "$log"
    if (( i == 40 || i == 85 )); then
      echo "$day deployer approve Change/c-$((i - 1))" >> "$log"
    else
      echo "$day maya approve Change/c-$((i - 1))" >> "$log"
    fi
  fi

  # backup: every day.
  echo "$day backup read Order/o-$((1000 + i))" >> "$log"
  echo "$day backup read StoreData/north" >> "$log"
  echo "$day backup read StoreData/south" >> "$log"
  echo "$day backup write Vault/main" >> "$log"
done

chmod 644 "$log"
