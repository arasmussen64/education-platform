# trail.sh: what the checks of Audit logging's server labs share. A check
# reads it with ". /usr/local/lib/lab/trail.sh". Nothing here changes the
# learner's work; the same file is in each of those labs' folders.
# shellcheck shell=bash

lib=/usr/local/lib/lab-pay
journal_dir=/var/log/journal/$(cat /etc/machine-id).audit

# A fresh marker: hex, so it is safe after "=" in a command.
marker() { echo "chk$(od -An -N6 -tx1 /dev/urandom | tr -d ' \n')"; }

# The audit trail's lines (the writer's, without journald's own).
trail() { journalctl --namespace=audit -t shop-audit -o cat 2> /dev/null; }

# wait_for_line TEXT: waits up to 5 seconds for a line of the trail that
# holds TEXT, and prints the first such line.
wait_for_line() {
  local try found
  for try in $(seq 1 10); do
    found=$(trail | grep -F -- "$1" | head -n 1)
    [ -n "$found" ] && { echo "$found"; return 0; }
    sleep 0.5
  done
  return 1
}

# setting KEY: the value of a journald setting for the audit namespace as
# the files that outlast a reboot give it: /etc/systemd/journald@audit.conf
# and every drop-in, the last one winning. A file under /run is left out,
# because a reboot empties /run. Prints nothing when the key is unset.
setting() {
  systemd-analyze cat-config systemd/journald@audit.conf 2> /dev/null | awk -v key="$1" '
    /^# \// { lasting = ($2 !~ /^\/run\//); next }
    /^[[:space:]]*[#;]/ { next }
    lasting {
      line = $0
      sub(/^[[:space:]]+/, "", line)
      eq = index(line, "=")
      if (eq && substr(line, 1, eq - 1) == key) {
        value = substr(line, eq + 1)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      }
    }
    END { print value }'
}

# seconds VALUE: a time span as journald reads it ("400d", "13month", a
# bare number of seconds), in whole seconds; nothing when it isn't one.
seconds() {
  systemd-analyze timespan -- "$1" 2> /dev/null | awk '/μs:/ { printf "%d\n", $2 / 1000000 }'
}

# bytes VALUE: a size as journald reads it ("8G", "7500M", a bare number of
# bytes; K, M, G and T are powers of 1024), in bytes; nothing when it
# isn't one. journald takes one letter and no more: it ignores "8GB"
# ("Failed to parse size value") and keeps its default, so "8GB" isn't a
# size here either.
bytes() {
  python3 - "$1" << 'PY'
import re, sys
found = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([BKMGTPE]?)", sys.argv[1].strip())
if found:
    print(int(float(found.group(1)) * 1024 ** max(" KMGTPE".find(found.group(2) or " "), 0)))
PY
}

# rate_limit: how many messages from one service the audit journal lets
# through in half a minute, by the settings that outlast a reboot (journald
# allows RateLimitBurst messages every RateLimitIntervalSec; 10000 and 30
# seconds when unset). Prints the number, "off" when either is 0, or
# "unreadable".
rate_limit() {
  local burst interval
  burst=$(setting RateLimitBurst)
  interval=$(setting RateLimitIntervalSec)
  interval=$(seconds "${interval:-30s}")
  burst=${burst:-10000}
  case $burst in *[!0-9]*) echo unreadable; return ;; esac
  [ -n "$interval" ] || { echo unreadable; return; }
  if [ "$burst" -eq 0 ] || [ "$interval" -eq 0 ]; then echo off; return; fi
  echo $((burst * 30 / interval))
}

# seal_interval KEYFILE: how many seconds apart the seals are that the key
# in KEYFILE is for. A verification key ends "/START-INTERVAL", the
# interval in microseconds, in hex; a key with another interval written on
# it doesn't validate up to now. Prints nothing when there is no such key.
seal_interval() {
  local key every
  key=$(cat "$1" 2> /dev/null | tr -d '[:space:]')
  every=${key##*-}
  case $key in */*-*) ;; *) return ;; esac
  case $every in "" | *[!0-9a-f]*) return ;; esac
  echo $((16#$every / 1000000))
}

# sealed_now KEYFILE: makes the shop record a sign-in and waits for the key
# in KEYFILE to vouch for it. Prints "sealed", or one sentence about what
# is wrong. The one wait of a check run: a seal is written every 10
# seconds, so a key can vouch for a new entry within about 20. A trail
# that isn't sealed at all, or is sealed with other keys, is told at once.
sealed_now() {
  local key mark when said state from to try failures=0
  key=$(cat "$1" 2> /dev/null | tr -d '[:space:]')
  [ -n "$key" ] || { echo "there is no verification key in $1"; return; }
  # Sealing has to be switched on by a file that outlasts a reboot:
  # Seal=yes in a drop-in under /run seals until the next reboot only.
  # (Unset counts: journald's own default is to seal once keys exist.)
  case $(setting Seal) in
    "" | yes | y | true | t | on | 1) ;;
    *) echo "the audit journal's settings that outlast a reboot don't switch sealing on"; return ;;
  esac
  [ -e "$journal_dir/system.journal" ] || { echo "the audit journal has no file of its own on disk"; return; }
  journalctl --file="$journal_dir/system.journal" --header 2> /dev/null | grep 'Compatible flags:.*SEALED' > /dev/null \
    || { echo "the audit journal's newest file is not a sealed one"; return; }
  mark=$(marker)
  when=$(date -u +%FT%TZ)
  shop-cli login.ok user="$mark" > /dev/null 2>&1 || { echo "the shop isn't answering (systemctl status shop-audit)"; return; }
  # The sign-in has to be in the very file that is verified: a journal
  # that writes somewhere else (memory, another folder) leaves an old
  # sealed file behind, whose seals say nothing about today.
  for try in $(seq 1 10); do
    journalctl --file="$journal_dir/system.journal" -t shop-audit -o cat 2> /dev/null | grep -F "user=$mark " > /dev/null && break
    [ "$try" = 10 ] && { echo "a sign-in made a moment ago isn't in the audit journal's newest file on disk"; return; }
    sleep 0.5
  done
  for try in $(seq 1 16); do
    said=$($lib/seal-range --file "$journal_dir/system.journal" "$key")
    read -r state from to <<< "$said"
    # TO is the end of the newest sealed interval, so "not before the
    # sign-in" means a seal was written in the sign-in's own 10 seconds or
    # later, with keys that the auditors' key fits.
    if [ "$state" = sealed ] && [[ ! $to < $when ]]; then
      echo sealed
      return
    fi
    # A file read while journald writes to it can fail once; a key that
    # doesn't fit fails every time.
    if [ "$state" = "failed:" ]; then
      failures=$((failures + 1))
      [ "$failures" -ge 3 ] && break
    fi
    sleep 2
  done
  echo "the key in $1 doesn't vouch for a sign-in made half a minute ago: $said"
}
