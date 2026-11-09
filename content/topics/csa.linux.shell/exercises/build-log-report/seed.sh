#!/usr/bin/env bash
# The shop's logs, the same in every Shell essentials lab: everything is
# decided by arithmetic on the line number, so the files are identical on
# every build and the checks can compute the truth from them.
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

# worker.log: a second log in the same shape, so a script can be tried on
# more than one file.
: > worker.log
for i in $(seq 1 120); do
  if (( i % 9 == 0 )); then line="ERROR worker crashed on task $i"
  elif (( i % 14 == 0 )); then line="error retrying task $i"
  else line="INFO task $i done"
  fi
  echo "$line" >> worker.log
done

# old-access.log: last month's requests, with a different favourite path and
# no ties in the top two.
: > old-access.log
for i in $(seq 1 300); do
  case $((i % 6)) in
    0|1|2) path=/search ;;
    3|4)   path=/home ;;
    *)     path=/cart ;;
  esac
  if (( i % 30 == 0 )); then status=500; else status=200; fi
  echo "GET $path $status $(( (i * 53) % 900 + 100 ))" >> old-access.log
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
