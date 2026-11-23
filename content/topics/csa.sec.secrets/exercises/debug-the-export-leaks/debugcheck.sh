# debugcheck.sh: the trial behind the checks of the export-leaks lab.
# A check starts with:   . /usr/local/lib/lab/debugcheck.sh
# and asks for one finding:   leak_finding args-clean
#
# The trial runs the export once, through its unit, and watches it the way
# an ordinary user could: the process list while it runs, the journal
# afterwards, the unit and every file that user can read. The gateway's
# own record says which key the run paid with; the trial then looks for
# that key, and asks the gateway about every key that has ever leaked.
# Nothing of the learner's is changed: the run charges the day's orders,
# as the timer's runs do.
#
# All six checks ask about one state of the machine, so the trial runs
# once for the six: its findings are kept for a minute in /run/lab-leaks,
# under a checksum of the unit, the job's settings and the gateway's keys.
. /usr/local/lib/lab/checklib-sec.sh

truth=/usr/local/lib/lab/debug
state=/var/lib/paygate
gateway=http://127.0.0.1:9440
findings=/run/lab-leaks

# note ASPECT TEXT: the trial's finding for one check; the first one said
# for an aspect is the one that counts.
note() {
  grep "^$1: " "$findings.new" > /dev/null 2>&1 || echo "$1: $2" >> "$findings.new"
}

all_aspects() {
  local aspect
  for aspect in job-works no-leaked-key-works args-clean journal-clean key-private; do
    note "$aspect" "$1"
  done
}

# works KEY: true when the gateway takes the key.
works() {
  [ "$(printf 'Authorization: Bearer %s' "$1" | curl -s -m 5 -o /dev/null -w '%{http_code}' -H @- "$gateway/whoami")" = 200 ]
}

# spellings VALUE: the value as it is, as base64 and as hex, one a line.
spellings() {
  printf '%s\n' "$1"
  printf '%s' "$1" | base64 -w 0
  echo
  printf '%s\n' "$1" | base64 -w 0
  echo
  printf '%s' "$1" | xxd -p -c 256
}

# keys_in: every gateway key in the text on standard input, one a line.
keys_in() {
  grep -a -o -E 'pg_live_[A-Za-z0-9]{32}' | sort -u
}

run_trial() {
  local work before after ids id key seen spelled found leaked value i since watcher started

  : > "$findings.new"
  chmod 600 "$findings.new"
  ready() { curl -s -m 3 -o /dev/null "$gateway/health"; }
  wait_for 10 ready || {
    all_aspects "the payment gateway isn't answering"
    return
  }
  [ "$(systemctl is-enabled shop-export.timer 2> /dev/null)" = enabled ] || {
    all_aspects "the export's timer won't start at the next boot"
    return
  }

  work=$(mktemp -d /var/tmp/leak-check.XXXXXX)
  # shellcheck disable=SC2064
  trap "rm -rf '$work'" EXIT

  # One run, watched. A run the timer started is let finish first. While
  # the run goes, the process list is read every fifth of a second. It is
  # read as root, who sees every command line there is: what an ordinary
  # user sees is part of that, unless /proc was remounted to hide other
  # users' processes, which lasts until the next boot and leaves the key
  # on the command line.
  idle() { [ "$(systemctl show shop-export -p ActiveState --value)" != activating ]; }
  for i in 1 2; do
    wait_for 20 idle
    before=$(wc -l < "$state/uses.log")
    since=$(date '+%Y-%m-%d %H:%M:%S')
    : > "$work/ps"
    (
      while sleep 0.2; do
        ps -eo user:20,args >> "$work/ps" 2> /dev/null
      done
    ) &
    watcher=$!
    systemctl start shop-export > /dev/null 2>&1
    started=$?
    kill "$watcher" 2> /dev/null
    wait "$watcher" 2> /dev/null
    after=$(tail -n "+$((before + 1))" "$state/uses.log")
    [ "$(echo "$after" | grep -c ' charge ok ')" -ge 3 ] && break
    [ "$started" = 0 ] || break
  done
  if [ "$started" != 0 ] || [ "$(echo "$after" | grep -c ' charge ok ')" -lt 3 ]; then
    all_aspects "the export, started through its unit, didn't charge the day's three orders"
    return
  fi
  ids=$(echo "$after" | awk '$3 == "charge" && $4 == "ok" {print $2}' | sort -u)
  [ "$(echo "$ids" | wc -l)" = 1 ] || {
    all_aspects "one run of the export paid with more than one key"
    return
  }
  id=$ids
  key=$(python3 -c 'import json, sys
for key in json.load(open(sys.argv[1])):
    if key["id"] == sys.argv[2]:
        print(key["key"])' "$state/keys.json" "$id")
  note job-works ok

  # Everything an ordinary user can see or read, gathered once.
  spelled=$(spellings "$key")
  {
    as_user audit journalctl --no-pager -o cat 2> /dev/null
  } > "$work/journal"
  {
    as_user audit systemctl show shop-export shop-export.timer 2> /dev/null
    as_user audit systemctl cat shop-export shop-export.timer 2> /dev/null
  } > "$work/unit"
  git -C /srv/git/shop.git log --all -p > "$work/history" 2> /dev/null

  # 1. No key that has leaked still works: the two the lab began with,
  # and any key that shows in the history, the journal, the process list
  # or the unit.
  leaked=$(
    {
      cat "$truth/keys"
      cat "$work/history" "$work/journal" "$work/unit" "$work/ps" | keys_in
    } | sort -u
  )
  found=""
  while IFS= read -r value; do
    [ -n "$value" ] || continue
    works "$value" && found=yes
  done <<< "$leaked"
  if [ -n "$found" ]; then
    note no-leaked-key-works "a key that has leaked still works at the gateway"
  else
    note no-leaked-key-works ok
  fi

  # 2. The process list during the run.
  if grep -F -f <(echo "$spelled") "$work/ps" > /dev/null || grep -a 'pg_live_' "$work/ps" > /dev/null; then
    note args-clean "while the export ran, a gateway key could be read by any user of the machine"
  else
    note args-clean ok
  fi

  # 3. The journal, as the ordinary user reads it: the run's own lines
  # are there, and the key isn't.
  seen=$(as_user audit journalctl --no-pager -o cat -u shop-export.service --since "$since" 2> /dev/null | grep -c 'INFO charged order')
  if [ "$seen" -lt 3 ]; then
    note journal-clean "an operator in the group adm can no longer read the export's lines in the journal"
  elif grep -F -f <(echo "$spelled") "$work/journal" > /dev/null; then
    note journal-clean "the journal shows the key the export pays with"
  else
    note journal-clean ok
  fi

  # 4. The unit, and every file the ordinary user can read.
  if grep -F -f <(echo "$spelled") "$work/unit" > /dev/null; then
    note key-private "systemd shows an ordinary user the key the export pays with"
  else
    # The spellings go to grep on its standard input (-f -), never as
    # arguments: a command that changes user is noted in the journal with
    # its whole command line, and the search would find itself there.
    found=$(as_user audit grep -rlF -f - /etc /home /srv /opt /tmp /var/tmp /var/lib /var/log /run /usr/local \
      2> /dev/null <<< "$spelled" | head -n 1)
    if [ -n "$found" ]; then
      note key-private "an ordinary user can read the key the export pays with, in $found"
    else
      note key-private ok
    fi
  fi
}

# leak_finding ASPECT: prints "ok", or what the trial found wrong.
leak_finding() {
  local sum now
  sum=$({
    systemctl cat shop-export 2> /dev/null
    cat /etc/shop/export.conf "$state/keys.json" 2> /dev/null
  } | sha256sum | cut -d' ' -f1)
  now=$(date +%s)
  if ! [ -s "$findings" ] \
    || [ "$(sed -n 's/^state: //p' "$findings")" != "$sum" ] \
    || [ $((now - $(sed -n 's/^at: //p' "$findings"))) -gt 60 ]; then
    (run_trial)
    {
      echo "state: $sum"
      echo "at: $now"
    } >> "$findings.new"
    mv "$findings.new" "$findings"
  fi
  sed -n "s/^$1: //p" "$findings"
}
