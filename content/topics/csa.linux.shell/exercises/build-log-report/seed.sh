#!/usr/bin/env bash
# Writes the shop's logs into /var/log/shop. Everything is decided by
# arithmetic on the line number, so the files are the same on every build
# and the checks can compute the truth from them.
set -euo pipefail

mkdir -p /var/log/shop
cd /var/log/shop

# access.log: 600 requests, "METHOD PATH STATUS BYTES". /home is the most
# requested path but never twice in a row, while /cart comes in pairs, so
# counting with uniq -c without sorting first gives the wrong answer.
: > access.log
for i in $(seq 1 600); do
  case $((i % 10)) in
    0|2|4|6) path=/home ;;
    7|8)     path=/cart ;;
    1)       path=/api/items ;;
    3)       path=/login ;;
    5)       path=/checkout ;;
    *)       path=/search ;;
  esac
  if (( i % 10 == 0 )); then method=POST; else method=GET; fi
  if (( i % 40 == 0 )); then status=503
  elif (( i % 25 == 0 )); then status=500
  elif (( i % 13 == 0 )); then status=404
  else status=200
  fi
  bytes=$(( (i * 37) % 1500 + 100 ))
  echo "$method $path $status $bytes" >> access.log
done

# app.log: 200 lines with mixed-case levels, so a case-sensitive grep misses some.
: > app.log
for i in $(seq 1 200); do
  if (( i % 17 == 0 )); then line="ERROR database connection refused (attempt $i)"
  elif (( i % 23 == 0 )); then line="error cache miss storm on key k$i"
  elif (( i % 5 == 0 )); then line="WARN slow query $((i * 3)) ms"
  else line="INFO handled request $i"
  fi
  echo "$line" >> app.log
done

# requests.csv: a header and 300 rows, 37 distinct users.
echo "user,path" > requests.csv
for i in $(seq 1 300); do
  case $((i % 4)) in
    0) path=/home ;;
    1) path=/api/items ;;
    2) path=/cart ;;
    *) path=/search ;;
  esac
  echo "u$((i % 37)),$path" >> requests.csv
done

chown -R root:root /var/log/shop
chmod 644 /var/log/shop/*
