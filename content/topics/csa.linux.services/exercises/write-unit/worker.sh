#!/usr/bin/env bash
# The shop's background worker: pretends to process one order every three
# seconds, for as long as it runs.
order=1000
while true; do
  echo "processed order $order"
  order=$((order + 1))
  sleep 3
done
